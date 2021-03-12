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
from ..query_filter import *
from ...models.term_trend import TermTrend


def handle_linear_regression(db):
    data = request.json
    data['similar_queries'] = get_similar_words(db, data['query'])
    dataset = count_interval_unique_similar(
        db=db, **data)
    model_scores = dict()
    if len(dataset) > 1:
        for n in range(1, 2):
            key_name = "degree {}".format(n)
            linear_model = get_linear_model(dataset, n)
            #save_to_db(db, linear_model, data['query'], "1 month")
            #decompose_trend = generate_trend_from_decompose(dataset)
            trend_dataset = generate_linear_series_from_model(
                len(dataset), linear_model)
            dataset = merge_datasets(dataset, trend_dataset, key_name=key_name)
            # dataset = merge_datasets(
            #    dataset, decompose_trend, key_name="Decompose trend")
            model_score = get_model_score(dataset, trend_key=key_name)
            model_scores[key_name] = model_score
            logging.debug(model_score)
    logging.debug(dataset)
    res = {
        'dataset': dataset,
        'model_scores': model_scores
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


def save_to_db(db, query, model_short, model_mid, model_long, similar_queries):
    record = TermTrend(
        query=query, model_short=model_short, model_mid=model_mid, model_long=model_long, similar_queries=similar_queries, created_at=datetime.now(), updated_at=datetime.now())
    record.create()
    db.session.add(record)
