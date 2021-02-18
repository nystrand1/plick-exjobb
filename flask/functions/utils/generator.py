import math
import numpy as np

def generate_series_from_model(time_series_len, model):
    res = list()
    predict = np.poly1d(model)
    for i in range(time_series_len+5):
        res.append(predict(i))

    return res