# -*- coding: utf-8 -*-
"""
*Machine Learning class*

Fits and predict result using one or several machine learning algorithm(s).

*This is an abstract class that should not be used directly*. Use instead one
one of the these classes:

    * **Classification**: supervised classification
    * **Clustering**: unsupervised classification
    * **Regression**: regression
    * **Reduction**: to reduce dimensions of a dataset
"""
from __future__ import print_function
import os
import numpy as np
import pandas as pd

from maplearn.app.reporting import icon_msg

from maplearn import logger


class Machine(object):
    """
    Class to apply one or several machine learning algorithm(s) on a given
    dataset.

    Args:

        * data (PackData): data to use with machine learning algorithm(s)
        * algorithm (list or str): algorithm(s) to use

    Attributes:

        * algo (str): key code of the currently used algorithm
        * result (dataframe): result(s) predicted by algorithm(s)
        * proba (dataframe): probabilities produced by some algorithm(s)

    Properties:

        * algorithm (list): machine learning algorithm(s) to use
    """
    ALL_ALGOS = dict()
    # Parametres lies a performance
    # Cache size = taille en RAM dispo (en Mo)
    # N_JOBS : nombre de processeurs à utiliser (-1 = tous)
    _params = {'cache_size': 24000000, 'n_jobs': -1}

    def __init__(self, data=None, algorithm=None, **kwargs):
        self._algorithm = dict()  # algorithms to use
        self.algo = None  # the current algorithm
        self._data = None  # (pack)data to use
        self._fitted = False
        self._na = np.nan
        self.result = pd.DataFrame() # output predictions
        self.proba = pd.DataFrame()  # probabilities
        self.scores = None
        # dossier en sortie
        if 'dirOut' not in kwargs or kwargs['dirOut'] is None:
            self.dir_out = os.getcwd()
            logger.warning('Output folder not mentionned => %s will be used',
                           self.dir_out)
        else:
            self.dir_out = kwargs['dirOut']
        if not os.path.exists(self.dir_out):
            os.makedirs(self.dir_out)
            logger.info('Folder %s missing => created', self.dir_out)
        # Creating a subdirectory for results
        if not os.path.exists(os.path.join(self.dir_out, 'results')):
            os.mkdir(os.path.join(self.dir_out, 'results'))
            logger.info('Create a subfolder "results" in %s', self.dir_out)

        # chargement des données
        if data is not None:
            self.load(data)
        if 'na' in kwargs:
            self._na = kwargs['na']

    @property
    def algorithm(self):
        """
        Gets list of algorithm that will be used when running the class
        """
        return [i for i in self._algorithm.keys()]

    @algorithm.setter
    def algorithm(self, algorithm):
        """
        Sets the list of algorithm(s) that will be used when running the class

        Args:

            * algorithm (list or str): algorithm(s) to use when running
        """
        if Machine.ALL_ALGOS is None or len(Machine.ALL_ALGOS) < 1:
            raise KeyError('No algorithm available')
        if isinstance(algorithm, (str, type(u""))):
            algorithm = [algorithm, ]
        if algorithm is None or len(algorithm) == 0:
            self._algorithm = Machine.ALL_ALGOS
            self.__set_params()
            return None
        try:
            self._algorithm = {k: Machine.ALL_ALGOS[k] for k in algorithm}
        except KeyError:
            str_msg = 'Unknown algorithm(s) in :'
            str_msg += ','.join(algorithm)
            logger.critical(str_msg)
            raise KeyError(str_msg)
        logger.info('%i algorithm(s) set', len(self._algorithm))
        self.__set_params()

    def _check(self):
        """
        Check that given data and parameters are correct
        """
        logger.debug('Checking...')

    def __set_params(self):
        """
        Apply parameters to an algorithm
        """
        for i in self.algorithm:
            params = {k: Machine._params[k] for k in Machine._params.keys()
                      if k in self._algorithm[i].get_params()}
            if len(params) > 0:
                logger.debug('"%i" parameters to change in %s', len(params), i)
                self._algorithm[i].set_params(**params)
        logger.debug('Performance parameters applied')

    def predict_1(self, algo, export=False):
        """
        Predict a result using a given algorithm

        Args:

            * algo (str): key name identifying the algorithm to use
            * export (bool): should the algorithm be used to predict results
        """
        self.__apply_1(algo)
        if export and self.dir_out is None:
            logger.error('EXPORT: missing output folder')
            export = False

        if not self._fitted:
            logger.warning("Algorithm %s not trained yet", algo)
            self.fit_1(algo)
            if not self._fitted:
                logger.error("Algorithm %s can't be trained", algo)
                return None
        logger.info('Predicting using %s', algo)

    def fit_1(self, algo):
        """
        Fits an algorithm to dataset
        """
        self._fitted = False
        self.__apply_1(algo)
        logger.info("Fitting algorithm %s", algo)

    def __apply_1(self, algo):
        """
        Use an algorithm
        """
        if algo not in self._algorithm.keys():
            raise Exception('Unknown algorithm : %s' % algo)
        self.algo = self._algorithm[algo]

    def load(self, data):
        """
        Loads necessary data to machine learning algorithm(s)

        Args:

            * data (PackData): dataset used by machine learning algorithm(s)
        """
        logger.debug('Loading data for processing...')
        """
        # TODO comment tester qu'il s'agit bien d'un packdata ?
        if not isinstance(data, PackData):
            logger.critical('Expecting a Packdata')
        """
        if hasattr(data, 'X') and hasattr(data, 'Y') and hasattr(data, 'data'):
            self._data = data
        else:
            raise TypeError('Assuming a packdata to process')
        logger.info('Data loaded for processing')
        self._check()

    def run(self, predict=False):
        """
        Apply machine learning task(s) using every specified algorithm(s)

        Args:

            * predict (boolean): should machine learning algorithm(s) be used
              to predict results (or just be fitted to samples) ?
        """
        print(self)
        for name in self._algorithm.keys():
            self.fit_1(name)
            if self._fitted and predict:
                self.predict_1(name)
        print('\n##Comparaison de(s) %i algorithme(s)##'
              % len(self._algorithm))

    def __str__(self):
        msg = '\n### Liste de(s) algorithme(s) ###'
        msg += icon_msg("Plus d'informations sur les algorithmes et les \
                        parametres sont disponibles sur le site de\
                        [scikit-learn](http://www.scikit-learn.org/stable/)")
        for k in self._algorithm:
            msg += '\n* **%s** : *%s*' % (k, self._algorithm[k])
        msg += '\n'
        return msg
