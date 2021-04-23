import numpy as np
import pandas as pd
import json
import logging
import time
import warnings
import matplotlib.pyplot as plt

# from ...models.brand_trend import BrandTrend
# from ...models.category_trend import CategoryTrend
# from ...models.query_trend import QueryTrend
# from ..utils.dataset import to_dataset


from darts import TimeSeries
from darts.models import RNNModel
from darts.dataprocessing.transformers import Scaler
from darts.utils.timeseries_generation import datetime_attribute_timeseries


TRAIN_SIZE_PERCENTAGE = 85

def get_lstm_model(dataset = None, plot = False, verbose = False):
    if(dataset is None):
        df = pd.read_csv("nike.csv")
    else:
        df = pd.DataFrame.from_dict(dataset)

    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])
    
    train, val = ts.split_after(0.8)

    params = dict()
    params['model'] = ["LSTM"]
    params['hidden_size'] = [50]
    params['n_rnn_layers'] = [1]
    params['input_chunk_length'] = [14]
    params['output_chunk_length'] = [7]
    params['n_epochs'] = [100]
    params['dropout'] = [0.1]
    #params['hidden_fc_sizes'] = [4]
    params['batch_size'] = [1]
    params['random_state'] = [0]
    #params['torch_device_str'] = ["vulkan"]

    lstm = RNNModel.gridsearch(
        parameters=params,
        series=train,
        val_series=val,
        verbose=verbose
    )

    # lstm_model = RNNModel(
    #     model="LSTM",
    #     input_chunk_length=14,
    #     output_chunk_length=1,
    #     hidden_size=25,
    #     n_rnn_layers=2,
    #     dropout=0.4,
    #     batch_size=16,
    #     n_epochs=100,
    #     optimizer_kwargs={'lr': 1e-3},
    #     model_name='Shoes_RNN',
    #     log_tensorboard=True,
    #     random_state=1
    # )
    params = lstm[1]
    lstm_model = lstm[0]

    lstm_model.fit(train, val_series=val)

    if(plot):
        backtest = lstm_model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            retrain=False,
            verbose=False
        )

        future = lstm_model.predict(7)
        backtest.plot(label='backtest')
        future.plot(label='future')
        ts.plot(label='actual')
        plt.legend()
        plt.show()
    else: 
        return [lstm_model, params]


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

def store_lstm_prediction(db, prediction = False, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.lstm_prediction = prediction
    else:
        logging.debug("what")
    db.session.commit()


if __name__ == '__main__':
    print("hello")
    get_lstm_model(plot=True, verbose=True)