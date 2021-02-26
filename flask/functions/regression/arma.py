import numpy as np
import pandas as pd
import json
import logging
import time
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from flask import request
from sklearn.metrics import r2_score

from ..count_interval import *
from ..utils.generator import *
from ..utils.merge import *

def determine_seasonality(dataset):
    count_list = list()
    date_list = list()
    for d in dataset:
        count_list.append(d['count'])
        date_list.append(datetime.strptime(d['time_interval'], '%Y-%m-%d'))
    df = pd.DataFrame({ 'data': count_list }, index=date_list)
    result = seasonal_decompose(df, model='multiplicative')
    logging.debug(result.seasonal)
    logging.debug(result.trend)
    logging.debug(result.resid)
    logging.debug(result.observed)



def handle_arma_regression(db):
    data = request.json
    dataset = count_interval_unique(db=db, **data)
    determine_seasonality(dataset)


    model_scores = dict()
    if False:
        for n in range(1, 4):
            key_name = "arma ({},{},{})".format(n,n%2,n)
            order = (n,n%2,n)
            arma_model = get_arma_model(dataset, order=order)
            trend_dataset = generate_arma_series_from_model(
                len(dataset), arma_model.fit())
            dataset = merge_datasets(dataset, trend_dataset, key_name=key_name)
            # model_score = get_model_score(dataset, trend_key=key_name, model=arma_model)
            # model_scores[key_name] = model_score
            # logging.debug(model_score)
    res = {
        'dataset': dataset,
        'model_scores': model_scores
    }
    return res

def get_arma_model(dataset, order):
    data = dict()
    count_list = list()
    for d in dataset:
        count_list.append(d['count'])
    data['amount'] = count_list
    data['time_slices'] = range(0, len(dataset))
    formatted_data = pd.DataFrame(data=data)
    model = ARIMA(formatted_data.amount, order=order)
    return model

def get_model_r2_score(combined_dataset, trend_key):
    y = [d['count'] for d in combined_dataset]
    y_pred = [d['trends'][trend_key] for d in combined_dataset]
    score = r2_score(y, y_pred)
    return score

def get_model_score(combined_dataset, trend_key, model):
    y = [d['count'] for d in combined_dataset]
    y_pred = [d['trends'][trend_key] for d in combined_dataset]
    score = model.score(y)
    return score[0]