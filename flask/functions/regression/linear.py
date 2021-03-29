import numpy as np
import pandas as pd
import json
import logging
import time
from datetime import datetime
from sklearn.metrics import r2_score
from flask import request

from ..count_interval import *
from ..utils.generator import *
from ..utils.dataset import *
from ..utils.plick import *
from ..query_filter import *
from ...models import *


def handle_linear_regression(db):
    data = request.json
    query = data['query']
    dataset = get_query_dataset(db, query)
    time_series = dataset['time_series_hour']
    if len(time_series) > 1:
        for n in range(1, 2):
            key_name = "degree {}".format(n)
            linear_model = get_linear_model(time_series, n)
            trend_dataset = generate_linear_series_from_model(
                len(time_series), linear_model)
            time_series = merge_datasets(time_series, trend_dataset, key_name=key_name)
    logging.debug(time_series)

    related_ads = get_ads(query)
    res = {
        'dataset': dataset,
        'related_ads': related_ads,
    }
    return res


def get_linear_model(dataset, degree=1):
    data = dict()
    count_list = list()
    for d in dataset:
        count_list.append(d['count'])
    data['amount'] = count_list
    data['time_slices'] = range(0, len(dataset))

    formatted_data = pd.DataFrame(data=data)
    x = formatted_data.time_slices
    y = formatted_data.amount
    model = np.polyfit(x, y, degree)
    logging.debug(model)
    return model.tolist()


def get_model_score(combined_dataset, trend_key):
    y = [d['count'] for d in combined_dataset]
    y_pred = [d['trends'][trend_key] for d in combined_dataset]
    score = r2_score(y, y_pred)
    return score


def save_to_db(db, data):
    TermTrend().create()
    record = db.session.query(TermTrend).get(data['query'])
    if(record is not None):
        record.model_long = data['model_long']
        record.model_mid = data['model_mid']
        record.model_short = data['model_short']
        record.similar_queries = data['similar_queries']
        record.updated_at = data['updated_at']
    else:
        record = TermTrend(**data)
        db.session.add(record)