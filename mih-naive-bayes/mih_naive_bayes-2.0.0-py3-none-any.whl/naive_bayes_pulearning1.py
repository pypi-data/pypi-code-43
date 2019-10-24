# encoding: utf-8

import numpy as np

# @deprecated
from naive_bayes import NaiveBayes
# from .naive_bayes import NaiveBayes


class NaiveBayesPULearning1(NaiveBayes):


    """ Training with Unlabeled data
    """


    def run(self, D1, D2, C1, n_iterations=1, threshold=None):
        """
        Parameters
        ----------
        D1 : list 
            labeled

        D2 : list 
            unlabeled

        C1 : list
            classes of D1
        """

        super(NaiveBayesPULearning1, self).fit(D1, C1)
        C2 = super(NaiveBayesPULearning1, self).predict(D2)

        D12 = D1 + D2
        C12 = C1 + C2

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

            super(NaiveBayesPULearning1, self).fit(D12, C12)
            C12 = super(NaiveBayesPULearning1, self).predict(D12)

            delta_likelihood = self.likelihood() - lld
            lld = self.likelihood()
            llds.append(lld)

            n_iterations -= 1

        return C12, llds
