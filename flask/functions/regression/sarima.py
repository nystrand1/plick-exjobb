import numpy as np
import pandas as pd
import json
import logging
import time
import warnings
from datetime import datetime
from flask import request
from darts import TimeSeries
from darts.models import AutoARIMA

from ...models.brand_trend import BrandTrend
from ...models.category_trend import CategoryTrend
from ...models.query_trend import QueryTrend

def get_sarima_model(dataset):
    # df = pd.DataFrame.from_dict(dataset)
    # ts = TimeSeries.from_dataframe(df, time_col='time_interval')
    df = pd.read_csv("shoes.csv")
    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])
    arima = AutoARIMA()
    arima.fit(series=ts)
    # train_size = int(TRAIN_SIZE_PERCENTAGE*len(dataset)/100)
    # train = formatted_data[:train_size]
    # test = formatted_data[train_size:]
    # seasonal_interval = 7
    # model = get_model(formatted_data, train, seasonal_interval)
    logging.debug(arima.model.summary())
    return arima.model

def store_sarima_model(db, serialized_model, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(BrandTrend).filter_by(query=id).first()
    if(record is not None):
        record.model_sarima = serialized_model
    else:
        logging.debug("what")
    db.session.commit()