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
from pmdarima.arima import *

from ..count_interval import *
from ..utils.generator import *
from ..utils.dataset import *

TRAIN_SIZE_PERCENTAGE = 90


def get_model(dataset, train_data, seasonal_interval = 24):
    adf = ADFTest(alpha=0.05)
    if (adf.should_diff(dataset)):
        logging.debug("SEASONAL")
        model = auto_arima(train_data, seasonal=True, trace=True,
                           random_state=20, n_fits=50, stepwise=True, m=seasonal_interval)
    else:
        logging.debug("NON-SEASONAL")
        model = auto_arima(train_data, seasonal=False)

    return model


def walk_forward_predictions(model, train_dataset, test_dataset):
    predictions = list()

    for t in range(len(test_dataset)):
        prediction = model.predict()[0]
        predictions.append(prediction)
        logging.debug("Predicted value: {}".format(prediction))
        logging.debug("Expected value: {}".format(test_dataset[t]))
        model.update(test_dataset[t])

    return predictions

def get_seasonal_interval(data):
    if 'trunc_by' in data:
        trunc_by = data['trunc_by']
        if trunc_by == "hour":
            return 24
        elif trunc_by == "day":
            return 7
        elif trunc_by == "week":
            return 52
    else:
        return 12


def handle_auto_sarima_regression(db):
    data = request.json
    dataset = count_interval_unique(db=db, **data)
    model_scores = dict()
    formatted_data = np.array([d['count'] for d in dataset])
    train_size = int(TRAIN_SIZE_PERCENTAGE*len(dataset)/100)
    train = formatted_data[:train_size]
    test = formatted_data[train_size:]
    seasonal_interval = get_seasonal_interval(data)
    if len(dataset) > 1:
        model = get_model(formatted_data, train, seasonal_interval)
        key_name = "auto_arima {}()".format(model.order, model.seasonal_order)
        predictions = model.predict(len(test))
        dataset = merge_partial_dataset(
            dataset, predictions, key_name=key_name)
        # model_score = get_model_score(dataset, trend_key=key_name, model=arma_model)
        # model_scores[key_name] = model_score
        logging.debug(model.summary())
    res = {
        'dataset': dataset,
        'model_scores': model_scores
    }
    return res
