# -*- coding: utf-8 -*-

import numpy as np

from scipy import optimize
from abc import ABC, abstractmethod

class Model(ABC):

    def __init__(self, mnz_method='CG', mnz_tol = 1e-8, mnz_options = {'maxiter': 1000, 'disp': False}):

        # ensure that key optimizer_name is present
        if 'maxiter' and 'disp' not in mnz_options:
            raise Exception('mnz_options must be include in the maxiter and disp variables')

        allowed_options = {
            'eta',
            'eps',
            'func',
            'xtol',
            'ftol',
            'gtol',
            'disp',
            'norm',
            'maxls',
            'scale',
            'catol',
            'direc',
            'xatol',
            'fatol',
            'offset',
            'stepmx',
            'rhobeg',
            'minfev',
            'maxfev',
            'maxcor',
            'maxfun',
            'iprint',
            'rescale',
            'maxiter',
            'maxCGit',
            'accuracy',
            'adaptive',
            'mesg_num',
            'return_all',
            'initial_simplex',
            'max_trust_radius',
            'initial_trust_radius'
        }

        for kwrd in mnz_options:
            if kwrd not in allowed_options:
                raise TypeError('Unexpected keyword argument passed as minimizer options: ' + str(kwrd))

        self.computed_duals = {}
        self.computed_gradnorms = {}

        self.minimizer_tol = mnz_tol
        self.minimizer_method = mnz_method
        self.minimizer_options = mnz_options


    def fit(self, feature_expectations):
        """
        Fits the model subject to constraints E[f(x)] = sum(x_i * p_x) = y

        Args:
            feature_matrix (numpy.array): feature matrix
            feature_expectations (numpy.array): the target constraints with shape [1, num features]

        Returns:
            self
        """

        feature_expectations = np.atleast_2d(feature_expectations)[0]
        assert feature_expectations.ndim == 1

        self.Y = feature_expectations

        # 1. check features

        # 2. sanity checks for the params

        self.setparams(np.zeros(len(feature_expectations), float))

        old_params = np.array(self.params)

        callback = self.log

        opt_result = optimize.minimize(self.dual,
                                                  old_params,
                                                  args=(),
                                                  method=self.minimizer_method,
                                                  jac=self.grad,
                                                  tol=self.minimizer_tol,
                                                  callback=callback,
                                                  options=self.minimizer_options)

        new_params = opt_result.x
        num_evals  = opt_result.nfev

        # print(new_params)
        if np.any(self.params != new_params):
            self.setparams(new_params)
        self.num_evals = num_evals

        return self

    def dual(self, params=None):

        L = self.log_norm_constant() - np.dot(self.params, self.Y)

        return L

    def log(self): pass

    @abstractmethod
    def log_norm_constant(self):
        """ Implemented by subclasses """
        raise NotImplementedError

    def norm_constant(self):
        """ normalization constant """
        return np.exp(self.log_norm_constant())


    def grad(self, params):
        """ estimate the gradients """
        G = self.expectations() - self.Y

        return G

    @abstractmethod
    def expectations(self):
        """ Implemented by subclasses """
        raise NotImplementedError

    def setparams(self, params):
        self.params = np.array(params, float)

        self.clearcache()

    def clearcache(self):
        for var in ['mu', 'logZ', 'logv']:
            if hasattr(self, var):
                delattr(self, var)
