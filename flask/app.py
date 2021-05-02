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
from http import HTTPStatus

import matplotlib.pyplot as plt

from darts import TimeSeries
from darts.models import AutoARIMA
from darts.models import TCNModel

from .models.search_record import SearchRecord
from .models.brand_trend import *
from .models.query_trend import *
from .models.category_trend import *

from .functions.trends.brand import *
from .functions.trends.category import *
from .functions.trends.query import *

from .functions.count_interval import *
from .functions.regression.linear import *
from .functions.regression.sarima import *
from .functions.regression.lstm import *
from .functions.regression.tcn import *
from .functions.utils.dataset import *
from .functions.process_queries import *
from .functions.utils.plick import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
cache = redis.Redis(host='redis', port=6379)
db = sa(app)

CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@app.route('/get-brand-timeseries', methods=['POST'])
@cross_origin()
def get_brand_timeseries():
    data = request.json
    brand_ids = data['brand_ids']
    trunc_by = data['resolution']
    res = get_formatted_brand_time_series(db, brand_ids=brand_ids, trunc_by=trunc_by)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/get-query-timeseries', methods=['POST'])
@cross_origin()
def get_query_timeseries():
    data = request.json
    query_ids = data['queries']
    trunc_by = data['resolution']
    res = get_formatted_query_time_series(db, query_ids=query_ids, trunc_by=trunc_by)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/get-category-timeseries', methods=['POST'])
@cross_origin()
def get_category_timeseries():
    data = request.json
    category_ids = data['category_ids']
    trunc_by = data['resolution']
    res = get_formatted_category_time_series(db, category_ids=category_ids, trunc_by=trunc_by)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

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

@app.route('/generate-tcn-models', methods=['GET'])
@cross_origin()
def generate_tcn_models():
    logging.debug("GENERATING QUERY TCN MODELS")
    generate_query_tcn_models(db, regenerate=False)
    logging.debug("GENERATING CATEGORY TCN MODELS")
    generate_category_tcn_models(db, regenerate=False)
    logging.debug("GENERATING BRAND TCN MODELS")
    generate_brand_tcn_models(db, regenerate=False)
    return Response(json.dumps("success"), status=HTTPStatus.OK, content_type="application/json")

@app.route('/generate-lstm-models', methods=['GET'])
@cross_origin()
def generate_lstm_models():
    logging.debug("GENERATING QUERY LSTM MODELS")
    generate_query_lstm_models(db, regenerate=False)
    logging.debug("GENERATING CATEGORY LSTM MODELS")
    generate_category_lstm_models(db, regenerate=False)
    logging.debug("GENERATING BRAND LSTM MODELS")
    generate_brand_lstm_models(db, regenerate=False)
    return Response(json.dumps("success"), status=HTTPStatus.OK, content_type="application/json")

@app.route('/generate-sarima-models', methods=['GET'])
@cross_origin()
def generate_sarima_models():
    logging.debug("GENERATING QUERY SAIMRA MODELS")
    generate_query_sarima_models(db, regenerate=False)
    logging.debug("GENERATING CATEGORY SAIMRA MODELS")
    generate_category_sarima_models(db, regenerate=False)
    logging.debug("GENERATING BRAND SARIMA MODELS")
    generate_brand_sarima_models(db, regenerate=False)
    return Response(json.dumps("success"), status=HTTPStatus.OK, content_type="application/json")

@app.route('/generate-models', methods=['GET'])
@cross_origin()
def generate_models():
    generate_tcn_models()
    generate_lstm_models()
    generate_sarima_models()
    return Response(json.dumps("success"), status=HTTPStatus.OK, content_type="application/json")

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

@app.route('/eval-sarima', methods=['GET'])
@cross_origin()
def eval_sarima():
    brands = get_all_brand_datasets(db)
    categories = get_all_category_datasets(db)
    queries = get_all_query_datasets(db)
    scores = eval_all_sarima_models(db, categories, brands, queries, regenerate=True)
    return Response(json.dumps(scores), status=HTTPStatus.OK, content_type="application/json")


