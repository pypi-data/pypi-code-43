# -*- coding: utf-8 -*-

import math
import numpy as np

from .base import Model
from scipy.special import logsumexp
# from scipy.stats import entropy

class MinDivModel(Model):
    """ MinDivModel Model. """

    def __init__(self,
                       feature_matrix,
                       mnz_method = 'CG',
                       mnz_tol = 1e-8,
                       mnz_options = {'maxiter': 1000, 'disp': False},
                       prior_log_pdf = None):
        super(MinDivModel, self).__init__(mnz_method = mnz_method,
                                          mnz_tol = mnz_tol,
                                          mnz_options = mnz_options)

        self.F = feature_matrix

        if isinstance(self.F, np.matrix):
            self.F = np.asarray(self.F)

        # allocate var self.prior_log_pdf
        self.priorlogprobs = None

    def log_norm_constant(self):
        """ calculates the log norm constant """

        # check if attr has been precomputed
        if hasattr(self, 'logZ'):
            return self.logZ

        #log_p_dot = self.F.T.dot(self.params)
        # log_p_dot = np.dot(self.F, self.params)
        log_p_dot = np.dot(self.params, self.F.T)

        if self.priorlogprobs is not None:
            log_p_dot += self.priorlogprobs

        self.logZ = logsumexp(log_p_dot)

        return self.logZ

    def expectations(self):

        p = self.probdist()
        # return self.F.dot(p)
        return np.dot(p, self.F)


    def log_probdist(self):

        #log_p_dot = self.F.T.dot(self.params)
        # log_p_dot = np.dot(self.F, self.params)
        log_p_dot = np.dot(self.params, self.F.T)

        if self.priorlogprobs is not None:
            log_p_dot += self.priorlogprobs

        if not hasattr(self, 'logZ'):
            self.logZ = logsumexp(log_p_dot)

        return log_p_dot - self.logZ

    def probdist(self):
        return np.exp(self.log_probdist())
