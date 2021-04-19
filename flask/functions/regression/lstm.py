import numpy as np
import pandas as pd
import json
import logging
import time
import warnings
import matplotlib.pyplot as plt

from ...models.brand_trend import BrandTrend
from ...models.category_trend import CategoryTrend
from ...models.query_trend import QueryTrend

from darts import TimeSeries
from darts.models import RNNModel
from darts.dataprocessing.transformers import Scaler
from darts.utils.timeseries_generation import datetime_attribute_timeseries


TRAIN_SIZE_PERCENTAGE = 85

def get_lstm_model():
    df = pd.read_csv("shoes.csv")
    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])

    train, val = ts.split_after(pd.Timestamp('2021-02-15 00:00:00'))

    lstm_model = RNNModel(
        model="LSTM",
        input_chunk_length=14,
        output_chunk_length=1,
        hidden_size=25,
        n_rnn_layers=2,
        dropout=0.4,
        batch_size=16,
        n_epochs=400,
        optimizer_kwargs={'lr': 1e-3},
        model_name='Shoes_RNN',
        log_tensorboard=True,
        random_state=1
    )

    lstm_model.fit(train, val_series=val, verbose=True)

    backtest = lstm_model.historical_forecasts(
        series=ts,
        start=pd.Timestamp('2021-03-01'),
        forecast_horizon=1,
        retrain=False,
        verbose=True
    )

    ts.plot(label='actual')
    backtest.plot(label='backtest')
    plt.legend()
    plt.show()


def store_lstm_model(db, serialized_model, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(BrandTrend).filter_by(query=id).first()
    if(record is not None):
        record.model_lstm = serialized_model
    else:
        logging.debug("what")
    db.session.commit()


if __name__ == '__main__':
    print("hello")
    get_lstm_model()