@app.route('/eval-lstm', methods=['GET'])
@cross_origin()
def eval_lstm():
    brands = get_all_brand_datasets(db)
    categories = get_all_category_datasets(db)
    queries = get_all_query_datasets(db)
    
    scores = eval_all_lstm_models(db, categories, brands, queries, regenerate=True)
    
    return Response(json.dumps(scores), status=HTTPStatus.OK, content_type="application/json")


@app.route('/eval-tcn', methods=['GET'])
@cross_origin()
def eval_tcn():
    brands = get_all_brand_datasets(db)
    categories = get_all_category_datasets(db)
    queries = get_all_query_datasets(db)
    
    scores = eval_all_tcn_models(db, categories, brands, queries, regenerate=True)
    
    return Response(json.dumps(scores), status=HTTPStatus.OK, content_type="application/json")

@app.route('/darts-test', methods=['GET'])
@cross_origin()
def darts_test():
    dataset = get_category_dataset(db, 6)
    logging.debug(dataset['time_series_day'])
    dataset = dataset['time_series_day']
    test = pd.DataFrame.from_dict(dataset)
    test.to_csv('./functions/regression/jeans_day.csv')
    return Response(json.dumps(dataset), status=HTTPStatus.OK, content_type="application/json")

@app.route('/eval-brands', methods=['GET'])
@cross_origin()
def eval_brands():
    scores = get_brand_model_scores(db)
    return Response(json.dumps(scores), status=HTTPStatus.OK, content_type="application/json")

@app.route('/graphs', methods=['GET'])
@cross_origin()
def get_graphs():
    brands = get_all_brand_datasets(db)
    for brand in brands:
        dataset = brand['time_series_day']
        serialized_model_tcn = brand['model_tcn']
        serialized_model_lstm = brand['model_lstm']
        serialized_model_sarima = brand['model_sarima']
        name = brand['brand_name']
        get_tcn_backtest(serialized_model_tcn, dataset, name)
        get_lstm_backtest(serialized_model_lstm, dataset)
        get_sarima_backtest(serialized_model_sarima, dataset)
        plt.legend()
        plt.savefig("graphs/brands/{}.png".format(name))
        plt.clf()

    categories = get_all_category_datasets(db)
    for category in categories:
        dataset = category['time_series_day']
        serialized_model_tcn = category['model_tcn']
        serialized_model_lstm = category['model_lstm']
        serialized_model_sarima = category['model_sarima']
        name = category['category_name']
        get_tcn_backtest(serialized_model_tcn, dataset, name)
        get_lstm_backtest(serialized_model_lstm, dataset)
        get_sarima_backtest(serialized_model_sarima, dataset)
        plt.legend()
        plt.savefig("graphs/categories/{}.png".format(name))
        plt.clf()

    queries = get_all_query_datasets(db)
    for query in queries:
        dataset = query['time_series_day']
        serialized_model_tcn = query['model_tcn']
        serialized_model_lstm = query['model_lstm']
        serialized_model_sarima = query['model_sarima']
        name = "Query: '{}'".format(query['query'])
        get_tcn_backtest(serialized_model_tcn, dataset, name)
        get_lstm_backtest(serialized_model_lstm, dataset)
        get_sarima_backtest(serialized_model_sarima, dataset)
        plt.legend()
        plt.savefig("graphs/queries/{}.png".format(query['query']))
        plt.clf()

    return "success"

@app.route('/future', methods=['GET'])
@cross_origin()
def future():
    brands = get_all_brand_datasets(db)
    categories = get_all_category_datasets(db)
    queries = get_all_query_datasets(db)

    for brand in brands:
        dataset = brand['tcn_prediction']
        future_model = get_linear_model(dataset)
        save_future_model(db, future_model, "brand", brand['brand_id'])

    for category in categories:
        dataset = category['tcn_prediction']
        future_model = get_linear_model(dataset)
        save_future_model(db, future_model, "category", category['category_id'])

    for query in queries:
        dataset = query['tcn_prediction']
        future_model = get_linear_model(dataset)
        save_future_model(db, future_model, "query", query['query'])

    return Response(json.dumps("success"), status=HTTPStatus.OK, content_type="application/json")
