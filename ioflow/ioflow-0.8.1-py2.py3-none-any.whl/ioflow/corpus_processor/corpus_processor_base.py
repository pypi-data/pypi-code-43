import numpy as np
from sklearn.model_selection import train_test_split

from tokenizer_tools.tagset.offset.sequence import Sequence
from typing import List


class CorpusProcessorBase(object):
    EVAL = 'eval'
    TRAIN = 'train'

    def __init__(self, config):
        self.config = config
        self.dataset_mapping = {}
        self.meta_info = {"tags": None, "labels": None}

    def prepare(self):
        raise NotImplementedError

    def train_test_split(self, *args, **kwargs):
        # go to https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
        # for *args and **kwargs
        return train_test_split(*args, **kwargs)

    def get_generator_func(self, data_set):
        return self.dataset_mapping[data_set]

    def get_meta_info(self):
        return self.meta_info

    def collect_tags(self, corpus_list: List[Sequence]):
        tag_list = []
        for corpus in corpus_list:
            for span in corpus.span_set:
                tag_list.append(span.entity)

        return set(tag_list)

    def collect_labels(self, corpus_list):
        label_list = [i.label for i in corpus_list]

        return set(label_list)
