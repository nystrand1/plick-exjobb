import time
import redis
import json
import datetime
import logging
import sys
from decouple import config
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy as sa
from flask_sqlalchemy import Model
from flask_cors import CORS, cross_origin

from .models.search_record import SearchRecord
from .functions.count_interval import count_interval_grouped, count_interval_individual
from .functions.regression.linear import get_linear_model
from .functions.utils.generator import generate_series_from_model
from .functions.utils.merge import merge_datasets


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
cache = redis.Redis(host='redis', port=6379)
db = sa(app)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


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
    res = db.session.query(SearchRecord).filter(
        SearchRecord.query.contains(query)).count()
    return 'Hello World! I have seen messages like "{}" {} times.\n'.format(query, res)


@app.route('/count-interval-grouped', methods=['POST'])
@cross_origin()
def count_query_interval_grouped():
    data = request.json
    if 'query' not in data:
        return Response("Missing parameter 'query'", status=400)
    if 'interval_mins' not in data:
        return Response("Missing parameter 'interval_mins'", status=400)

    query = data['query']
    interval_mins = data['interval_mins']
    start_date = data['start_date']
    end_date = data['end_date']
    res = count_interval_grouped(
        db, query, interval_mins, start_date, end_date)
    return Response(json.dumps(res, indent=4, sort_keys=True, default=str), status=200, content_type="application/json")


@app.route('/count-interval-individual', methods=['POST'])
@cross_origin()
def count_query_interval_individual():
    data = request.json
    if 'query' not in data:
        return Response("Missing parameter 'query'", status=400)
    if 'interval_mins' not in data:
        return Response("Missing parameter 'interval_mins'", status=400)

    query = data['query']
    interval_mins = data['interval_mins']
    start_date = data['start_date']
    end_date = data['end_date']
    res = count_interval_individual(
        db, query, interval_mins, start_date, end_date)
    return Response(json.dumps(res, indent=4, sort_keys=True, default=str), status=200, content_type="application/json")


@app.route('/linear-regression', methods=['POST'])
@cross_origin()
def linear_regression():
    data = request.json
    if 'query' not in data:
        return Response("Missing parameter 'query'", status=400)
    if 'interval_mins' not in data:
        return Response("Missing parameter 'interval_mins'", status=400)

    query = data['query']
    interval_mins = data['interval_mins']
    start_date = data['start_date']
    end_date = data['end_date']
    if start_date == end_date:
        logging.debug("SAME DATE")
        logging.debug(end_date)
    
    dataset = count_interval_grouped(
        db, query, interval_mins, start_date, end_date)

    if len(dataset) > 1:
        for n in range(9, 10):
            linear_model = get_linear_model(dataset, n)
            time_series = generate_series_from_model(len(dataset), linear_model)
            dataset = merge_datasets(dataset, time_series, key_name="degree {}".format(n))
    logging.debug(dataset)
    return Response(json.dumps(dataset), status=200, content_type="application/json")
