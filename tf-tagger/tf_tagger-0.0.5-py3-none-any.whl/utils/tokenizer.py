import os

import numpy as np
import tensorflow as tf

from .label import PAD, SOS, EOS, UNK

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class Tokenizer:
    def __init__(self):
        self.word_index = {
            PAD: 0,
            UNK: 1,
            SOS: 2,
            EOS: 3
        }

    def fit(self, X):
        for sent in X:
            for word in sent:
                if word not in self.word_index:
                    self.word_index[word] = len(self.word_index)
        self.vocab_size = len(self.word_index)
        self.index_word = {v: k for k, v in self.word_index.items()}

    def inverse_transform(self, X):
        ret = []
        for sent in X:
            words = []
            for w in sent:
                if w <= 0:
                    break
                if w in self.index_word:
                    words.append(self.index_word[w])
            ret.append(words)
        return ret

    def transform(self, X):
        max_length = max([len(x) for x in X]) + 2
        ret = []
        for sent in X:
            vec = []
            vec.append(self.word_index[SOS])
            for word in sent:
                if word in self.word_index:
                    vec.append(self.word_index[word])
                else:
                    vec.append(self.word_index[UNK])
            vec.append(self.word_index[EOS])
            if len(vec) < max_length:
                vec = vec + [self.word_index[PAD]] * (max_length - len(vec))
            ret.append(vec)
        return np.array(ret, dtype=np.int32)
