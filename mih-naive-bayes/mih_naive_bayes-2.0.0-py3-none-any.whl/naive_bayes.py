# encoding: utf-8

import itertools
import numpy   as np
import pandas  as pd
import _pickle as pickle

from collections import Counter
from progressbar import progressbar


class NaiveBayes(object):


    def __init__(self):

        self._logprior      = {}
        self._loglikelihood = None
        self._V             = None
        self._C             = None


    def flatten(self, l):

        return list(itertools.chain.from_iterable(l))


    def logprior(self, y):

        c = Counter(y)
        p = np.log2(list(c.values())) - np.log2(len(y))

        self._logprior = {list(c.keys())[i]:p[i] for i in range(len(list(c.keys())))}


    def V(self, X):

        D_flatten = self.flatten(X)
        self._V = np.unique(D_flatten)


    def cwords(self, X, y):
        """ make dict{c:[w]}
        """

        c_full = Counter(y)

        c_words = {i:[] for i in c_full.keys()}

        for i in range(len(y)):
            c_words[y[i]].append(X[i])

        for k, v in c_words.items():
            c_words[k] = self.flatten(v)

        return c_words, c_full


    def loglikelihood(self, X, y):

        c_words, c_full = self.cwords(X, y)

        # num of words in each class
        c_count = {k:len(v) for k, v in c_words.items()} 

        # each word counts in each class
        c_part = {c:Counter(c_words[c]) for c in c_full.keys()}

        # log likelihood
        len_V = len(self._V)

        self._loglikelihood = {c:{} for c in c_full.keys()}

        # for c, cnt in c_part.iteritems():
        for c, cnt in c_part.items():
            denominator = np.log2(c_count[c] + len_V)

            c_part_count = c_part[c]
            
            for w in c_part[c].keys():
                self._loglikelihood[c][w] = np.log2(c_part_count.get(w,0)+1.) - denominator

            for w in set(self._V)-set(c_part_count.keys()):
                self._loglikelihood[c][w] = -denominator



    def likelihood(self):

        return np.sum([list(v.values()) for v in self._loglikelihood.values()])



    def cunique(self, y):

        self._C = np.unique(y)


    def fit(self, X, y):

        self.logprior(y)
        self.V(X)
        self.loglikelihood(X, y)
        self.cunique(y)


    def predict(self, X):

        score = [[self._logprior.get(c,0) + sum([self._loglikelihood[c].get(w,0) for w in d]) for c in self._C] for d in progressbar(X)]
        idx   = np.argmax(score, axis=1)
        c     = self._C[idx].tolist()

        return c


    def save(self, fn):

        with open(fn, 'wb') as f:
            pickle.dump(self.__dict__, f)


    def load(self, fn):

        with open(fn, 'rb') as f:
            self.__dict__.update(pickle.load(f))
