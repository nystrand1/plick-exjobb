import numpy as np
import pandas as pd
import logging
import matplotlib.pyplot as plt

from ...models.brand_trend import BrandTrend
from ...models.category_trend import CategoryTrend
from ...models.query_trend import QueryTrend

from datetime import datetime
from darts import TimeSeries
from darts.models import TCNModel
from darts.models import ExponentialSmoothing
from darts.utils.utils import ModelMode
from darts.dataprocessing.transformers import Scaler
from darts.utils.timeseries_generation import datetime_attribute_timeseries


def get_tcn_model(dataset = None, plot=False):
    #dataset = dataset['time_series_hour']
#    df = pd.DataFrame.from_dict(dataset)
    if(dataset is None):
        df = pd.read_csv("nike.csv")
    else:
        df = pd.DataFrame.from_dict(dataset)

    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])
    
    train, val = ts.split_after(0.8) #80% train, 20% val

    params = dict()
    params['kernel_size'] = [3,4,5]
    params['num_filters'] = [9,12,15]
    params['random_state'] = [0,1]
    params['input_chunk_length'] = [8]
    params['output_chunk_length'] = [7]
    params['dilation_base'] = [1,2]
    params['n_epochs'] = [50]
    params['dropout'] = [0, 0.2]
    params['weight_norm'] = [True]
    tcn = TCNModel.gridsearch(
        parameters=params,
        series=train,
        val_series=val,
        verbose=True,
    )
    logging.debug(tcn)
    tcn_model = tcn[0]
    tcn_model.fit(series=train, val_series=val)
    backtest = tcn_model.historical_forecasts(
        series=ts,
        start=0.8,
        forecast_horizon=1,
        stride=1,
        retrain=False,
        verbose=True
    )

    future = tcn_model.predict(7)

    if(plot):
        backtest.plot(label='backtest')
        future.plot(label='future')
        ts.plot(label='actual')
        plt.legend()
        plt.show()
    else: 
        return tcn_model

def store_tcn_model(db, serialized_model, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(BrandTrend).filter_by(query=id).first()
    if(record is not None):
        record.model_tcn = serialized_model
    else:
        logging.debug("what")
    db.session.commit()

if __name__ == '__main__':
    print("hello")
    get_tcn_model(plot=True)