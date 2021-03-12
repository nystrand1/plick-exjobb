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
from ..utils.dataset import *

TRAIN_SIZE_PERCENTAGE = 85

def create_dataset(dataset, look_back=1):
 dataX, dataY = [], []
 for i in range(len(dataset)-look_back-1):
    a = dataset[i:(i+look_back), 0]
    dataX.append(a)
    dataY.append(dataset[i + look_back, 0])
 return numpy.array(dataX), numpy.array(dataY)

def train_test_split(data, n_test):
    return data[:-n_test], data[-n_test:]

def handle_lstm(db):
    data = request.json
    dataset = count_interval_unique(
        db=db, **data)

    train_size = int(len(dataset)*TRAIN_SIZE_PERCENTAGE/100)
    test_size = len(dataset) - train_size
    train, test = train_test_split(dataset, test_size)
    trainX, trainY = create_dataset(train)
    testX, testY = create_dataset(test)
    logging.debug(trainX)
    logging.debug(trainY)