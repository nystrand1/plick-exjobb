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
    if(dataset is None):
        df = pd.read_csv("jeans_day.csv")
    else:
        df = pd.DataFrame.from_dict(dataset)
    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])

    train, val = ts.split_after(0.8) #80% train, 20% val

    scaler = Scaler()
    train_transformed = scaler.fit_transform(train)
    val_transformed = scaler.transform(val)
    ts_transformed = scaler.transform(ts)
    

    params = dict()
    params['kernel_size'] = [4, 6]
    params['num_filters'] = [10]
    params['random_state'] = [0, 1]
    params['input_chunk_length'] = [22, 27]
    params['output_chunk_length'] = [1]
    params['dilation_base'] = [2,3] 
    params['n_epochs'] = [100]
    params['dropout'] = [0]
    params['loss_fn'] = [MSELoss()]
    params['weight_norm'] = [True]
    tcn = TCNModel.gridsearch(
        parameters=params,
        series=train_transformed,
        val_series=val_transformed,
        verbose=verbose,
        metric=mse
    )

    params = tcn[1]
    tcn_model = tcn[0]
    tcn_model.fit(series=train_transformed)
    if(plot):
        backtest = tcn_model.historical_forecasts(
            series=ts_transformed,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            retrain=False,
            verbose=verbose
        )
        val = scaler.inverse_transform(val_transformed)
        backtest = scaler.inverse_transform(backtest)
        train = scaler.inverse_transform(train_transformed)
        print(scaler.inverse_transform(tcn_model.predict(7)))
        print("R2: {}".format(r2_score(val, backtest[1:], intersect=False)))
        print("MAPE: {}".format(mape(val, backtest[1:])))
        print("MASE: {}".format(mase(val, backtest[1:], train)))
        print("MAE: {}".format(mae(val, backtest[1:])))
        print("RMSE: {}".format(np.sqrt(mse(val, backtest[1:]))))
        backtest.plot(label='backtest')
        ts.plot(label='actual')
        plt.title("H&M Daily, TCN Model")
        plt.xlabel("Date")
        plt.ylabel("Count")
        plt.legend()
        plt.show()
    else: 
        return [tcn_model, params]

def get_tcn_predictions(model, dataset):
    df = pd.DataFrame.from_dict(dataset)
    
    ts = TimeSeries.from_dataframe(
        df, time_col='time_interval', value_cols=['count'])
    scaler = Scaler()
    ts = scaler.fit_transform(ts)
    model.fit(series=ts)
    prediction = scaler.inverse_transform(model.predict(7)) #Predict a week ahead
    prediction_json = json.loads(prediction.to_json())
    dates = prediction_json['index']
    counts = prediction_json['data']
    prediction_dataset = to_dataset(dates, counts)
    logging.debug(prediction_dataset)
    return prediction_dataset

def get_tcn_backtest(serialized_model, dataset, topic):
    df = pd.DataFrame.from_dict(dataset)
    
    ts = TimeSeries.from_dataframe(
        df, time_col='time_interval', value_cols=['count'])
    scaler = Scaler()
    ts = scaler.fit_transform(ts)

    model = pickle.loads(serialized_model)

    backtest = model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            retrain=False,
            verbose=False
    )
    backtest = scaler.inverse_transform(backtest)
    ts = scaler.inverse_transform(ts)
    ts.plot(label='Actual', lw=3)
    backtest.plot(label='TCN Model', lw=3)
    plt.title("{} Daily".format(topic))
    plt.xlabel("Date")
    plt.ylabel("Count")


def eval_all_tcn_models(db, categories, brands, queries, regenerate = False):
    scores = list() 

    for brand in brands:
        if 'tcn_metrics' in brand and regenerate is False:
            scores.append(brand['tcn_metrics'])
        else:
            score = eval_tcn_model(brand['model_tcn'], brand['time_series_day'])
            score['topic'] = brand['brand_name']
            score['topic_id'] = brand['brand_id']
            store_tcn_score(db, score=score, trend_type="brand", id=brand['brand_id'])
            scores.append(score)

    for category in categories:
        if 'tcn_metrics' in category and regenerate is False:
            scores.append(category['tcn_metrics'])
        else:
            score = eval_tcn_model(category['model_tcn'], category['time_series_day'])
            score['topic'] = category['category_name']
            score['topic_id'] = category['category_id']
            store_tcn_score(db, score=score, trend_type="category", id=category['category_id'])
            scores.append(score)

    for query in queries:
        if 'tcn_metrics' in query and regenerate is False:
            scores.append(query['tcn_metrics'])
        else:
            score = eval_tcn_model(query['model_tcn'], query['time_series_day'])
            score['topic'] = query['query']
            score['topic_id'] = query['query']
            store_tcn_score(db, score=score, trend_type="query", id=query['query'])
            scores.append(score)

    mean_scores = dict()

    mape_sum = 0
    mape_count = 0
    r2_sum = 0
    mase_sum = 0
    mae_sum = 0
    rmse_sum = 0

    for score in scores:
        try:
            mape_sum += float(score['mape_score'])
            mape_count += 1
        except:
            pass
        r2_sum += float(score['r2'])
        mase_sum += float(score['mase_score'])
        mae_sum += float(score['mae_score'])
        rmse_sum += float(score['rmse_score'])

    mean_scores['r2'] = r2_sum/len(scores)
    mean_scores['mape'] = mape_sum/mape_count
    mean_scores['mase'] = mase_sum/len(scores)
    mean_scores['mae'] = mae_sum/len(scores)
    mean_scores['rmse'] = rmse_sum/len(scores)
    mean_scores['mape_count'] = mape_count
    mean_scores['total'] = len(scores)

    return mean_scores

def eval_tcn_model(serialized_model, dataset):
    tcn_model = pickle.loads(serialized_model)
    df = pd.DataFrame.from_dict(dataset)
    ts = TimeSeries.from_dataframe(df, time_col='time_interval', value_cols=['count'])
    train, val = ts.split_after(0.8) #80% train, 20% val
    scaler = Scaler()
    ts = scaler.fit_transform(ts)
    val_transformed = scaler.transform(val)
    train_transformed = scaler.transform(train)
    backtest = tcn_model.historical_forecasts(
            series=ts,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            retrain=False,
    )

    val_transformed = scaler.inverse_transform(val_transformed)
    backtest = scaler.inverse_transform(backtest)
    train_transformed = scaler.inverse_transform(train_transformed)
    scores = dict()
    scores['r2'] = r2_score(val_transformed, backtest[1:])
    scores['mase_score'] = mase(val_transformed, backtest[1:], train_transformed)
    scores['mae_score'] = mae(val_transformed, backtest[1:])
    scores['rmse_score'] = np.sqrt(mse(val_transformed, backtest[1:]))
    try:
        scores['mape_score'] = mape(val_transformed, backtest[1:])
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