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
    dataset = count_interval_unique_similar(db, **data)
    datasets = split_dataset(dataset)
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
    save_to_db(db, data['query'], linear_model_short, linear_model_mid, linear_model_long, data['similar_queries'])