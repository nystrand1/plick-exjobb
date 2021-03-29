import logging
import redis
import json
cache = redis.Redis(host='redis', port=6379)

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