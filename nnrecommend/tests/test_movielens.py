
import os
import numpy as np
from nnrecommend.dataset import Dataset
import pandas as pd


DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../datasets/ml-dataset-splitted/movielens")


def test_dataset():
    dataset = Dataset(pd.read_csv(f"{DATASET_PATH}.train.rating", sep='\t', header=None))
    iddiff = dataset.normalize_ids()
    matrix = dataset.create_adjacency_matrix()
    dataset.add_negative_sampling(matrix, 4)
    testset = Dataset(pd.read_csv(f"{DATASET_PATH}.test.rating", sep='\t', header=None))
    testset.normalize_ids(iddiff)
    testset.add_negative_sampling(matrix, 99)

    assert len(dataset) == 5*99057
    assert (dataset.idrange == (943, 2625)).all()
    assert matrix.shape == (2625, 2625)
    assert len(testset) == 943*100
    assert (testset.idrange == (943, 2595)).all()
    assert (dataset[50*5] == (0, 113+943, 1, 875072173)).all()
    assert (dataset[90000*5] == (861, 1008+943, 1, 879303622)).all()
    assert (testset[500*100] == (500, 1949, 1, 883995203)).all()
