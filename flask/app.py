import time
import redis
import json
import datetime
from decouple import config
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy as sa
from flask_sqlalchemy import Model
from flask_cors import CORS, cross_origin

from .models.search_record import SearchRecord


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
cache = redis.Redis(host='redis', port=6379)
db = sa(app)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
@cross_origin()
def hello():
    res = db.session.query(SearchRecord).filter_by(query='nike').count()
    return 'Hello World! I have seen "nike" {} times.\n'.format(res)

@app.route('/count', methods=['POST'])
@cross_origin()
def count_query():
    data = request.json
    query = data['query']
    res = db.session.query(SearchRecord).filter(SearchRecord.query.contains(query)).count()
    return 'Hello World! I have seen messages like "{}" {} times.\n'.format(query, res)

@app.route('/count-interval', methods=['POST'])
@cross_origin()
def count_query_interval():
    data = request.json
    if 'query' not in data:
        return Response("Missing parameter 'query'", status=400)
    if 'interval_mins' not in data:
        return Response("Missing parameter 'interval_mins'", status=400)
    if 'days_ago' not in data:
        return Response("Missing parameter 'days_ago'", status=400)
    query = data['query']
    interval_mins = data['interval_mins']
    days_ago = data['days_ago']
    res = db.session.execute("""
        SELECT search_records.query, count(search_records.query) as count, 
        UNIX_TIMESTAMP(created_at) DIV (60 * :mins) as timekey
        FROM search_records
        WHERE
        search_records.query LIKE :query
        AND
        search_records.created_at >= now() - interval :days day
        GROUP BY
        timekey, :query
        ORDER BY
        timekey DESC
        """, {
            'query': query,
            'mins': interval_mins,
            'days': days_ago 
        })
    res_arr = []
    for r in res:
        r = dict(r.items())
        r['time'] = datetime.datetime.utcfromtimestamp(r['timekey']*60*interval_mins).strftime('%Y-%m-%d %H:%M:%S')
        res_arr.append(r)
    res_arr.reverse()
    return Response(json.dumps(res_arr), status=200, content_type="application/json")
    