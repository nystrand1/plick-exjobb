import numpy as np
import pandas as pd
import json
import logging
import time
from datetime import datetime

def get_linear_model(dataset):
    logger = logging.getLogger(__name__)
    data = dict()
    count_list = list()
    for d in dataset:
        count_list.append(d['count'])
    data['amount'] = count_list
    data['time_slices'] = range(0, len(dataset))

    formatted_data = pd.DataFrame(data=data)
    x = formatted_data.time_slices
    y = formatted_data.amount
    logger.debug(formatted_data)
    model = np.polyfit(x, y, 1)
    logger.debug(model)
    return model.tolist()

