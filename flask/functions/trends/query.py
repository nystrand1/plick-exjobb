import logging
import redis
import json
import pickle
from datetime import datetime

from ..utils.dataset import split_dataset
from ..regression.linear import get_linear_model, generate_linear_series_from_model
from ...models.query_trend import QueryTrend
from ..regression.tcn import *
cache = redis.Redis(host='redis', port=6379)

def get_query_candidates(db, seperate_query_categories = False):
    if(seperate_query_categories):
        res = db.session.execute("""
        SELECT query_processed, count(record.query_processed) as amount, cat.name as category, query.name as query
        FROM plick.search_record_processed as record
        LEFT JOIN plick.categories as cat on cat.id = ANY(record.category_ids)
        LEFT JOIN plick.querys as query on query.id = ANY(record.query_ids)
        WHERE LENGTH(query_processed) > 1
        AND
        record.created_at > '2021-04-18'::date - interval '7 day'
        GROUP BY query_processed, cat.name, query.name
        HAVING count(query_processed) > 100
        ORDER BY amount DESC
        """)
    else:    
        res = db.session.execute("""
        SELECT query_processed, count(query_processed) as amount
        FROM plick.search_record_processed
        WHERE LENGTH(query_processed) > 1
        AND
        created_at > '2021-04-18'::date - interval '7 day'
        GROUP BY query_processed
        HAVING count(query_processed) > 300
        ORDER BY amount DESC
        LIMIT 50
        """)

    res_arr = []

    for r in res:
        res_arr.append(dict(r))
    
    return res_arr

def get_similar_words(db, query, similarity_threshold = 0.59):
    CACHE_KEY = "_SIMQUERY:{}_SIMTHRESHOLD:{}".format(query, similarity_threshold)
    
    if (cache.get(CACHE_KEY)):
        logging.debug("GETTING SIMILAR WORDS FROM CACHE")
        return json.loads(cache.get(CACHE_KEY))
        
    res = db.session.execute("""
    SET work_mem='12MB';
    SET pg_trgm.similarity_threshold = :threshold;
    SET pg_trgm.word_similarity_threshold = :threshold;
    SET pg_trgm.strict_word_similarity_threshold = :threshold;
    SELECT query_processed, similarity(query_processed, :query) as sim,
    word_similarity(query_processed, :query) as word_sim,
    strict_word_similarity(query_processed, :query) as strict_word_sim,
    count(query_processed) as amount
    FROM plick.search_record_processed
    WHERE 
    :query % query_processed
    AND
    :query %> query_processed
    AND
    :query %>> query_processed
    GROUP BY query_processed
    HAVING count(query_processed) > 100
    ORDER BY sim DESC
    """, {
        'query': query,
        'threshold': similarity_threshold,
    })

    res_arr = []

    for r in res:
        res_arr.append(r['query_processed'])

    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr

def get_trending_words(db, limit=5, k_threshold=0):
    res = db.session.execute("""
    SELECT query, similar_queries, model_short, model_long,
    model_short[1] as k_short,
    model_long[1] as k_long,
    ABS(model_short[1]/model_long[1])*100 as k_val_diff_percent,
    model_short[1]-model_long[1] as k_val_diff,
    (plick.weekly_count_diff(time_series_day))[1] - (plick.weekly_count_diff(time_series_day))[2] as weekly_diff,
    (plick.weekly_count_diff(time_series_day))[3] * 100 - 100 as weekly_diff_percentage,
    (plick.monthly_count_diff(time_series_day))[1] - (plick.monthly_count_diff(time_series_day))[2] as monthly_diff,
    (plick.monthly_count_diff(time_series_day))[3] * 100 - 100 as monthly_diff_percentage
    FROM plick.query_trends
    WHERE model_short[1] + :threshold > model_long[1]
    AND model_short[1] > 1
    ORDER BY model_short[1] DESC
    LIMIT :limit
    """, {
        'limit': limit,
        'threshold': k_threshold
    })

    res_arr = []

    for r in res:
        tmp = dict()
        tmp['query'] = r['query']
        tmp['similar_queries'] = r['similar_queries']
        tmp['model_short'] = r['model_short']
        tmp['model_long'] = r['model_long']
        tmp['weekly_diff'] = int(r['weekly_diff'])
        tmp['weekly_diff_percentage'] = float(r['weekly_diff_percentage'])
        tmp['monthly_diff'] = int(r['monthly_diff'])
        tmp['monthly_diff_percentage'] = float(r['monthly_diff_percentage'])
        res_arr.append(tmp)
    return res_arr 

