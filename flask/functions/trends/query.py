import logging
import redis
import json
from datetime import datetime

from ..utils.dataset import split_dataset
from ..regression.linear import get_linear_model
from ...models.query_trend import QueryTrend
cache = redis.Redis(host='redis', port=6379)

def get_query_candidates(db, seperate_brand_categories = False):
    if(seperate_brand_categories):
        res = db.session.execute("""
        SELECT query_processed, count(record.query_processed) as amount, cat.name as category, brand.name as brand
        FROM plick.search_record_processed as record
        LEFT JOIN plick.categories as cat on cat.id = ANY(record.category_ids)
        LEFT JOIN plick.brands as brand on brand.id = ANY(record.brand_ids)
        WHERE LENGTH(query_processed) > 1
        AND
        record.created_at > '2021-03-15'::date - interval '7 day'
        GROUP BY query_processed, cat.name, brand.name
        HAVING count(query_processed) > 100
        ORDER BY amount DESC
        """)
    else:    
        res = db.session.execute("""
        SELECT query_processed, count(query_processed) as amount
        FROM plick.search_record_processed
        WHERE LENGTH(query_processed) > 1
        AND
        created_at > '2021-03-15'::date - interval '7 day'
        GROUP BY query_processed
        HAVING count(query_processed) > 300
        ORDER BY amount DESC
        """)

    res_arr = []

    for r in res:
        res_arr.append(dict(r))
    
    logging.debug(res_arr)
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

def generate_query_datasets(db):
    CACHE_KEY = "_QUERY_CANDIDATES"
    if(cache.get(CACHE_KEY)):
        queries = json.loads(cache.get(CACHE_KEY))
    else: 
        queries = get_query_candidates(db)
        cache.set(CACHE_KEY, json.dumps(queries), 300)

    data = dict()
    data['start_date'] = "2021-01-01"
    data['end_date'] = "2021-03-15"
    processed_queries = []
    [generate_query_dataset(db, data, query, processed_queries) for query in queries] 
    return "success"

def generate_query_dataset(db, data, r, processed_queries):
    logging.debug(processed_queries)
    data['query'] = r['query_processed']
    if data['query'] in processed_queries:
        logging.debug("WORD ALDREADY PROCESSED: {}".format(data['query']))
        return
    data['similar_queries'] = get_similar_words(db, data['query'])
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
    return res_arr[0]

def get_query_time_series(db, query="nike", trunc_by="hour", start_date="2021-01-25", end_date="2021-01-31", similar_queries=[]):
    CACHE_KEY = "_COUNTSIM:{}:FROM:{}:TO:{}:TRUNC_BY:{}".format(
        query, start_date, end_date, trunc_by)
    if (cache.get(CACHE_KEY)):
        logging.debug("GETTING INTERVAL FROM CACHE")
        return json.loads(cache.get(CACHE_KEY))

    res = db.session.execute("""
        SELECT :query as query, to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval, sum(coalesce(count.amount,0)) as count from 
        (SELECT query_processed, count(distinct coalesce(user_id, 0)) as amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (60*15)) * (60*15) as time_interval
        FROM plick.search_record_processed 
        WHERE query_processed LIKE ANY(:similar_queries)
        AND
        created_at BETWEEN (:start_date)::date AND (:end_date)::date + interval '1 day'
        GROUP BY floor(extract('epoch' from created_at) / (60*15)), query_processed
		) count
		RIGHT JOIN 
        (
        SELECT generate_series(date_trunc('minute',(:start_date)::date),
        date_trunc('minute', (:end_date)::date + time '23:59:59'),'15 min'::interval) as time_interval
        ) series
        on series.time_interval = count.time_interval
		GROUP BY date_trunc(:trunc_by,series.time_interval)
        ORDER BY
       	time_interval DESC
        """, {
        'query': query,
        'trunc_by': trunc_by,
        'start_date': start_date,
        'end_date': end_date,
        'similar_queries': similar_queries
    })
    res_arr = []
    for r in res:
        tmp = dict()
        tmp['count'] = int(r['count'])
        tmp['trends'] = dict()
        tmp['time_interval'] = r['time_interval']
        res_arr.append(tmp)
    res_arr.reverse()
    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
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