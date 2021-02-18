
def merge_datasets(dataset_1, dataset_2, key_name = "degree 1"):
    for (i, data) in enumerate(dataset_1):
        data['trends'][key_name] = dataset_2[i]
    
    return dataset_1