def generate_query_tcn_models(db, regenerate = False):
    param_dict = dict()
    datasets = get_all_query_datasets(db)
    for dataset in datasets:
        ts = dataset['time_series_day']
        if(dataset['model_tcn'] is None or regenerate is True):
            model = get_tcn_model(dataset=ts)
            param_dict[dataset['query']] = model[1]
            model = model[0]
        else:
            model = pickle.loads(dataset['model_tcn'])
        predictions = get_tcn_predictions(model)
        store_tcn_model(db, pickle.dumps(model), trend_type="query", id=dataset['query'])
        store_tcn_prediction(db, prediction=predictions, trend_type="query", id=dataset['query'])

def generate_query_datasets(db):
    CACHE_KEY = "_QUERY_CANDIDATES"
    if(cache.get(CACHE_KEY)):
        queries = json.loads(cache.get(CACHE_KEY))
    else: 
        queries = get_query_candidates(db)
        cache.set(CACHE_KEY, json.dumps(queries), 300)

    data = dict()
    data['start_date'] = "2021-01-01"
    data['end_date'] = "2021-04-18"
    processed_queries = []
    [generate_query_dataset(db, data, query, processed_queries) for query in queries] 
    return "success"

def generate_query_dataset(db, data, r, processed_queries):
    data['query'] = r['query_processed']
    if data['query'] in processed_queries:
        logging.debug("WORD ALDREADY PROCESSED: {}".format(data['query']))
        return
    data['similar_queries'] = get_similar_words(db, data['query'])
    generate_query_time_series(db, data['query'], data['similar_queries'])
    logging.debug("SIMILAR WORDS: {}".format(data['similar_queries']))
    data['trunc_by'] = "minute"
    time_series_min = get_query_time_series(db, **data)
    data['trunc_by'] = "hour"
    time_series_hour = get_query_time_series(db, **data)
    data['trunc_by'] = "day"
    time_series_day = get_query_time_series(db, **data)
    data['trunc_by'] = "week"
    time_series_week = get_query_time_series(db, **data)
    data['trunc_by'] = "month"
    time_series_month = get_query_time_series(db, **data)
    datasets = split_dataset(time_series_day)
    linear_model_long = get_linear_model(datasets['long'])
    linear_model_mid = get_linear_model(datasets['mid'])
    linear_model_short = get_linear_model(datasets['short'])
    logging.debug("LONG MODEL: {}".format(linear_model_long))
    logging.debug("MID MODEL: {}".format(linear_model_mid))
    logging.debug("SHORT MODEL: {}".format(linear_model_short))
    processed_queries.extend(data['similar_queries'])
    try:
        data['similar_queries'].remove(data['query'])
    except:
        logging.debug("COULD NOT REMOVE: {}".format(data['query']))

    data_store = {
        'query': data['query'],
        'similar_queries': data['similar_queries'],
        'time_series_min': time_series_min,
        'time_series_hour': time_series_hour,
        'time_series_day': time_series_day,
        'time_series_week': time_series_week,
        'time_series_month': time_series_month,
        'model_short': linear_model_short,
        'model_mid': linear_model_mid,
        'model_long': linear_model_long,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }
    save_to_db(db, data_store)
    db.session.commit()

