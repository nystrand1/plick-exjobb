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

import multiprocessing
from joblib import Parallel
from joblib import delayed

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

#from .functions.utils.sanitizer import *
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

@app.route('/tcn-test', methods=['GET'])
@cross_origin()
def tcn_test():
    dataset = get_category_dataset(db, 12)
    logging.debug(dataset['time_series_day'])
    dataset = dataset['time_series_day']
    model = get_tcn_model(dataset=dataset)
    predictions = get_tcn_predictions(model)
    store_tcn_model(db, pickle.dumps(model), trend_type="category", id=12)
    store_tcn_prediction(db, prediction=predictions)
    return Response(json.dumps(dataset), status=HTTPStatus.OK, content_type="application/json")


@app.route('/trending-words', methods=['POST'])
@cross_origin()
def trending_words():
    data = request.json
    logging.debug(request)
    limit = data['limit']
    res = get_trending_words(db, limit)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/trending-categories', methods=['POST'])
@cross_origin()
def trending_categories():
    res = get_trending_categories(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/trending-brands', methods=['POST'])
@cross_origin()
def trending_brands():
    res = get_trending_brands(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/trending-ads', methods=['POST'])
@cross_origin()
def get_trending_ads():
    res = get_ads("nike")
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/query-dataset', methods=['POST'])
@cross_origin()
def query_dataset():
    data = request.json
    res = get_query_dataset(db, data['query'])
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")

@app.route('/darts-test', methods=['GET'])
@cross_origin()
def darts_test():
    dataset = get_brand_dataset(db, 11)
    logging.debug(dataset['time_series_hour'])
    dataset = dataset['time_series_day']
    test = pd.DataFrame.from_dict(dataset)
    test.to_csv('./functions/regression/nike.csv')
    # ts = TimeSeries.from_dataframe(test, time_col='time_interval', value_cols=['count'])
    
    # latest_date = datetime.strptime(dataset[-1]['time_interval'], '%Y-%m-%d %H:%M:%S')
    # split_date = latest_date - timedelta(days=15)

    # train, val = ts.split_after(pd.Timestamp(split_date))
    # logging.debug(ts)
    # logging.debug(train)
    
    # tcn = TCNModel(
    #     input_chunk_length=(24*14) + 1,
    #     output_chunk_length=24*14,
    #     n_epochs=400,
    #     dropout=0.1,
    #     dilation_base=2,
    #     weight_norm=True,
    #     kernel_size=5,
    #     num_filters=3,
    #     random_state=0
    # )
    # tcn.fit(ts)
    # logging.debug(tcn.predict(1))
    # arima = AutoARIMA()
    # arima.fit(series=ts)
    # logging.debug(arima.model.summary())
    # logging.debug(ts)
    # logging.debug(arima.predict(1))
    return Response(json.dumps(dataset), status=HTTPStatus.OK, content_type="application/json")