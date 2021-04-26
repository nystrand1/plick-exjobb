import numpy as np
import pandas as pd
import json
import logging
import time
import pickle
import warnings
import matplotlib.pyplot as plt

from ...models.brand_trend import BrandTrend
from ...models.category_trend import CategoryTrend
from ...models.query_trend import QueryTrend
from ..utils.dataset import to_dataset


from darts import TimeSeries
from darts.models import RNNModel
from darts.dataprocessing.transformers import Scaler
from darts.utils.timeseries_generation import datetime_attribute_timeseries
from darts.metrics import *
from torch.nn import MSELoss, L1Loss


def get_lstm_model(dataset=None, plot=False, verbose=False):
    if(dataset is None):
        df = pd.read_csv("nike.csv")
    else:
        df = pd.DataFrame.from_dict(dataset)

    ts = TimeSeries.from_dataframe(
        df, time_col='time_interval', value_cols=['count'])

    train, val = ts.split_after(0.8)

    scaler = Scaler()
    train_transformed = scaler.fit_transform(train)
    val_transformed = scaler.transform(val)
    ts_transformed = scaler.transform(ts)

    params = dict()
    params['model'] = ["LSTM"]
    params['hidden_size'] = [50, 75, 100]
    params['n_rnn_layers'] = [1]
    params['input_chunk_length'] = [14]
    params['output_chunk_length'] = [7]
    params['n_epochs'] = [100]
    params['dropout'] = [0]
    params['batch_size'] = [4, 6, 8]
    params['random_state'] = [0, 1]
    params['loss_fn'] = [MSELoss()]

    lstm = RNNModel.gridsearch(
        parameters=params,
        series=train_transformed,
        val_series=val_transformed,
        verbose=verbose,
        metric=mse
    )

    params = lstm[1]
    lstm_model = lstm[0]

    lstm_model.fit(ts_transformed, verbose=True)

    if(plot):
        backtest = lstm_model.historical_forecasts(
            series=ts_transformed,
            start=0.8,
            forecast_horizon=1,
            stride=1,
            retrain=False,
            verbose=False
        )
        print(val)
        print(backtest[1:])
        print("R2: {}".format(r2_score(scaler.inverse_transform(
            val_transformed), scaler.inverse_transform(backtest[1:]), intersect=False)))
        print("MAPE: {}".format(
            mape(scaler.inverse_transform(val_transformed), scaler.inverse_transform(backtest[1:]))))
        print("MASE: {}".format(
            mase(scaler.inverse_transform(val_transformed), scaler.inverse_transform(backtest[1:]), train)))
        print("MAE: {}".format(
            mae(scaler.inverse_transform(val_transformed), scaler.inverse_transform(backtest[1:]))))
        scaler.inverse_transform(val_transformed).plot(label="TEST")
        scaler.inverse_transform(backtest).plot(label='backtest')
        scaler.inverse_transform(ts_transformed).plot(label='actual')
        print("FUTURE")
        print(scaler.inverse_transform(lstm_model.predict(7)))
        plt.legend()
        plt.show()
    else:
        return [lstm_model, params]

def get_lstm_predictions(model, dataset):
    df = pd.DataFrame.from_dict(dataset)
    
    ts = TimeSeries.from_dataframe(
        df, time_col='time_interval', value_cols=['count'])
    scaler = Scaler()
    train_transformed = scaler.fit_transform(ts)

    prediction = scaler.inverse_transform(model.predict(7)) #Predict a week ahead
    prediction_json = json.loads(prediction.to_json())
    dates = prediction_json['index']
    counts = prediction_json['data']
    prediction_dataset = to_dataset(dates, counts)
    logging.debug(prediction_dataset)
    return prediction_dataset

def eval_all_lstm_models(db, categories, brands, queries):
    scores = list() 
    for brand in brands:
        score = eval_lstm_model(brand['model_lstm'], brand['time_series_day'])
        score['topic'] = brand['brand_name']
        score['topic_id'] = brand['brand_id']
        store_lstm_score(db, score=score, trend_type="brand", id=brand['brand_id'])
        scores.append(score)

    for category in categories:
        score = eval_lstm_model(category['model_lstm'], category['time_series_day'])
        score['topic'] = category['category_name']
        score['topic_id'] = category['category_id']
        store_lstm_score(db, score=score, trend_type="category", id=category['category_id'])
        scores.append(score)

    for query in queries:
        score = eval_lstm_model(query['model_lstm'], query['time_series_day'])
        score['topic'] = query['query']
        score['topic_id'] = query['query']
        store_lstm_score(db, score=score, trend_type="query", id=query['query'])
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


def eval_lstm_model(serialized_model, dataset):
    lstm_model = pickle.loads(serialized_model)
    df = pd.DataFrame.from_dict(dataset)
    ts = TimeSeries.from_dataframe(
        df, time_col='time_interval', value_cols=['count'])
    train, val = ts.split_after(0.8)  # 80% train, 20% val
    scaler = Scaler()
    ts = scaler.fit_transform(ts)
    val_transformed = scaler.transform(val)
    train_transformed = scaler.transform(train)
    backtest = lstm_model.historical_forecasts(
        series=ts,
        start=0.8,
        forecast_horizon=1,
        stride=1,
        retrain=False,
    )
    scores = dict()
    scores['r2'] = r2_score(val_transformed, backtest[1:])
    scores['mase_score'] = mase(val_transformed, backtest[1:], train_transformed)
    scores['mae_score'] = mae(val_transformed, backtest[1:])
    try:
        scores['mape_score'] = mape(val_transformed, backtest[1:])
    except:
        scores['mape_score'] = "Could not be calculated (Zero value in time series)"
    return scores


def store_lstm_model(db, serialized_model, trend_type="category", id=12):
    if(trend_type == "category"):
        record = db.session.query(CategoryTrend).filter_by(
            category_id=id).first()
    elif(trend_type == "brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(BrandTrend).filter_by(query=id).first()
    if(record is not None):
        record.model_lstm = serialized_model
    else:
        logging.debug("what")
    db.session.commit()


def store_lstm_prediction(db, prediction=False, trend_type="category", id=12):
    if(trend_type == "category"):
        record = db.session.query(CategoryTrend).filter_by(
            category_id=id).first()
    elif(trend_type == "brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.lstm_prediction = prediction
    else:
        logging.debug("what")
    db.session.commit()


def store_lstm_score(db, score=None, trend_type="category", id=12):
    if(trend_type == "category"):
        record = db.session.query(CategoryTrend).filter_by(
            category_id=id).first()
    elif(trend_type == "brand"):
        record = db.session.query(BrandTrend).filter_by(brand_id=id).first()
    else:
        record = db.session.query(QueryTrend).filter_by(query=id).first()
    if(record is not None):
        record.lstm_metrics = score
    else:
        logging.debug("what")
    db.session.commit()


if __name__ == '__main__':
    print("hello")
    get_lstm_model(plot=True, verbose=True)
