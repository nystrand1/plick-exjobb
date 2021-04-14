import logging
import math
from datetime import datetime, timedelta

def merge_datasets(dataset_1, dataset_2, key_name = "degree 1"):
    for (i, data) in enumerate(dataset_1):
        if(math.isnan(dataset_2[i])):
            continue
        else:
            data['trends'][key_name] = dataset_2[i]
    
    return dataset_1

def merge_partial_dataset(dataset_1, dataset_2, key_name = "degree 1"):
    start_index = len(dataset_1) - len(dataset_2)
    logging.debug("START INDEX: {}".format(start_index))
    logging.debug("LENGTH DATASET 2: {}".format(len(dataset_2)))
    logging.debug("LENGTH DATASET 1: {}".format(len(dataset_1)))
    for (i,data) in enumerate(dataset_1[start_index:]):
        if(math.isnan(dataset_2[i])):
            continue
        else:
            data['trends'][key_name] = dataset_2[i]
        start_index+=1
    return dataset_1

def split_dataset(dataset):
    latest_date = datetime.strptime(dataset[-1]['time_interval'], '%Y-%m-%d %H:%M:%S')
    mid_date = latest_date - timedelta(days=31)
    mid_date = datetime.strftime(mid_date, '%Y-%m-%d %H:%M:%S')
    logging.debug(mid_date)
    logging.debug(latest_date)
    logging.debug(dataset)
    mid_index = [(index, d) for index, d in enumerate(dataset) if d['time_interval'] ==  mid_date][0][0]
    logging.debug(mid_index)
    short_date = latest_date - timedelta(days=7)
    short_date = datetime.strftime(short_date, '%Y-%m-%d %H:%M:%S')
    short_index = [(index, d) for index, d in enumerate(dataset) if d['time_interval'] ==  short_date][0][0]
    res = dict()
    res['long'] = dataset
    res['mid'] = dataset[mid_index:]
    res['short'] = dataset[short_index:]
    return res