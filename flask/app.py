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

from .models.search_record import SearchRecord
from .functions.utils.sanitizer import *
from .functions.query_filter import *
from .functions.count_interval import *
from .functions.regression.linear import *
from .functions.regression.arma import handle_arma_regression
from .functions.regression.sarma import handle_sarma_regression
from .functions.regression.lstm import handle_lstm
from .functions.regression.auto_sarima import handle_auto_sarima_regression


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
    data['end_date'] = "2021-02-18"
    data['trunc_by'] = "day"
    for r in res:
        data['query'] = r['query']
        dataset = count_interval_unique(db, **data)
        linear_model = get_linear_model(dataset)
        save_to_db(db, linear_model, data['query'], "1 month")
    db.session.commit()
    return Response(json.dumps(get_query_candidates(db)), status=HTTPStatus.OK, content_type="application/json")