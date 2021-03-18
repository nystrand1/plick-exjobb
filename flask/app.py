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
from http import HTTPStatus

import multiprocessing
from joblib import Parallel
from joblib import delayed

from .models.search_record import SearchRecord
from .models.term_trend import TermTrend
from .functions.utils.sanitizer import *
from .functions.query_filter import *
from .functions.count_interval import *
from .functions.regression.linear import *
from .functions.regression.arma import handle_arma_regression
from .functions.regression.sarma import handle_sarma_regression
from .functions.regression.lstm import handle_lstm
from .functions.regression.auto_sarima import handle_auto_sarima_regression
from .functions.utils.dataset import *
from .functions.process_queries import *


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
    res = get_query_candidates(db)
    data = dict()
    data['start_date'] = "2021-01-01"
    data['end_date'] = "2021-03-15"
    data['trunc_by'] = "day"
    db.session.query(TermTrend).delete()
    db.session.commit()
    processed_queries = []
    [process_query(db, data, r, processed_queries) for r in res]
    db.session.commit()
    return Response(json.dumps(get_query_candidates(db)), status=HTTPStatus.OK, content_type="application/json")

@app.route('/trending-words', methods=['GET'])
@cross_origin()
def trending_words():
    res = get_trending_words(db)
    return Response(json.dumps(res), status=HTTPStatus.OK, content_type="application/json")
 