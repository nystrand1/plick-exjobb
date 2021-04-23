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
    generate_query_tcn_models(db)
    logging.debug("GENERATING CATEGORY TCN MODELS")
    #generate_category_tcn_models(db)
    logging.debug("GENERATING BRAND TCN MODELS")
    #generate_brand_tcn_models(db)
    return Response(json.dumps("success"), status=HTTPStatus.OK, content_type="application/json")

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
    param_dict = dict()
    for i in range(1, 21):
        dataset = get_category_dataset(db, i)
        logging.debug(dataset['time_series_day'])
        ts = dataset['time_series_day']
        if(dataset['model_tcn'] is None):
            model = get_tcn_model(dataset=ts)
            param_dict[i] = model[1]
            model = model[0]
        else:
            model = pickle.loads(dataset['model_tcn'])
        predictions = get_tcn_predictions(model)
        store_tcn_model(db, pickle.dumps(model), trend_type="category", id=i)
        store_tcn_prediction(db, prediction=predictions, id=i)

    logging.debug(param_dict)
    return Response(json.dumps(predictions), status=HTTPStatus.OK, content_type="application/json")

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

@app.route('/darts-test', methods=['GET'])
@cross_origin()
def darts_test():
    dataset = get_brand_dataset(db, 5)
    logging.debug(dataset['time_series_day'])
    dataset = dataset['time_series_day']
    test = pd.DataFrame.from_dict(dataset)
    test.to_csv('./functions/regression/mk_day.csv')
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
