import time
import redis
import json
import datetime
import logging
import sys
from decouple import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy as sa
from flask_sqlalchemy import Model
from flask_cors import CORS, cross_origin

from .models.search_record import SearchRecord
from .functions.regression.linear import handle_linear_regression


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
cache = redis.Redis(host='redis', port=6379)
db = sa(app)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@app.route('/linear-regression', methods=['POST'])
@cross_origin()
def linear_regression():
    return handle_linear_regression(db)
