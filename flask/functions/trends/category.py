import logging
import redis
import json
import pickle
from datetime import datetime

from ..utils.dataset import split_dataset
from ..regression.linear import get_linear_model
from ..regression.auto_sarima import get_sarima_model
from ...models.category_trend import CategoryTrend
cache = redis.Redis(host='redis', port=6379)


def get_category_candidates(db):
    CACHE_KEY = "_CATEGORY_CANDIDATES"

    if(cache.get(CACHE_KEY)):
        return json.loads(cache.get(CACHE_KEY))

    res = db.session.execute("""
        SELECT count(DISTINCT record.id) as count, cat.id, cat.name
        FROM plick.search_record_processed as record
        INNER JOIN plick.categories as cat on cat.id = ANY(record.category_ids)
        WHERE record.created_at > '2021-03-15'::date - interval '7 day'
        GROUP BY cat.id, cat.name
        HAVING count(DISTINCT record.id) > 1000
        ORDER BY count(DISTINCT record.id) DESC
        LIMIT 50
    """)

    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    
    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr

"""
Returns the most popular words searched for within a category/s
"""
def get_popular_words_in_categorys(db, category_ids):
    res = db.session.execute("""
    SELECT count(DISTINCT record.id) as count, category.name, query_processed as words, query
        FROM plick.search_record_processed as record
        INNER JOIN plick.categories as category on category.id = ANY(record.category_ids)
        WHERE record.created_at > '2021-03-15'::date - interval '7 day'
        AND :category_ids && record.category_ids
        AND query_processed is not null
        GROUP BY category.name, record.query_processed, query
        HAVING count(DISTINCT record.id) > 150
        ORDER BY count(DISTINCT record.id) DESC
    """, {
        'category_ids': category_ids
    })

    res_arr = []
    for r in res:
        res_arr.append(dict(r))

    return res_arr

def get_category_dataset(db, category_id): 
    res = db.session.execute("""
        SELECT *
        FROM plick.category_trends
        WHERE category_id = :category_id
    """, {
        'category_id': category_id
    })
    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    return res_arr[0]


def generate_category_datasets(db):
    CACHE_KEY = "_CATEGORIES"
    if(cache.get(CACHE_KEY)):
        categories = json.loads(cache.get(CACHE_KEY))
    else: 
        categories = get_category_candidates(db)
        cache.set(CACHE_KEY, json.dumps(categories), 300)
    [generate_category_dataset(db, category) for category in categories] 
    return "success"

def generate_category_dataset(db, category, calcualate_sarima = False):
    logging.debug(category)
    data = dict()
    data['start_date'] = "2021-01-01"
    data['end_date'] = "2021-03-15"
    data['category_id'] = category['id']
    data['trunc_by'] = "minute"
    generate_category_time_series(db, category['id'])
    time_series_min = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "hour"
    time_series_hour = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "day"
    time_series_day = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "week"
    time_series_week = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "month"
    time_series_month = get_category_time_series_overlapping(db, **data)
    datasets = split_dataset(time_series_day)
    linear_model_long = get_linear_model(datasets['long'])
    linear_model_mid = get_linear_model(datasets['mid'])
    linear_model_short = get_linear_model(datasets['short'])
    logging.debug("LONG MODEL: {}".format(linear_model_long))
    logging.debug("MID MODEL: {}".format(linear_model_mid))
    logging.debug("SHORT MODEL: {}".format(linear_model_short))
    data_store = {
        'category_id': category['id'],
        'category_name': category['name'],
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
    if(calcualate_sarima):
        sarima_model = get_sarima_model(time_series_hour)
        data_store['model_sarima'] = pickle.dumps(sarima_model)

    logging.debug("STORING CATEGORY '{}' TREND DATA".format(category['name']))
    save_to_db(db, data_store)
    return "success"

def generate_category_time_series(db, category_id=11):
    res = db.session.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS plick.category_{} AS
        SELECT count(distinct coalesce(user_id, 0)) as amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from record.created_at) / (60*15)) * (60*15) as time_interval
        FROM plick.search_record_processed as record
		INNER JOIN plick.categories as cat on cat.id = ANY(record.category_ids)
        WHERE record.category_ids && ARRAY[:category_id]
        GROUP BY floor(extract('epoch' from record.created_at) / (60*15));

        CREATE UNIQUE INDEX IF NOT EXISTS time_series_interval_category_{}
        ON plick.category_{} (time_interval);
    """.format(category_id, category_id, category_id), {
        'category_id': category_id
    })

def get_category_time_series_overlapping(db, start_date="2021-01-01", end_date="2021-03-15", trunc_by="day", category_id=11):
    CACHE_KEY = "_CATEGORY_TIME_SERIES_OVERLAPPING_{}_{}".format(category_id, trunc_by)

    if(cache.get(CACHE_KEY)):
        logging.debug("Getting category id {} {} trend from cache".format(category_id, trunc_by))
        return json.loads(cache.get(CACHE_KEY))

    """
    Gets time series when category_ids array have atleast 1 overlapping id. 
    Consider multiple options here like chosen categorys should be
    a subset(combined), or exactly the same.
    """
    res = db.session.execute("""
        SELECT to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval, sum(coalesce(categories.amount,0)) as count from 
        (SELECT *
        FROM plick.category_{}
		) categories
		RIGHT JOIN 
        (
        SELECT generate_series(date_trunc('minute',(:start_date)::date),
        date_trunc('minute', (:end_date)::date + time '23:59:59'),'15 min'::interval) as time_interval
        ) series
        on series.time_interval = categories.time_interval
		GROUP BY date_trunc(:trunc_by,series.time_interval)
        ORDER BY
       	time_interval ASC
    """.format(category_id),{
        'category_id': category_id,
        'trunc_by': trunc_by,
        'start_date': start_date,
        'end_date': end_date,
    })

    res_arr = []
    for r in res:
        data = dict()
        data['count'] = int(r['count'])
        data['time_interval'] = r['time_interval']
        res_arr.append(data)

    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr


def save_to_db(db, data):
    CategoryTrend().create()
    logging.debug(data['category_name'])
    record = db.session.query(CategoryTrend).filter_by(category_id=data['category_id']).first()
    if(record is not None):
        record.time_series_min = data['time_series_min'],
        record.time_series_hour = data['time_series_hour'],
        record.time_series_day = data['time_series_day'],
        record.time_series_week = data['time_series_week'],
        record.time_series_month = data['time_series_month'],
        record.model_long = data['model_long']
        record.model_mid = data['model_mid']
        record.model_short = data['model_short']
        record.updated_at = data['updated_at']
    else:
        record = CategoryTrend(**data)
        db.session.add(record)
    db.session.commit()

def store_sarima_model(db, serialized_model):
    record = db.session.query(CategoryTrend).filter_by(category_id=11).first()
    if(record is not None):
        record.model_sarima = serialized_model
    else:
        logging.debug("what")
    db.session.commit()
