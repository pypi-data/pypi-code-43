# encoding: utf-8

import numpy as np

# @deprecated
from naive_bayes import NaiveBayes
# from .naive_bayes import NaiveBayes


class BinaryNaiveBayes(NaiveBayes):


    def __init__(self):
        super(BinaryNaiveBayes, self).__init__()


    def fit(self, D, C):

        D = [np.unique(d) for d in D]
        super(BinaryNaiveBayes, self).fit(D, C)


    def predict(self, d):

        d = np.unique(d)
        return super(BinaryNaiveBayes, self).predict(d)
