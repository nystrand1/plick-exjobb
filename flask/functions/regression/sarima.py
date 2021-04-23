import numpy as np
import pandas as pd
import json
import logging
import time
import warnings
import matplotlib.pyplot as plt

from datetime import datetime
from flask import request
from darts import TimeSeries
from darts.models import AutoARIMA
from darts.metrics import *

# from ...models.brand_trend import BrandTrend
# from ...models.category_trend import CategoryTrend
# from ...models.query_trend import QueryTrend
# from ..utils.dataset import to_dataset

def get_sarima_model(dataset = None, plot=False, verbose=False):
    if(dataset is None):
        df = pd.read_csv("nike.csv")
    else:
        df = pd.DataFrame.from_dict(dataset)

    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])
    
    train, val = ts.split_after(0.8) #80% train, 20% val
    params = dict()
    params['m'] = [7] #Check for yearly and weekly seasonality
    arima = AutoARIMA.gridsearch(
        parameters=params,
        series=train,
        val_series=val,
        verbose=verbose

    )
    logging.debug("CHOSEN PARAMETERS:")
    params = arima[1]
    arima_model = arima[0]
    arima_model.fit(series=ts)
    if(plot):
        backtest = arima_model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            verbose=verbose
        )
        print(val)
        print(backtest[1:])
        print("ACC")
        print(coefficient_of_variation(val, backtest[1:]))
        print(r2_score(val, backtest[1:]))
        print(mape(val, backtest[1:]))
        print(mase(val, backtest[1:], train))
        print(mse(val, backtest[1:]))


        future = arima_model.predict(7)
        backtest.plot(label='backtest')
        future.plot(label='future')
        ts.plot(label='actual')
        plt.legend()
        plt.show()
    else: 
        return [arima_model, params]

def get_model_accuracy(val_series, pred_series):
    pass

def get_sarima_predictions(model):
    prediction = model.predict(7) #Predict a week ahead
    prediction_json = json.loads(prediction.to_json())
    dates = prediction_json['index']
    counts = prediction_json['data']
    prediction_dataset = to_dataset(dates, counts)
    logging.debug(prediction_dataset)
    return prediction_dataset

def store_sarima_model(db, serialized_model, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.model_sarima = serialized_model
    else:
        logging.debug("what")
    db.session.commit()

def store_sarima_prediction(db, prediction = False, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.sarima_prediction = prediction
    else:
        logging.debug("what")
    db.session.commit()

if __name__ == '__main__':
    print("hello")
    get_sarima_model(plot=True, verbose=True)