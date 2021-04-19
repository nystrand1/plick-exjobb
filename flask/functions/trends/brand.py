import logging
import redis
import json
from datetime import datetime

from ..utils.dataset import split_dataset
from ..regression.linear import get_linear_model
from ...models.brand_trend import BrandTrend

cache = redis.Redis(host='redis', port=6379)


def get_brand_candidates(db):
    CACHE_KEY = "_BRAND_CANDIDATES"
    if(cache.get(CACHE_KEY)):
        return json.loads(cache.get(CACHE_KEY))

    res = db.session.execute("""
        SELECT count(DISTINCT record.id) as count, brand.id, brand.name
        FROM plick.search_record_processed as record
        INNER JOIN plick.brands as brand on brand.id = ANY(record.brand_ids)
        WHERE record.created_at > '2021-04-18'::date - interval '7 day'
        GROUP BY brand.id
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
Returns the most popular categories within a brand
"""
def get_popular_categories_in_brands(db, brand_ids):
    res = db.session.execute("""
    SELECT count(DISTINCT record.id) as count, brand.name, brand.id, category.name
        FROM plick.search_record_processed as record
        INNER JOIN plick.brands as brand on brand.id = ANY(record.brand_ids)
        INNER JOIN plick.categories as category on category.id = ANY(record.category_ids)
        WHERE record.created_at > '2021-04-18'::date - interval '7 day'
        AND :brand_ids && record.brand_ids
        GROUP BY brand.name, brand.id, category.name
        ORDER BY count(DISTINCT record.id) DESC
        LIMIT 10
    """, {
        'brand_ids': brand_ids
    })

    res_arr = []
    for r in res:
        res_arr.append(dict(r))

    return res_arr

"""
Returns the most popular words searched for within a brand/s
"""
def get_popular_words_in_brands(db, brand_ids):
    res = db.session.execute("""
    SELECT count(DISTINCT record.id) as count, brand.name, query_processed as words, query
        FROM plick.search_record_processed as record
        INNER JOIN plick.brands as brand on brand.id = ANY(record.brand_ids)
        WHERE record.created_at > '2021-04-18'::date - interval '7 day'
        AND :brand_ids && record.brand_ids
        AND query_processed is not null
        GROUP BY brand.name, record.query_processed, query
        HAVING count(DISTINCT record.id) > 150
        ORDER BY count(DISTINCT record.id) DESC
    """, {
        'brand_ids': brand_ids
    })

    res_arr = []
    for r in res:
        res_arr.append(dict(r))

    return res_arr

def get_trending_brands(db, limit=5, k_threshold=0.5):
    res = db.session.execute("""
    SELECT brand_name, 
    brand_id,
    model_long,
    model_short,
    model_short[1] as k_short,
    model_long[1] as k_long,
    ABS(model_short[1]/model_long[1])*100 as k_val_diff_percent,
    model_short[1]-model_long[1] as k_val_diff,
    (plick.weekly_count_diff(time_series_day))[1] - (plick.weekly_count_diff(time_series_day))[2] as weekly_diff,
    (plick.weekly_count_diff(time_series_day))[3] * 100 - 100 as weekly_diff_percentage,
    (plick.monthly_count_diff(time_series_day))[1] - (plick.monthly_count_diff(time_series_day))[2] as monthly_diff,
    (plick.monthly_count_diff(time_series_day))[3] * 100 - 100 as monthly_diff_percentage
    FROM plick.brand_trends
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
        data = dict()
        data['brand_id'] = r['brand_id']
        data['brand_name'] = r['brand_name']
        data['model_long'] = r['model_long']
        data['model_short'] = r['model_short']
        data['weekly_diff'] = int(r['weekly_diff'])
        data['weekly_diff_percentage'] = float(r['weekly_diff_percentage'])
        data['monthly_diff'] = int(r['monthly_diff'])
        data['monthly_diff_percentage'] = float(r['monthly_diff_percentage'])
        res_arr.append(data)
    return res_arr 

def get_brand_dataset(db, brand_id): 
    res = db.session.execute("""
        SELECT *
        FROM plick.brand_trends
        WHERE brand_id = :brand_id
    """, {
        'brand_id': brand_id
    })
    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    res_arr.reverse()
    return res_arr[0]

def generate_brand_datasets(db):
    CACHE_KEY = "_BRANDS"
    if(cache.get(CACHE_KEY)):
        brands = json.loads(cache.get(CACHE_KEY))
    else: 
        brands = get_brand_candidates(db)
        cache.set(CACHE_KEY, json.dumps(brands), 300)
    [generate_brand_dataset(db, brand) for brand in brands] 
    return "success"

def generate_brand_dataset(db, brand):
    data = dict()
    data['start_date'] = "2021-01-01"
    data['end_date'] = "2021-04-18"
    data['brand_id'] = brand['id']
    data['trunc_by'] = "minute"
    generate_brand_time_series(db, brand['id'])
    time_series_min = get_brand_time_series_overlapping(db, **data)
    data['trunc_by'] = "hour"
    time_series_hour = get_brand_time_series_overlapping(db, **data)
    data['trunc_by'] = "day"
    time_series_day = get_brand_time_series_overlapping(db, **data)
    data['trunc_by'] = "week"
    time_series_week = get_brand_time_series_overlapping(db, **data)
    data['trunc_by'] = "month"
    time_series_month = get_brand_time_series_overlapping(db, **data)
    datasets = split_dataset(time_series_day)
    linear_model_long = get_linear_model(datasets['long'])
    linear_model_mid = get_linear_model(datasets['mid'])
    linear_model_short = get_linear_model(datasets['short'])
    logging.debug("LONG MODEL: {}".format(linear_model_long))
    logging.debug("MID MODEL: {}".format(linear_model_mid))
    logging.debug("SHORT MODEL: {}".format(linear_model_short))
    data_store = {
        'brand_id': brand['id'],
        'brand_name': brand['name'],
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

    logging.debug("STORING BRAND {} TREND DATA".format(brand['name']))
    save_to_db(db, data_store)
    return "success"

def generate_brand_time_series(db, brand_id=11):
    res = db.session.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS plick.brand_{} AS
        SELECT count(distinct coalesce(user_id, 0)) as amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from record.created_at) / (60*15)) * (60*15) as time_interval
        FROM plick.search_record_processed as record
		INNER JOIN plick.categories as cat on cat.id = ANY(record.brand_ids)
        WHERE record.brand_ids && ARRAY[:brand_id]
		AND
        record.created_at BETWEEN '2021-01-01'::date AND '2021-04-18'::date + interval '1 day'
        GROUP BY floor(extract('epoch' from record.created_at) / (60*15));

        CREATE UNIQUE INDEX IF NOT EXISTS time_series_interval_brand_{}
        ON plick.brand_{} (time_interval);
    """.format(brand_id, brand_id, brand_id), {
        'brand_id': brand_id
    })

def get_brand_time_series_overlapping(db, start_date="2021-01-01", end_date="2021-04-18", trunc_by="day", brand_id=10):
    
    CACHE_KEY = "_BRAND_TIME_SERIES_OVERLAPPING_{}_{}".format(brand_id, trunc_by)

    if(cache.get(CACHE_KEY)):
        logging.debug("Getting brand id {} {} trend from cache".format(brand_id, trunc_by))
        return json.loads(cache.get(CACHE_KEY))

    """
    Gets time series when brand_ids array have atleast 1 overlapping id. 
    Consider multiple options here like chosen brands should be
    a subset(combined), or exactly the same.
    """
    res = db.session.execute("""
        SELECT to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval, sum(coalesce(brands.amount,0)) as count from 
        (SELECT *
        FROM plick.brand_{}
		) brands
		RIGHT JOIN 
        (
        SELECT generate_series(date_trunc('minute',(:start_date)::date),
        date_trunc('minute', (:end_date)::date + time '23:59:59'),'15 min'::interval) as time_interval
        ) series
        on series.time_interval = brands.time_interval
		GROUP BY date_trunc(:trunc_by,series.time_interval)
        ORDER BY
       	time_interval ASC
        """.format(brand_id), {
        'brand_id': brand_id,
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
    BrandTrend().create()

    record = db.session.query(BrandTrend).get(data['brand_id'])
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
        record = BrandTrend(**data)
        db.session.add(record)
    db.session.commit()