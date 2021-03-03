from math import sqrt
from multiprocessing import cpu_count
from joblib import Parallel
from joblib import delayed
from warnings import catch_warnings
from warnings import filterwarnings
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
from flask import request
import pandas as pd
import logging

from ..count_interval import *
from ..utils.generator import *
from ..utils.merge import *

TRAIN_SIZE_PERCENTAGE = 85

# one-step sarima forecast
def sarima_forecast(history, config):
    order, sorder, trend = config
    # define model
    model = SARIMAX(history, order=order, seasonal_order=sorder, trend=trend,
                    enforce_stationarity=False, enforce_invertibility=False)
    # fit model
    model_fit = model.fit(disp=False)
    # make one step forecast
    yhat = model_fit.predict(len(history), len(history))
    return yhat[0]

# root mean squared error or rmse


def measure_rmse(actual, predicted):
    return sqrt(mean_squared_error(actual, predicted))

# split a univariate dataset into train/test sets


def train_test_split(data, n_test):
    return data[:-n_test], data[-n_test:]


def grid_search(data, cfg_list, n_test, parallel=True):
    scores = None
    if parallel:
        logging.debug("EXECUTING IN PARALLELL")
        # execute configs in parallel
        executor = Parallel(n_jobs=cpu_count(), backend='multiprocessing')
        tasks = (delayed(score_model)(data, n_test, cfg) for cfg in cfg_list)
        scores = executor(tasks)
    else:
        logging.debug("EXECUTING IN SEQUENTIAL")
        scores = [score_model(data, n_test, cfg) for cfg in cfg_list]
    # remove empty results
    scores = [r for r in scores if r[1] != None]
    # sort configs by error, asc
    scores.sort(key=lambda tup: tup[1])
    return scores

# walk-forward validation for univariate data
def walk_forward_validation(data, n_test, cfg):
	predictions = list()
	# split dataset
	train, test = train_test_split(data, n_test)
	# seed history with training dataset
	history = [x for x in train]
	# step over each time-step in the test set
	for i in range(len(test)):
		# fit model and make forecast for history
		yhat = sarima_forecast(history, cfg)
		# store forecast in list of predictions
		predictions.append(yhat)
		# add actual observation to history for the next loop
		history.append(test[i])
	# estimate prediction error
	error = measure_rmse(test, predictions)
	return (error, predictions)

def sarima_configs(seasonal=[0]):
    models = list()
    # define config lists
    p_params = [0, 1, 2]
    d_params = [0, 1]
    q_params = [0, 1, 2]
    t_params = ['n', 'c', 't', 'ct']
    P_params = [0, 1, 2]
    D_params = [0, 1]
    Q_params = [0, 1, 2]
    m_params = seasonal
    # create config instances
    for p in p_params:
        for d in d_params:
            for q in q_params:
                for t in t_params:
                    for P in P_params:
                        for D in D_params:
                            for Q in Q_params:
                                for m in m_params:
                                    cfg = [(p, d, q), (P, D, Q, m), t]
                                    models.append(cfg)
    return models


def score_model(data, n_test, cfg, debug=False):
    result = None
    # convert config to a key
    key = str(cfg)
    # show all warnings and fail on exception if debugging
    if debug:
        result = walk_forward_validation(data, n_test, cfg)
    else:
        # one failure during model validation suggests an unstable config
        try:
            # never show warnings when grid searching, too noisy
            with catch_warnings():
                filterwarnings("ignore")
                result = walk_forward_validation(data, n_test, cfg)
        except:
            error = None
    # check for an interesting result
    if result is not None:
        logging.debug(' > Model[%s] %.3f' % (key, result[0]))
    return (key, result)


def convert_data_to_series(dataset):
    series = [d['count'] for d in dataset]
    return series


def handle_sarma_regression(db):
    data = request.json
    dataset = count_interval_unique(db=db, **data)
    model_scores = dict()

    if len(dataset) > 1:
        configs = sarima_configs(seasonal=[24])
        train_size = int(len(dataset)*TRAIN_SIZE_PERCENTAGE/100)
        test_size = len(dataset) - train_size
        series = convert_data_to_series(dataset)
        logging.debug(series)
        scores = grid_search(series, configs, test_size)
        best_config, best_result = scores[0]
        logging.debug("BEST SARIMA ORDER")
        logging.debug(best_config)
        logging.debug(best_result)
        predictions = best_result[1]
        key_name = "sarma"
        dataset = merge_partial_dataset(
            dataset, predictions, key_name=key_name)
        # model_score = get_model_score(dataset, trend_key=key_name, model=arma_model)
        # model_scores[key_name] = model_score
        # logging.debug(model_score)
    res = {
        'dataset': dataset,
        'model_scores': best_result[0]
    }
    return res
