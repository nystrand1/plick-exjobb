import numpy as np
import pandas as pd
import json
import logging
import time
import warnings
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from flask import request
from sklearn.metrics import r2_score, mean_squared_error

from ..count_interval import *
from ..utils.generator import *
from ..utils.merge import *

TRAIN_SIZE_PERCENTAGE = 60

def find_best_arima(dataset, p_values=[1], d_values=[1], q_values=[1,2,3]):
    warnings.filterwarnings("ignore")
    best_score, best_model, best_order = float("inf"), None, None
    predictions = list()
    for p in p_values:
        for d in d_values:
            for q in q_values:
                order = (p, d, q)
                logging.debug(order)
                model, score, predictions = evaluate_model(dataset, order)
                if score < best_score:
                    best_score, best_model, best_order = score, model, order
    return best_model, best_score, best_order, predictions

def evaluate_model(dataset, order):
    train_size = int(len(dataset)*TRAIN_SIZE_PERCENTAGE/100)
    formatted_data = [d['count'] for d in dataset]
    train_dataset, test_dataset = formatted_data[0:train_size], formatted_data[train_size:]

    history = [x for x in train_dataset]
    predictions = list()
    for t in range(len(test_dataset)):
        model = ARIMA(history, order=order)
        model_fit = model.fit()
        y_hat = model_fit.forecast()[0]
        logging.debug("TRUE VALUE: {}".format(test_dataset[t]))
        logging.debug("PREDTICTED VALUE: {}".format(y_hat))
        predictions.append(round(y_hat))
        history.append(test_dataset[t])

    error = mean_squared_error(test_dataset, predictions)

    return model, error, predictions

def handle_arma_regression(db):
    data = request.json
    dataset = count_interval_unique(db=db, **data)
    model_scores = dict()
    if len(dataset) > 1:
        arma_model, score, order, predictions = find_best_arima(dataset)
        logging.debug("BEST ARIMA ORDER")
        logging.debug(order)
        key_name = "arma {}".format(order)
        dataset = merge_partial_dataset(dataset, predictions, key_name=key_name)
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