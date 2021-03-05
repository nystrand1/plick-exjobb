import logging

def merge_datasets(dataset_1, dataset_2, key_name = "degree 1"):
    for (i, data) in enumerate(dataset_1):
        data['trends'][key_name] = dataset_2[i]
    
    return dataset_1

def merge_partial_dataset(dataset_1, dataset_2, key_name = "degree 1"):
    start_index = len(dataset_1) - len(dataset_2)
    logging.debug("START INDEX: {}".format(start_index))
    logging.debug("LENGTH DATASET 2: {}".format(len(dataset_2)))
    logging.debug("LENGTH DATASET 1: {}".format(len(dataset_1)))
    for (i,data) in enumerate(dataset_1[start_index:]):
        data['trends'][key_name] = dataset_2[i]
        start_index+=1
    
    return dataset_1