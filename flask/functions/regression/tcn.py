import numpy as np
import pandas as pd
import logging
import simplejson as json
import matplotlib.pyplot as plt
import pickle

# from ...models.brand_trend import BrandTrend
# from ...models.category_trend import CategoryTrend
# from ...models.query_trend import QueryTrend
# from ..utils.dataset import to_dataset

from datetime import datetime
from darts import TimeSeries
from darts.models import TCNModel
from darts.models import ExponentialSmoothing
from darts.utils.utils import ModelMode
from darts.dataprocessing.transformers import Scaler, MissingValuesFiller, Mapper, InvertibleMapper
from darts.utils.timeseries_generation import datetime_attribute_timeseries
from darts.metrics import *
from torch.nn import MSELoss, L1Loss


def get_tcn_model(dataset = None, plot=False, verbose=False):
    #dataset = dataset['time_series_hour']
#    df = pd.DataFrame.from_dict(dataset)
    if(dataset is None):
        df = pd.read_csv("zadig_day.csv")
    else:
        df = pd.DataFrame.from_dict(dataset)
    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])


    # scaler = Scaler()
    # ts = scaler.fit_transform(ts)
    
    train, val = ts.split_after(0.8) #80% train, 20% val

    params = dict()
    params['kernel_size'] = [2,6]
    params['num_filters'] = [10]
    params['random_state'] = [0]
    #params['input_chunk_length'] = [11, 27] nike
    params['input_chunk_length'] = [11, 22, 27]
    params['output_chunk_length'] = [7]
    params['dilation_base'] = [1,2,4] 
    #params['dilation_base'] = [1, 2, 3] nike
    params['n_epochs'] = [50]
    params['dropout'] = [0]
    params['nr_epochs_val_period'] = [10]
    params['loss_fn'] = [MSELoss()]
    params['weight_norm'] = [True]
    tcn = TCNModel.gridsearch(
        parameters=params,
        series=train,
        val_series=val,
        verbose=verbose,
        metric=mse
    )
    logging.debug("CHOSEN PARAMETERS:")
    params = tcn[1]
    tcn_model = tcn[0]
    tcn_model.fit(series=ts)

    if(plot):
        backtest = tcn_model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            retrain=False,
            verbose=verbose
        )

        print(val)
        print(backtest[1:])
        print("R2: {}".format(r2_score(val, backtest[1:], intersect=False)))
        print("MAPE: {}".format(mape(val, backtest[1:])))
        print("MASE: {}".format(mase(val, backtest[1:], train)))
        print("MAE: {}".format(mae(val, backtest[1:])))
        val.plot(label="TEST")
        backtest.plot(label='backtest')
        ts.plot(label='actual')
        plt.legend()
        plt.show()
    else: 
        return [tcn_model, params]

def get_tcn_predictions(model):
    prediction = model.predict(7) #Predict a week ahead
    prediction_json = json.loads(prediction.to_json())
    dates = prediction_json['index']
    counts = prediction_json['data']
    prediction_dataset = to_dataset(dates, counts)
    logging.debug(prediction_dataset)
    return prediction_dataset

def eval_tcn_model(serialized_model, dataset):
    tcn_model = pickle.loads(serialized_model)
    df = pd.DataFrame.from_dict(dataset)
    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])
    train, val = ts.split_after(0.8) #80% train, 20% val
    backtest = tcn_model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            retrain=False,
    )
    scores = dict()
    scores['r2'] = r2_score(val, backtest[1:])
    scores['mase_score'] = mase(val, backtest[1:], train)
    scores['mae_score'] = mae(val, backtest[1:])
    try:
        scores['mape_score'] = mape(val, backtest[1:])
    except:
        scores['mape_score'] = "Could not be calculated (Zero value in time series)"
    return scores



def store_tcn_model(db, serialized_model = None, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.model_tcn = serialized_model
    else:
        logging.debug("what")
    db.session.commit()

def store_tcn_prediction(db, prediction = False, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.tcn_prediction = prediction
    else:
        logging.debug("what")
    db.session.commit()

def store_tcn_score(db, score = None, trend_type="category", id=12):
    if(trend_type=="category"):
        record = db.session.query(CategoryTrend).filter_by(category_id=id).first()
    elif(trend_type=="brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.tcn_metrics = score
    else:
        logging.debug("what")
    db.session.commit()

if __name__ == '__main__':
    print("hello")
    get_tcn_model(plot=True, verbose=True)