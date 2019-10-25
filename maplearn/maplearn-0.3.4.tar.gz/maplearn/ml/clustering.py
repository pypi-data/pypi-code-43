# -*- coding: utf-8 -*-
"""

**Clustering: unsupervised classification**

A clustering algorithm groups the given samples, each represented as a vector x
in the N-dimensional feature space, into a set of clusters according to their
spatial distribution in the N-D space. Clustering is an unsupervised
classification as no a priori knowledge (such as samples of known classes) is
assumed to be available.

Clustering is unsupervised and does not need samples for fitting. The output
will be a matrix with integer values.

Example:
    >>> from maplearn.datahandler.loader import Loader
    >>> from maplearn.datahandler.packdata import PackData
    >>> loader = Loader('iris')
    >>> data = PackData(X=loader.X, Y=loader.Y, data=loader.aData)
    >>> lst_algos = ['knn', 'lda', 'rforest']
    >>> dir_out = os.path.join('maplean_path', 'tmp')
    >>> cls = Clustering(data=data, dirOut=dir_out, algorithm='mkmeans')
    >>> cls.run()
"""

from __future__ import print_function

import numpy as np
import pandas as pd


from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph

from maplearn.ml.machine import Machine
from maplearn.ml.algos_clustering import ALGOS
from maplearn import logger


class Clustering(Machine):
    '''
    Apply one or several methods of clustering onto a dataset

    Args:
        * data (PackData): dataset to play with
        * algorithm (str or list): name of algorithm(s) to use
        * **kwargs: more parameters about clustering. The 'metric' to use, the
          number of clusters expected ('n_clusters')
    
    '''

    def __init__(self, data=None, algorithm=None, **kwargs):
        if 'metric' in kwargs:
            Machine._params['metric'] = kwargs['metric']
        else:
            Machine._params['metric'] = 'euclidean'
        # n_clusters = nombre de clusters attendus
        if 'n_clusters' in kwargs:
            Machine._params['n_clusters'] = kwargs['n_clusters']
            self.n_cluster = {'f': kwargs['n_clusters']}
        else:
            self.n_cluster = {'f': 15}
        logger.info('%i clusters wanted', self.n_cluster['f'])
        self.__connectivity = None
        self.__data = None

        # LISTE DES ALGOS EN STOCK
        Machine.ALL_ALGOS = ALGOS
        Machine.__init__(self, data, algorithm=algorithm, **kwargs)
        self.algorithm = algorithm

    def __compute_connectivity(self):
        logger.debug('Computing connectivity...')
        if self.__connectivity is None:
            __nn_graph = kneighbors_graph(self.__data, n_neighbors=10,
                                          n_jobs=-1, include_self=False)
            self.__connectivity = __nn_graph.astype('float16')
        if 'ward' in self.algorithm:
            self._algorithm['ward'].set_params(connectivity=self.__connectivity)
        logger.info('Connectivity computed')

    def _check(self):
        """
        Check parameters
        """
        Machine._check(self)
        # number of clusters (n_clusters)
        if not isinstance(self.n_cluster['f'], int):
            str_msg = 'n_clusters is supposed to be an integer value. \
                       Got "%s"' % str(self.n_cluster['f'])
            logger.critical(str_msg)
            raise TypeError(str_msg)
        if self.n_cluster['f'] < 2:
            str_msg = 'n_clusters is supposed to be >= 2. Got "%i"' \
                       % self.n_cluster['f']
            logger.critical(str_msg)
            raise ValueError(str_msg)

    def load(self, data):
        """
        Loads necessary data for clustering: no samples are needed.

        Arg:
            * data (PackData): data to play with
        """
        Machine.load(self, data)
        if self._data.data is None:
            self._data.data = self._data.X
        # matrice de distances
        self.__data = StandardScaler().fit_transform(self._data.data)
        # connectivity (needed by some algorithm(s))
        if 'ward' in self.algorithm:
            self.__compute_connectivity()
        return 0

    def fit_1(self, algo):
        """
        Fits one clustering algorithm

        Arg:
            * algo (str): name of the algorithm to fit
        """
        Machine.fit_1(self, algo)
        print('\n####%s - Entrainement clustering####' % algo)

        try:
            self.algo.fit(self.__data)
        except Exception as ex:
            logger.error(ex)
        else:
            self._fitted = True

    def predict_1(self, algo, export=False):
        """
        Makes clustering prediction using one algorithme

        Args:
            * algo (str): name of the algorithm to use
            * export (bool): should the result be exported?
        """
        Machine.predict_1(self, algo)
        if hasattr(self.algo, 'labels_'):
            result = self.algo.labels_.astype(np.int8)
        elif hasattr(self.algo, 'predict'):
            result = self.algo.predict(self.__data).astype(np.int8)
        else:
            result = self.algo.fit_predict(self.__data).astype(np.int8)
        n_clusters = np.unique(result).size
        print('%i Clusters expected - Got %i clusters'
              % (self.n_cluster['f'], n_clusters))
        if hasattr(self.algo, 'score'):
            print('* Score : %.2f' % self.algo.score(self.__data))
        try:
            score = metrics.silhouette_score(self.__data, result,
                                             metric=Machine._params['metric'])
        except MemoryError:
            logger.error('Not enough memory to compute score for %s', algo)
        else:
            print('* Silhouette Score : %.2f' % score)

        score = metrics.calinski_harabaz_score(self.__data, result)
        print('* Calinski and Harabaz score : %.2f' % score)

        # 1er resultat ou ajout d'une classification a d'autres resultats
        # existants
        if self.result is None:
            self.result = pd.DataFrame(data=result, columns=[algo, ],
                                       dtype=np.int8)
        else:
            self.result[algo] = result
