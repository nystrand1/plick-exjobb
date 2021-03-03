import math
import logging
import numpy as np

def generate_linear_series_from_model(time_series_len, model):
    res = list()
    predict = np.poly1d(model)
    for i in range(time_series_len):
        res.append(int(predict(i)))

    return res

def generate_arma_series_from_model(time_series_len, list):
    train_size = int(time_series_len*0.6)
    res = list()
    prediction = model.predict(train_size, time_series_len)
    logging.debug(prediction)
    return [round(val) for val in prediction]