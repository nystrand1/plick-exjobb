import math
import logging
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose

def generate_linear_series_from_model(time_series_len, model):
    res = list()
    predict = np.poly1d(model)
    for i in range(time_series_len):
        res.append(predict(i))

    return res

def generate_arma_series_from_model(time_series_len, list):
    train_size = int(time_series_len*0.6)
    res = list()
    prediction = model.predict(train_size, time_series_len)
    logging.debug(prediction)
    return [round(val) for val in prediction]

def generate_trend_from_decompose(series, period = 7):
    formatted_series = [d['count'] for d in series]
    data = seasonal_decompose(formatted_series, model='additive', period=period)
    return data.trend