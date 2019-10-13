import pickle
from gensim import models


def load_pickle(file_path):
    with open(file_path, 'rb') as fp:
        return pickle.load(fp)


def load_pickled_w2v_embeddings(file_path) -> models.keyedvectors.Word2VecKeyedVectors:
    with open(file_path, 'rb') as fp:
        return pickle.load(fp)
