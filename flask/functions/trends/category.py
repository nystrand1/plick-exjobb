import logging
import redis
import json
from datetime import datetime

from ...models.category_trend import CategoryTrend
cache = redis.Redis(host='redis', port=6379)


def get_category_candidates(db):
    CACHE_KEY = "_CATEGORY_CANDIDATES"

    if(cache.get(CACHE_KEY)):
        return json.loads(cache.get(CACHE_KEY))

    res = db.session.execute("""
        SELECT count(DISTINCT record.id) as count, record.category_ids, ARRAY_AGG(DISTINCT cat.name) as names
        FROM plick.search_record_processed as record
        INNER JOIN plick.categories as cat on cat.id = ANY(record.category_ids)
        WHERE record.created_at > '2021-03-15'::date - interval '7 day'
        GROUP BY record.category_ids
        HAVING count(record.id) > 5000
        ORDER BY count(record.id) DESC
    """)

    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    
    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr

def get_category_dataset(db, category): 
    res = db.session.execute("""
        SELECT *
        FROM plick.category_trends
        WHERE category like :category
    """, {
        'category': category
    })
    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    res_arr.reverse()
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

def generate_category_dataset(db, category):
    logging.debug(category)
    data = dict()
    data['start_date'] = "2021-01-01"
    data['end_date'] = "2021-03-15"
    data['category_ids'] = category['category_ids']
    data['trunc_by'] = "minute"
    time_series_min = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "hour"
    time_series_hour = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "day"
    time_series_day = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "week"
    time_series_week = get_category_time_series_overlapping(db, **data)
    data['trunc_by'] = "month"
    time_series_month = get_category_time_series_overlapping(db, **data)

    data_store = {
        'category_ids': category['category_ids'],
        'category_names': category['names'],
        'time_series_min': time_series_min,
        'time_series_hour': time_series_hour,
        'time_series_day': time_series_day,
        'time_series_week': time_series_week,
        'time_series_month': time_series_month,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }

    logging.debug("STORING CATEGORY {} TREND DATA".format(category['names']))
    save_to_db(db, data_store)
    return "success"

def get_category_time_series_overlapping(db, start_date="2021-01-01", end_date="2021-03-15", trunc_by="day", category_ids=[10]):
    CACHE_KEY = "_CATEGORY_TIME_SERIES_OVERLAPPING_{}_{}".format(category_ids, trunc_by)

    if(cache.get(CACHE_KEY)):
        logging.debug("Getting category id {} {} trend from cache".format(category_ids, trunc_by))
        return json.loads(cache.get(CACHE_KEY))

    """
    Gets time series when category_ids array have atleast 1 overlapping id. 
    Consider multiple options here like chosen categorys should be
    a subset(combined), or exactly the same.
    """
    res = db.session.execute("""
        SELECT to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval, sum(coalesce(categories.amount,0)) as count from 
        (SELECT count(distinct coalesce(user_id, 0)) as amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from record.created_at) / (60*15)) * (60*15) as time_interval
        FROM plick.search_record_processed as record
		INNER JOIN plick.categories as cat on cat.id = ANY(:category_ids)
        WHERE record.category_ids && :category_ids
		AND
        record.created_at BETWEEN (:start_date)::date AND (:end_date)::date + interval '1 day'
        GROUP BY floor(extract('epoch' from record.created_at) / (60*15))
		) categories
		RIGHT JOIN 
        (
        SELECT generate_series(date_trunc('minute',(:start_date)::date),
        date_trunc('minute', (:end_date)::date + time '23:59:59'),'15 min'::interval) as time_interval
        ) series
        on series.time_interval = categories.time_interval
		GROUP BY date_trunc(:trunc_by,series.time_interval)
        ORDER BY
       	time_interval DESC
    """,{
        'category_ids': category_ids,
        'trunc_by': trunc_by,
        'start_date': start_date,
        'end_date': end_date,
    })

    res_arr = []
    for r in res:
        data = dict()
        data['count'] = int(r['count'])
        data['time_inteval'] = r['time_interval']
        res_arr.append(data)
    
    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr


def save_to_db(db, data):
    CategoryTrend().create()
    logging.debug(data['category_names'])
    record = db.session.query(CategoryTrend).filter_by(category_ids=data['category_ids']).first()
    if(record is not None):
        record.time_series_min = data['time_series_min'],
        record.time_series_hour = data['time_series_hour'],
        record.time_series_day = data['time_series_day'],
        record.time_series_week = data['time_series_week'],
        record.time_series_month = data['time_series_month'],
        # record.model_long = data['model_long']
        # record.model_mid = data['model_mid']
        # record.model_short = data['model_short']
        record.updated_at = data['updated_at']
    else:
        record = CategoryTrend(**data)
        db.session.add(record)
    db.session.commit()
