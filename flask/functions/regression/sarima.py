import numpy as np
import pandas as pd
import json
import logging
import time
import warnings
import pickle
import matplotlib.pyplot as plt

from datetime import datetime
from flask import request
from darts import TimeSeries
from darts.models import AutoARIMA
from darts.metrics import *

from ...models.brand_trend import BrandTrend
from ...models.category_trend import CategoryTrend
from ...models.query_trend import QueryTrend
from ..utils.dataset import to_dataset


def get_sarima_model(dataset=None, plot=False, verbose=False):
    if(dataset is None):
        df = pd.read_csv("nike.csv")
    else:
        df = pd.DataFrame.from_dict(dataset)

    ts = TimeSeries.from_dataframe(
        df, time_col='time_interval', value_cols=['count'])

    train, val = ts.split_after(0.8)  # 80% train, 20% val
    params = dict()
    params['m'] = [7]  # Weekly seasonality
    sarima = AutoARIMA.gridsearch(
        parameters=params,
        series=train,
        val_series=val,
        verbose=verbose,
        metric=mse
    )
    logging.debug("CHOSEN PARAMETERS:")
    params = sarima[1]
    sarima_model = sarima[0]
    sarima_model.fit(series=ts)
    print(params)
    if(plot):
        backtest = sarima_model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            verbose=verbose
        )
        print(val)
        print(backtest)
        print("R2: {}".format(r2_score(val, backtest[1:], intersect=False)))
        print("MAPE: {}".format(mape(val, backtest[1:])))
        print("MASE: {}".format(mase(val, backtest[1:], train)))
        print("MAE: {}".format(mae(val, backtest[1:])))
        backtest.plot(label='backtest')
        ts.plot(label='actual')
        plt.legend()
        plt.show()
    else:
        return [sarima_model, params]


def eval_all_sarima_models(db, categories, brands, queries):
    scores = list() 
    for brand in brands:
        score = eval_sarima_model(brand['model_sarima'], brand['time_series_day'])
        score['topic'] = brand['brand_name']
        score['topic_id'] = brand['brand_id']
        store_sarima_score(db, score=score, trend_type="brand", id=brand['brand_id'])
        scores.append(score)

    for category in categories:
        score = eval_sarima_model(category['model_sarima'], category['time_series_day'])
        score['topic'] = category['category_name']
        score['topic_id'] = category['category_id']
        store_sarima_score(db, score=score, trend_type="category", id=category['category_id'])
        scores.append(score)

    for query in queries:
        score = eval_sarima_model(query['model_sarima'], query['time_series_day'])
        score['topic'] = query['query']
        score['topic_id'] = query['query']
        store_sarima_score(db, score=score, trend_type="query", id=query['query'])
        scores.append(score)

    mean_scores = dict()

    mape_sum = 0
    mape_count = 0
    r2_sum = 0
    mase_sum = 0
    mae_sum = 0

    for score in scores:
        try:
            mape_sum += float(score['mape_score'])
            mape_count += 1
        except:
            pass
        r2_sum += float(score['r2'])
        mase_sum += float(score['mase_score'])
        mae_sum += float(score['mae_score'])

    mean_scores['r2'] = r2_sum/len(scores)
    mean_scores['mape'] = mape_sum/mape_count
    mean_scores['mase'] = mase_sum/len(scores)
    mean_scores['mae'] = mae_sum/len(scores)
    mean_scores['mape_count'] = mape_count

    return mean_scores


def eval_sarima_model(serialized_model, dataset):
    sarima_model = pickle.loads(serialized_model)
    df = pd.DataFrame.from_dict(dataset)
    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])
    train, val = ts.split_after(0.8) #80% train, 20% val
    sarima_model.fit(train)
    no_retrain = sarima_model.predict(len(val))
    backtest = sarima_model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
    )
    scores = dict()
    scores['retrained']['r2'] = r2_score(val, backtest[1:])
    scores['retrained']['mase_score'] = mase(val, backtest[1:], train)
    scores['retrained']['mae_score'] = mae(val, backtest[1:])
    scores['not_retrained']['r2'] = r2_score(val, no_retrain)
    scores['not_retrained']['mase_score'] = mase(val, no_retrain, train)
    scores['not_retrained']['mae_score'] = mae(val, no_retrain)
    try:
        scores['retrained']['mape_score'] = mape(val, backtest[1:])
        scores['not_retrained']['mape_score'] = mape(val, no_retrain)
    except:
        scores['retrained']['mape_score'] = "Could not be calculated (Zero value in time series)"
        scores['not_retrained']['mape_score'] = "Could not be calculated (Zero value in time series)"
    return scores


def get_sarima_predictions(model):
    prediction = model.predict(7)  # Predict a week ahead
    prediction_json = json.loads(prediction.to_json())
    dates = prediction_json['index']
    counts = prediction_json['data']
    prediction_dataset = to_dataset(dates, counts)
    logging.debug(prediction_dataset)
    return prediction_dataset


def store_sarima_model(db, serialized_model, trend_type="category", id=12):
    if(trend_type == "category"):
        record = db.session.query(CategoryTrend).filter_by(
            category_id=id).first()
    elif(trend_type == "brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.model_sarima = serialized_model
    else:
        logging.debug("what")
    db.session.commit()


def store_sarima_prediction(db, prediction=False, trend_type="category", id=12):
    if(trend_type == "category"):
        record = db.session.query(CategoryTrend).filter_by(
            category_id=id).first()
    elif(trend_type == "brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.sarima_prediction = prediction
    else:
        logging.debug("what")
    db.session.commit()

def store_sarima_score(db, score = None, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.sarima_metrics = score
    else:
        logging.debug("what")
    db.session.commit()


if __name__ == '__main__':
    print("hello")
    get_sarima_model(plot=True, verbose=True)