def generate_query_time_series(db, query="nike", similar_queries=[]):
    formatted_query = query.replace(" ", "_")
    formatted_query = formatted_query.replace("&", "_")
    formatted_query = formatted_query.replace("-", "_")
    res = db.session.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS plick.query_{} AS
        SELECT :query, count(distinct coalesce(user_id, 0)) as amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (60*15)) * (60*15) as time_interval
        FROM plick.search_record_processed 
        WHERE query_processed LIKE ANY(:similar_queries)
        GROUP BY floor(extract('epoch' from created_at) / (60*15));

        CREATE UNIQUE INDEX IF NOT EXISTS time_series_interval_query_{}
        ON plick.query_{} (time_interval);
    """.format(formatted_query, formatted_query, formatted_query), {
        'query': query,
        'similar_queries': similar_queries
    })

def get_query_dataset(db, query): 
    res = db.session.execute("""
        SELECT *
        FROM plick.query_trends
        WHERE query like :query
    """, {
        'query': query
    })
    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    res_arr.reverse()
    return res_arr

def get_all_query_datasets(db):
    res = db.session.execute("""
        SELECT query, model_tcn, model_lstm, model_sarima, time_series_day
        FROM plick.query_trends
    """)
    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    res_arr.reverse()

    return res_arr

def get_query_time_series(db, query="nike", trunc_by="hour", start_date="2021-01-25", end_date="2021-01-31", similar_queries=[]):
    CACHE_KEY = "_COUNTSIM:{}:FROM:{}:TO:{}:TRUNC_BY:{}".format(
        query, start_date, end_date, trunc_by)
    if (cache.get(CACHE_KEY)):
        logging.debug("GETTING INTERVAL FROM CACHE")
        return json.loads(cache.get(CACHE_KEY))
    formatted_query = query.replace(" ", "_")
    formatted_query = formatted_query.replace("&", "_")
    formatted_query = formatted_query.replace("-", "_")
    res = db.session.execute("""
        SELECT :query as query, to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval, sum(coalesce(count.amount,0)) as count from 
        (SELECT *
        FROM plick.query_{}
		) count
		RIGHT JOIN
        (
        SELECT generate_series(date_trunc('minute',(:start_date)::date),
        date_trunc('minute', (:end_date)::date + time '23:59:59'),'15 min'::interval) as time_interval
        ) series
        on series.time_interval = count.time_interval
		GROUP BY date_trunc(:trunc_by,series.time_interval)
        ORDER BY
       	time_interval ASC
        """.format(formatted_query), {
        'query': query,
        'trunc_by': trunc_by,
        'start_date': start_date,
        'end_date': end_date,
        'similar_queries': similar_queries
    })
    res_arr = []
    for r in res:
        data = dict()
        data['count'] = int(r['count'])
        data['trends'] = dict()
        data['time_interval'] = r['time_interval']
        res_arr.append(data)

    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr

def get_formatted_query_time_series(db, start_date="2021-01-01", end_date="2021-04-18", trunc_by="day", query_ids=["keps", "jeans", "klackskor"]):

    query_counts = ""
    query_joins = ""

    if(trunc_by == "day"):
        query_models = dict()
        query_tcn_predictions = dict()

    for query_id in query_ids:
        query_counts += ', sum(coalesce(query_{id}.amount,0))::int as query_{id}_count'.format(id=query_id)
        query_joins += 'LEFT JOIN plick.query_{id} AS query_{id} on query_{id}.time_interval = series.time_interval '.format(id=query_id)
        
        if(trunc_by == "day"):
            models = db.session.execute("""
            SELECT model_long, model_short, tcn_prediction
            FROM plick.query_trends
            WHERE query = :query_id
            """, {
                'query_id': query_id
            })
            for model in models:
                query_models[query_id] = model
                query_tcn_predictions[query_id] = model[2]

    res = db.session.execute("""
        SELECT to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval
        {query_counts}
        FROM (
        SELECT generate_series(date_trunc('minute', (:start_date)::date),
        date_trunc('minute', (:end_date)::date + time '23:59:59'),'15 min'::interval) as time_interval
        ) series
        {query_joins}
        GROUP BY date_trunc(:trunc_by,series.time_interval)
        ORDER BY
        time_interval ASC
        """.format(query_counts=query_counts, query_joins=query_joins), {
        'query_counts': query_counts,
        'query_joins': query_joins,
        'trunc_by': trunc_by,
        'start_date': start_date,
        'end_date': end_date,
    })

    res_arr = []
    if(trunc_by != "day"):
        for r in res:
            res_arr.append(dict(r))
    else:
        linear_datasets = dict()

        for query_id in query_ids:
            model = query_models[query_id]
            short = generate_linear_series_from_model(7, model[1]) #week
            long = generate_linear_series_from_model(res.rowcount, model[0])
            linear_datasets[query_id] = {
                'long': long,
                'short': short,
            }
            logging.debug(short)
            logging.debug(long)

        short_index = 0
        for i, r in enumerate(res):
            data = dict(r)
            for query_id in query_ids:
                data['trend_long_{}'.format(query_id)] = linear_datasets[query_id]['long'][i]
                if (i >= res.rowcount - 7):
                    logging.debug(short_index)
                    data['trend_short_{}'.format(query_id)] = linear_datasets[query_id]['short'][short_index]
                    data['tcn_pred_{}'.format(query_id)] = query_tcn_predictions[query_id][short_index]['count']
            
            if (i >= res.rowcount - 7):
                short_index += 1
            res_arr.append(dict(data))

    res_arr.reverse()
    return res_arr

def save_to_db(db, data):
    QueryTrend().create()
    record = db.session.query(QueryTrend).get(data['query'])
    if(record is not None):
        record.model_long = data['model_long']
        record.model_mid = data['model_mid']
        record.model_short = data['model_short']
        record.similar_queries = data['similar_queries']
        record.updated_at = data['updated_at']
    else:
        record = QueryTrend(**data)
        db.session.add(record)
    db.session.commit()