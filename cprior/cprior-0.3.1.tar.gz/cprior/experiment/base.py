"""
Bayesian A/B and MV testing experiment.
"""

# Guillermo Navas-Palencia <g.navas.palencia@gmail.com>
# Copyright (C) 2019

import time


_STATUS = []


class Experiment(object):
    def __init__(self, name, test, stopping_rule="expected_loss", epsilon=1e-5,
                 min_samples=None, max_samples=None, options=None,
                 verbose=True):

        self.name = name
        self.test = test
        self.stopping_rule = stopping_rule
        self.epsilon = epsilon
        self.min_samples = min_samples
        self.max_samples = max_samples
        self.options = options
        self.verbose = verbose

        # auxiliary data

        # statistics
        self._dict_measures = {}

        # running statistics (mean / variance)

        # timing

        # flags
        self._status = None
        self._termination = False

        # experiment setup
        self._setup()

    @abstractmethod
    def stats(self):
        pass

    def _setup(self):
        pass

    def _from_abtest(self):
        # transform abtest to standard experiment form
        pass

    def _from_mvtest(self):
        # transform mvtest to standard experiment form
        pass