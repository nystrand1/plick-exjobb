def count_interval(db, query = "nike", interval_mins = 60, days_ago=7):
    res = db.session.execute("""
        SELECT query, to_char(series.minute, 'YYYY-MM-DD HH24:MI:SS') as interval, coalesce(count.amount,0) as count from 
        (
        SELECT :query as query, count(query) amount,
        TIMESTAMP WITH TIME ZONE 'epoch' +
        INTERVAL '1 second' * round(extract('epoch' from created_at) / (:mins * 60)) * (:mins * 60) as interval
        FROM search_records.search_record  
        WHERE query LIKE :query
        AND
        created_at >= '2021-02-02'::date - :days
        GROUP BY round(extract('epoch' from created_at) / (:mins * 60))
        ) count

        RIGHT JOIN 
        (
        SELECT generate_series(max(date_trunc('minute',created_at::date - :days)),
        max(date_trunc('minute', '2021-02-02'::date)),':mins m') as minute from search_records.search_record
        ) series
        on series.minute = count.interval
        ORDER BY
        interval DESC
        """, {
            'query': query,
            'mins': interval_mins,
            'days': days_ago ,
        })
    res_arr = []
    for r in res:
        r = dict(r.items())
        res_arr.append(r)
    res_arr.reverse()
    return res_arr