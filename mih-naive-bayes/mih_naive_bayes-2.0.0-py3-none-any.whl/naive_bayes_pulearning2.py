# encoding: utf-8

import itertools
import numpy  as np
import pandas as pd

from collections  import Counter
# @deprecated
from naive_bayes import NaiveBayes
# from .naive_bayes import NaiveBayes


class NaiveBayesPULearning2(NaiveBayes):



    def new_logprior(self, C1, C2, plambda):

        c1 = Counter(C1)
        c2 = Counter(C2)

        denominator = np.log2(len(C1) + plambda*len(C2))

        for k in (set(c1.keys())|set(c2.keys())):
            self._logprior[k] = np.log2(c1.get(k,0) + plambda*c2.get(k,0)) - denominator



    def new_V(self, D1, D2):
        
        self.V(D1+D2)



    def new_loglikelihood(self, D1, D2, C1, C2, plambda):

        c_words1, c_full1 = self.cwords(D1, C1)
        c_words2, c_full2 = self.cwords(D2, C2)

        # @deprecated
        # c_count1 = {k:len(v) for k, v in c_words1.iteritems()}
        # c_count2 = {k:len(v) for k, v in c_words2.iteritems()}
        c_count1 = {k:len(v) for k, v in c_words1.items()}
        c_count2 = {k:len(v) for k, v in c_words2.items()}

        c_part1  = {c:Counter(c_words1[c]) for c in c_full1.keys()}
        c_part2  = {c:Counter(c_words2[c]) for c in c_full2.keys()}

        # log likelihood
        len_V = len(self._V)

        c_full = set(c_full1.keys()) | set(c_full2.keys())

        self._loglikelihood = {c:{} for c in c_full}

        for c in c_full:
            denominator = np.log2(c_count1.get(c,0) + plambda*c_count2.get(c,0) + len_V)
            c_part1_count = c_part1.get(c, {})
            c_part2_count = c_part2.get(c, {})

            w_full = set(c_part1_count.keys()) | set(c_part2_count.keys())
            w_rest = set(self._V) - w_full
            for w in w_full:
                self._loglikelihood[c][w] = np.log2(\
                                                        c_part1_count.get(w,0) +\
                                              plambda * c_part2_count.get(w,0) + 1.)\
                                              - denominator


            for w in w_rest:
                self._loglikelihood[c][w] = -denominator



    def new_cunique(self, C1, C2):

        self.cunique(C1+C2)



    def new_fit(self, D1, D2, C1, C2, plambda):

        self.new_logprior(C1, C2, plambda)
        self.new_V(D1, D2)
        self.new_loglikelihood(D1, D2, C1, C2, plambda)
        self.new_cunique(C1, C2)



    def run(self, D1, D2, C1, plambda=1, n_iterations=1, threshold=None):

        self.fit(D1, C1)
        C2 = self.predict(D2)

        llds = []
        lld  = self.likelihood()
        llds.append(lld)
        delta_likelihood = threshold

        while(True):

            if not n_iterations:
                break

            if threshold:
                if threshold > delta_likelihood:
                    break

            self.new_fit(D1, D2, C1, C2, plambda)
            C2 = self.predict(D2)

            delta_likelihood = self.likelihood() - lld
            lld = self.likelihood()
            llds.append(lld)

            n_iterations -= 1

        return llds
