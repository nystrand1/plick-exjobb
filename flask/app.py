import time
import redis
from decouple import config
from flask import Flask, request
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