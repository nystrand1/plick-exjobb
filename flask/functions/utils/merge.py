
def merge_datasets(dataset_1, dataset_2, key_name = "trend"):
    for (i, data) in enumerate(dataset_1):
        data[key_name] = dataset_2[i]
    
    return dataset_1