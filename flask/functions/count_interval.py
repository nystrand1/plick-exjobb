import logging
import redis
import json
cache = redis.Redis(host='redis', port=6379)

"""
Count grouped occurrences, for example when query is 'nike%' it will count
'nike air' and 'nike shorts' as same data points
"""


def count_interval_grouped(db, query="nike", interval_mins=60, start_date="2021-01-14", end_date="2021-01-15"):
    res = db.session.execute("""
        SELECT query, to_char(series.time_interval, :date_format) as time_interval, coalesce(count.amount,0) as count from 
        (SELECT :query as query, count(query) amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (:mins *60)) * (:mins *60) as time_interval
        FROM plick.search_record  
        WHERE query LIKE :query
        AND
        created_at BETWEEN (:start_date)::date AND (:end_date)::date + interval '1 day'
        GROUP BY floor(extract('epoch' from created_at) / (:mins *60))
		) count
		RIGHT JOIN 
        (
        SELECT generate_series(date_trunc('minute',(:start_date)::date),
        date_trunc('minute', (:end_date)::date),':mins min'::interval) as time_interval
        ) series
        on series.time_interval = count.time_interval
        ORDER BY
        time_interval DESC
        """, {
        'query': query,
        'mins': interval_mins,
        'start_date': start_date,
        'end_date': end_date,
        'date_format': 'YYYY-MM-DD HH24:MI:SS' if interval_mins < 60*24 else 'YYYY-MM-DD'
    })
    res_arr = []
    for r in res:
        r['start_date'] = start_date
        r['end_date'] = end_date
        r['trends'] = dict()
        res_arr.append(r)
    res_arr.reverse()
    return res_arr


"""
Count indvidual occurrences, for example when query is 'nike%' it will count
'nike air' and 'nike shorts' as individual data points
"""


def count_interval_individual(db, query="nike", interval_mins=60, start_date="2020-12-30", end_date="2020-12-31"):
    res = db.session.execute("""
        SELECT query, to_char(series.time_interval, 'YYYY-MM-DD HH24:MI:SS') as time_interval, coalesce(count.amount,0) as count from 
        (SELECT query, count(query) amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (:mins *60)) * (:mins *60) as time_interval
        FROM plick.search_record  
        WHERE query LIKE :query
        AND
        created_at BETWEEN  (:start_date)::date AND (:end_date)::date
        GROUP BY floor(extract('epoch' from created_at) / (:mins *60)), query
		) count
		RIGHT JOIN 
        (
        SELECT generate_series(date_trunc('minute',(:start_date)::date),
        date_trunc('minute', (:end_date)::date ),':mins min'::interval) as time_interval
        ) series
        on series.time_interval = count.time_interval
        ORDER BY
        time_interval DESC
        """, {
        'query': query,
        'mins': interval_mins,
        'start_date': start_date,
        'end_date': end_date
    })
    res_arr = []
    for r in res:
        res_arr.append(r)
        r['trends'] = dict()
    res_arr.reverse()
    return res_arr


"""
Counts query occurences with an interval of 15 minute per user.
Example user 1337 searches for 'nike' 5 times in 10 minute. This
will be counted as 1 occurence in order to minimize the impact 
of the trend.
"""


def count_interval_unique(db, query="nike", trunc_by="hour", start_date="2021-01-25", end_date="2021-01-31"):
    res = db.session.execute("""
        SELECT :query as query, to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval, sum(coalesce(count.amount,0)) as count from 
        (SELECT :query as query, count(distinct coalesce(user_id, 0)) as amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (60*15)) * (60*15) as time_interval
        FROM plick.search_record  
        WHERE query LIKE :query
        AND
        created_at BETWEEN (:start_date)::date AND (:end_date)::date + interval '1 day'
        GROUP BY floor(extract('epoch' from created_at) / (60*15))
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
        'end_date': end_date
    })
    res_arr = []
    for r in res:
        r['count'] = int(r['count'])
        r['trends'] = dict()
        res_arr.append(r)
    res_arr.reverse()
    return res_arr


def count_interval_unique_similar(db, query="nike", trunc_by="hour", start_date="2021-01-25", end_date="2021-01-31", similar_queries=[]):
    CACHE_KEY = "_COUNTSIM:{}:FROM:{}:TO:{}:TRUNC_BY:{}".format(
        query, start_date, end_date, trunc_by)
    if (cache.get(CACHE_KEY)):
        logging.debug("GETTING INTERVAL FROM CACHE")
        return json.loads(cache.get(CACHE_KEY))

    res = db.session.execute("""
        SELECT :query as query, to_char(date_trunc(:trunc_by,series.time_interval), 'YYYY-MM-DD HH24:MI:SS') as time_interval, sum(coalesce(count.amount,0)) as count from 
        (SELECT query, count(distinct coalesce(user_id, 0)) as amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (60*15)) * (60*15) as time_interval
        FROM plick.search_record  
        WHERE query LIKE ANY(:similar_queries)
        AND
        created_at BETWEEN (:start_date)::date AND (:end_date)::date + interval '1 day'
        GROUP BY floor(extract('epoch' from created_at) / (60*15)), query
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
        #r['count'] = int(r['count'])
        #r['trends'] = dict()
        res_arr.append(tmp)
    res_arr.reverse()
    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr

def get_query_dataset(db, query): 
    res = db.session.execute("""
        SELECT *
        FROM plick.term_trends
        WHERE query like :query
    """, {
        'query': query
    })
    res_arr = []
    for r in res:
        res_arr.append(dict(r))
    res_arr.reverse()
    return res_arr[0]