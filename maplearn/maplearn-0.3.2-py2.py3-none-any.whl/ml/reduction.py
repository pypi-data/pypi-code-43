# -*- coding: utf-8 -*-
"""
**Reduction of dimensions**


The number of dimensions are reduced by selecting some of the features (like in
kbest approach) or transforming them (like in PCA...). This reduction is
applied to samples and the data to predict in further step.

Several approaches are available, which are listed in the class attribute
"ALG_ALGOS".


"""
from __future__ import print_function
import os

import numpy as np
import pandas as pd

from maplearn.app.reporting import icon_msg
from maplearn.ml.machine import Machine
from maplearn.ml.algos_reduction import ALGOS
from maplearn.datahandler.plotter import Plotter

from maplearn import logger


pd.set_option('display.precision', 2)
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 700)

class Reduction(Machine):
    """
    This class reduces the number of dimensions by selecting some of the features
    or transforming them (like in PCA...). This reduction is applied to samples
    and the data to predict in further step.

    Args:
        * data (PackData): dataset to reduced
        * algorithm (list): list of algorithm(s) to apply on dataset
        * **kwargs: parameters about the reduction (numberof components) or the
          dataset (like features)

    Attributes:
        * attributes inherited from Machine classe
        * ncomp (int): number of components expected
    """

    def __init__(self, data=None, algorithm=None, **kwargs):

        Machine.ALL_ALGOS = ALGOS

        self.ncomp = 1  # nombre de dimensions souhaitees
        if 'features' in kwargs:
            self.__features = kwargs['features']
        else:
            self.__features = None

        Machine.__init__(self, algorithm=algorithm, data=data, **kwargs)
        if 'ncomp' in kwargs:
            self.__nb_comp(kwargs['ncomp'])

        self.algorithm = algorithm
        self.result = dict()

    def load(self, data):
        """
        Loads dataset to reduce

        Args:
            * data (PackData): dataset to load
        """
        Machine.load(self, data)
        if self._data.Y is None:
            if self.algorithm in ['lda', 'rfe']:
                raise TypeError('%s algorithm needs samples. y is missing.',
                                self.algorithm)
            else:
                logger.warning('No samples specified')
        if self._data.data is None:
            self._data.data = self._data.X
        self.__check()

        if self.__features is None:
            if self._data.X is not None:
                last_col = self._data.X.shape[1] + 1
            else:
                last_col = self._data.data.shape[1] + 1
            features = range(1, last_col)
            self.__features = [str(i) for i in features]

    def __check(self):
        """
        Chekc if the dataset is compatible with reduction
        """
        if not isinstance(self._data.data, np.ndarray):
            raise TypeError("Data is expected to be an array")

        elif self._data.data.ndim != 2:
            raise IndexError("Dataset should be 2D (%i dimensions found"
                             % self._data.data.ndim)
        elif self._data.data.shape[1] < self.ncomp:
            str_msg = "Dataset does not contain enough features (%i <= %i)" \
                      % (self._data.data.shape[1], self.ncomp)
            icon_msg(str_msg, "error")
            logger.critical(str_msg)
            raise IndexError(str_msg)
        else:
            logger.debug('Dataset ready to be reduced')

        if self._data.X is None or self._data.Y is None:
            logger.warning("X ou Y non renseigné => seront ignorés")
            self._data.X = None
            self._data.Y = None

        if self._data.X is not None:
            if self._data.X.ndim != self._data.data.ndim:
                raise IndexError("X and data have different number of \
                                 dimensions: %i vs. %i", self._data.X.ndim,
                                 self._data.data.ndim)
            elif self._data.X.shape[1] != self._data.data.shape[1]:
                raise IndexError("X & data have different number of features:\
                                 %i vs. %i", self._data.X.shape[1],
                                 self._data.data.shape[1])
        if self._data.Y is not None:
            if self._data.Y.ndim != 1:
                raise TypeError("Y should be a vector (containing labels")
            elif self._data.Y.shape[0] != self._data.X.shape[0]:
                raise IndexError("Y and X have different number of \
                                 individuals: %i vs. %i",
                                 self._data.Y.shape[0],
                                 self._data.X.shape[0])

    def __nb_comp(self, n_feat):
        """
        Guess the number of dimensions that could be expected after reduction,
        if the user does not mention it.

        Args:
            * n_feat (int or None): number of features expected or None if it
              should be guessed

        Returns:
            int: the number of features expected
        """
        if n_feat is not None:
            self.ncomp = n_feat
        elif self._data.Y is not None:
            ncomp = len(np.unique(self._data.Y)) - 1  # nb. de dimensions a conserver
            if ncomp < self.ncomp:
                ncomp = self.ncomp  # au moins nMin dimensions
        else:
            logger.warning('No information about number of components')

        # application de l'objectif [nombre de dimensions]
        if self.ncomp is not None:
            logger.info('Purpose : reducing to %i dimension(s)', self.ncomp)
            for i in ('k', 'n_features_to_select', 'n_components'):
                Machine._params[i] = self.ncomp
        return self.ncomp

    def fit_1(self, algo):
        """
        Fits one reduction algorithm to the dataset

        Args:
            * algo (str): name of the algorithm to fit
        """
        Machine.fit_1(self, algo)
        self.result['data'] = None
        self.result['X'] = None

        # algorithm(s) that need samples to fit
        lst_algos = ('kbest', 'kbest_chi2', 'lda', 'rfe', 'kernel_pca')
        if self._data.X is None or self._data.Y is None:
            if algo in lst_algos:
                str_msg = "%s Reduction needs samples" % algo
                logger.error(str_msg)
                return None

        # fitting
        if algo in lst_algos:
            try:
                self.algo.fit(self._data.X, self._data.Y)
            except ValueError as error:
                print(icon_msg(error, nature="error"))
                logger.critical(error)
                raise ValueError(error)
        elif algo == 'pca':
            self.algo.fit(self._data.data)
        self._fitted = True

    def predict_1(self, algo):
        """
        Applies chosen way of reduction to the dataset

        Args:
            algo (str): name of the algorithm to apply
        """
        print('\n#### Reduction a %i dimension(s)####' % self.ncomp)
        Machine.predict_1(self, algo)
        
        if hasattr(self.algo, 'get_support'):
            # select features to keep
            self.scores = pd.DataFrame({'Features':self.__features})
            self.__features = [self.__features[c] for c in
                               self.algo.get_support(True)]
            self.result['data'] = self._data.data[:, self.algo.get_support(True)]
            self.result['X'] = self._data.X[:, self.algo.get_support(True)]
        elif hasattr(self.algo, 'transform'):
            # Dimensionnality reduction -> using features transformation
            if self._data.X is not None:
                self.result['X'] = self.algo.transform(self._data.X)
            self.result['data'] = self.algo.transform(self._data.data)
            self.__features = [algo + str(i+1) for i in range(self.ncomp)]
            self.scores = pd.DataFrame({'Features':self.__features})
        else:
            logger.error('Unknow way to reduce dimension')
            return None
        
        # compute scores
        __output = ["scores_", "ranking_", "pvalues_", "support_",
                    "explained_variance_ratio_", "grid_scores_"]
        for i in __output:
            if hasattr(self.algo, i):
                col = i.replace('_', ' ').strip().capitalize()
                __score = getattr(self.algo, i)
                try:
                    self.scores[col] = __score
                except:
                    logger.debug('Unable to get scores: expecting %i - got %i',
                                 self.scores.shape[1], len(__score))
        self.scores.to_csv(os.path.join(self.dir_out, 'results',
                                            'reduction_%s.csv' % algo))
        # sort features (more important -> less important)
        __impce = {'Scores':False, 'Ranking':True}
        for k, v in __impce.items():
            if k in self.scores.columns:
                try:
                    self.scores.sort_values(by=k, ascending=v,
                                            inplace=True)
                except AttributeError:
                    #PATCH: deal with pandas version < 17
                    self.scores.sort(k, ascending=v, inplace=True)
            break # one column used to sort scores => done
        str_msg = 'Dimensions reduites de %i => %i' \
                  % (self._data.data.shape[1], self.result['data'].shape[1])
        logger.info(str_msg)
        print(icon_msg(str_msg))
        print(self.__print(algo))

    def run(self, predict=True, ncomp=None):
        """
        Executes reduction of dimensions (fits and applies)

        Args:
            * predict (bool): should apply the reduction or just fit the
                              algorithm ?
            * ncomp (int): number of dimensions expected

        Returns:
            * array: reduced features data
            * array: reduced samples features
            * list: liste of features
        """
        if ncomp is not None:
            self.__nb_comp(ncomp)
        Machine.run(self, predict)
        return(self.result['data'], self.result['X'], self.__features)

    def __print(self, algo):
        """
        Textual display of the resulting reduction

        Args:
            * algo (str): name of the algorithm applied
        """
        str_msg = '<pre>%s</pre>' % str(self.scores)
        __plt = Plotter(self.dir_out)
        for i in ['Scores', 'Ranking', 'Explained variance ratio']:
            if i in self.scores.columns:
                str_msg += __plt.barplot(y=i, x='Features', data=self.scores,
                                         file='reduction_%s.png' % algo)
                break # scores are plotted => done
        
        if algo == 'rfecv':
            logger.info("Optimal number of features : %d" % \
                        self.algo.n_features_)
            self.__nb_comp(self.algo.n_features_)
            __df = pd.DataFrame(self.scores['Grid scores'])
            __df['Nb features'] = range(1, self.scores.shape[0] + 1)
            str_msg += __plt.factorplot(data=__df, x="Nb features",
                                        y="Grid scores",
                                        file="feature_imptce_%s.png" % algo)
        __plt = None
        return str_msg