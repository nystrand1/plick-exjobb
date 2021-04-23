import time
import redis
import simplejson as json
import datetime
import logging
import sys
import pickle
from decouple import config
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy as sa
from flask_sqlalchemy import Model
from flask_cors import CORS, cross_origin
from flask_caching import Cache
from http import HTTPStatus

import multiprocessing
from joblib import Parallel
from joblib import delayed

from .models.search_record import SearchRecord
from .models.brand_trend import *
from .models.query_trend import *
from .models.category_trend import *

from .functions.trends.brand import *
from .functions.trends.category import *
from .functions.trends.query import *

from .functions.utils.sanitizer import *
from .functions.count_interval import *
from .functions.regression.linear import *
from .functions.regression.arma import handle_arma_regression
from .functions.regression.sarma import handle_sarma_regression
from .functions.regression.lstm import handle_lstm
from .functions.regression.auto_sarima import handle_auto_sarima_regression
from .functions.utils.dataset import *
from .functions.process_queries import *
from .functions.utils.plick import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
cache = redis.Redis(host='redis', port=6379)
db = sa(app)

CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@app.route('/linear-regression', methods=['POST'])
@cross_origin()
def linear_regression():
    inputs = LinearRegressionInputs(request)
    if not inputs.validate():
        return Response(json.dumps(inputs.errors), status=HTTPStatus.BAD_REQUEST, content_type="application/json")
    res = handle_linear_regression(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/arma-regression', methods=['POST'])
@cross_origin()
def arma_regression():
    return handle_arma_regression(db)

@app.route('/sarma-regression', methods=['POST'])
@cross_origin()
def sarma_regression():
    return handle_sarma_regression(db)

@app.route('/lstm', methods=['POST'])
@cross_origin()
def lstm():
    return handle_lstm(db)

@app.route('/auto-sarima', methods=['POST'])
@cross_origin()
def auto_arima():
    return handle_auto_sarima_regression(db)

@app.route('/query-candidates', methods=['GET'])
@cross_origin()
def query_candidates():
    res = generate_query_datasets(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/category-candidates', methods=['GET'])
@cross_origin()
def category_candidates():
    res = generate_category_datasets(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/brand-candidates', methods=['GET'])
@cross_origin()
def brand_candidates():
    res = generate_brand_datasets(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/generate-trend-data', methods=['GET'])
@cross_origin()
def generate_trend_data():
    logging.debug("GENERATING QUERY DATASETS")
    res = generate_query_datasets(db)
    logging.debug("GENERATING CATEGORY DATASETS")
    res = generate_category_datasets(db)
    logging.debug("GENERATING BRAND DATASETS")
    res = generate_brand_datasets(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/sarima-test', methods=['GET'])
@cross_origin()
def sarima_test():
    dataset = get_category_dataset(db, 12)
    logging.debug(dataset['time_series_hour'])
    dataset = dataset['time_series_hour']
    model = get_sarima_model(dataset)
    store_sarima_model(db, pickle.dumps(model))
    logging.debug(model.summary())
    return Response(json.dumps(dataset), status=HTTPStatus.OK, content_type="application/json")


@app.route('/trending-words', methods=['POST'])
@cross_origin()
def trending_words():
    data = request.json
    limit = data['limit']
    res = get_trending_words(db, limit)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/trending-categories', methods=['POST'])
@cross_origin()
def trending_categories():
    data = request.json
    limit = data['limit']
    res = get_trending_categories(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/trending-brands', methods=['POST'])
@cross_origin()
def trending_brands():
    data = request.json
    limit = data['limit']
    res = get_trending_brands(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/example-ads', methods=['POST'])
@cross_origin()
def get_example_ads():
    data = request.json
    query = data['query']
    limit = data['limit']
    res = get_ads(query, limit)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/query-dataset', methods=['POST'])
@cross_origin()
def query_dataset():
    data = request.json
    res = get_query_dataset(db, data['query'])
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/brand-dataset', methods=['POST'])
@cross_origin()
def brand_dataset():
    data = request.json
    res = get_brand_dataset(db, data['brand'])
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")