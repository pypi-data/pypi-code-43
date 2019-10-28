# -*- coding: utf-8 -*-
import os

import numpy as np
from sklearn.preprocessing import LabelEncoder

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


PAD = '[PAD]'
SOS = '[CLS]'
EOS = '[SEP]'
UNK = '[UNK]'


class Label:
    def __init__(self):
        pass

    def fit(self, y):
        # label = LabelEncoder()
        tags = []
        for yy in y:
            tags += yy
        tags = sorted(set(tags))
        # label.fit([PAD, SOS, EOS] + tags)
        # self.label = label
        self.classes = [PAD, SOS, EOS] + tags
        self.tag_index = {}
        for i, t in enumerate(self.classes):
            self.tag_index[t] = i
        self.index_tag = {
            v: k
            for k, v in self.tag_index.items()
        }
        self.label_size = len(self.classes)

    def transform(self, y):
        max_length = int(np.max([len(yy) for yy in y])) + 2
        ret = []
        for yy in y:
            vec = [self.tag_index[SOS]]
            for yyy in yy:
                vec.append(self.tag_index[yyy])
            vec.append(self.tag_index[EOS])
            if len(vec) < max_length:
                vec += [self.tag_index[PAD]] * (max_length - len(vec))
            ret.append(vec)
        return np.array(ret)

    def inverse_transform(self, y):
        # import pdb; pdb.set_trace()
        return [
            [
                self.index_tag[yyy] if yyy in self.index_tag else UNK
                for yyy in yy
            ]
            for yy in y
        ]