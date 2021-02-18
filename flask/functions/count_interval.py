import logging

def count_interval_grouped(db, query="nike", interval_mins=60, start_date="2020-12-30", end_date="2020-12-31"):
    res = db.session.execute("""
        SELECT query, to_char(series.time_interval, :date_format) as time_interval, coalesce(count.amount,0) as count from 
        (SELECT :query as query, count(query) amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (:mins *60)) * (:mins *60) as time_interval
        FROM search_records.search_record  
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
        r = dict(r.items())
        r['start_date'] = start_date
        r['end_date'] = end_date
        r['trends'] = dict()
        res_arr.append(r)
    res_arr.reverse()
    return res_arr


def count_interval_individual(db, query="nike", interval_mins=60, start_date="2020-12-30", end_date="2020-12-31"):
    res = db.session.execute("""
        SELECT query, to_char(series.time_interval, 'YYYY-MM-DD HH24:MI:SS') as time_interval, coalesce(count.amount,0) as count from 
        (SELECT query, count(query) amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * floor(extract('epoch' from created_at) / (:mins *60)) * (:mins *60) as time_interval
        FROM search_records.search_record  
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
        r = dict(r.items())
        res_arr.append(r)
    res_arr.reverse()
    return res_arr
