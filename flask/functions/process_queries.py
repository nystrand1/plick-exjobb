import logging

from .query_filter import *
from .count_interval import *
from .regression.linear import *


def process_query(db, data, r, processed_queries):
    logging.debug(processed_queries)
    data['query'] = r['query']
    if data['query'] in processed_queries:
        logging.debug("WORD ALDREADY PROCESSED: {}".format(data['query']))
        return
    data['similar_queries'] = get_similar_words(db, data['query'])
    logging.debug("SIMILAR WORDS: {}".format(data['similar_queries']))
    data['trunc_by'] = "minute"
    time_series_min = count_interval_unique_similar(db, **data)
    data['trunc_by'] = "hour"
    time_series_hour = count_interval_unique_similar(db, **data)
    data['trunc_by'] = "day"
    time_series_day = count_interval_unique_similar(db, **data)
    data['trunc_by'] = "week"
    time_series_week = count_interval_unique_similar(db, **data)
    data['trunc_by'] = "month"
    time_series_month = count_interval_unique_similar(db, **data)
    datasets = split_dataset(time_series_day)
    linear_model_long = get_linear_model(datasets['long'])
    linear_model_mid = get_linear_model(datasets['mid'])
    linear_model_short = get_linear_model(datasets['short'])
    logging.debug("LONG MODEL: {}".format(linear_model_long))
    logging.debug("MID MODEL: {}".format(linear_model_mid))
    logging.debug("SHORT MODEL: {}".format(linear_model_short))
    processed_queries.extend(data['similar_queries'])
    try:
        data['similar_queries'].remove(data['query'])
    except:
        logging.debug("COULD NOT REMOVE: {}".format(data['query']))

    data_store = {
        'query': data['query'],
        'similar_queries': data['similar_queries'],
        'time_series_min': time_series_min,
        'time_series_hour': time_series_hour,
        'time_series_day': time_series_day,
        'time_series_week': time_series_week,
        'time_series_month': time_series_month,
        'model_short': linear_model_short,
        'model_mid': linear_model_mid,
        'model_long': linear_model_long,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }
    save_to_db(db, data_store)
    db.session.commit()