# -*- coding: utf-8 -*-
"""
**Distance**

Computes pairwise distance between 2 matrices, using several metric (euclidean
is the default)

Example:
    >>> import numpy as np
    >>> y1 = np.random.random(50)
    >>> y2 = np.random.random(50)
    >>> dist = Distance(y1, y2)
    >>> dist.run()

"""
from __future__ import print_function

from math import exp, sqrt, log

import numpy as np
from scipy.spatial import distance

from maplearn import logger
from sklearn.metrics.pairwise import pairwise_distances
try:
    from mlpy import dtw_std, lcs_real
except ImportError:
    logger.warning("mlpy is not available on this system dtw and lcs will not "
                   "be available")


class Distance(object):
    """
    Computes pairwise distance between 2 matrices (x and y)

    Args:
        * x (matrix)
        * y (matrix)
    """

    def __init__(self, x=None, y=None):
        # dictionnaire des distances possibles
        self.methods = {'euclidean': 'euclidean',
                        'l2': 'l2',
                        'l1': 'l1',
                        'manhattan': 'manhattan',
                        'cityblock': 'cityblock',
                        'braycurtis': distance.braycurtis,
                        'canberra': distance.canberra,
                        'correlation': distance.correlation,
                        'cosine': distance.cosine,
                        'dice': distance.dice,
                        'hamming': distance.hamming,
                        'jaccard': distance.jaccard,
                        'kulsinski': distance.kulsinski,
                        'matching': distance.matching,
                        'rogerstanimoto': distance.rogerstanimoto,
                        'russellrao': distance.russellrao,
                        'sokalsneath': distance.sokalsneath,
                        'sqeuclidean': distance.sqeuclidean,
                        'chebyshev': distance.chebyshev,
                        'yule': distance.yule,
                        'simplex': self.simplex,
                        'minkowski': self.__minkowski,
                        'jm': self.__jm, }
        # 'mahalanobis': self.__mahalanobis
        # 'seuclidean': distance.seuclidean,

        if 'dtw_std' in globals():
            self.methods['dtw'] = self.dtw

        if 'lcs_real' in globals():
            self.methods['lcs'] = self.lcs

        self.x_a = None
        self.x_b = None
        if x is not None or y is not None:
            self.__set(x, y)

    def __set(self, x=None, y=None):
        """
        Set x and y to use
        """
        if x is not None:
            if x.ndim == 1:
                x = x.reshape(-1, 1)
            self.x_a = x
        if y is not None:
            if y.ndim == 1:
                y = y.reshape(-1, 1)
            self.x_b = y
        if self.x_a is not None and self.x_b is not None:
            if self.x_a.ndim != self.x_b.ndim:
                raise IndexError("Dimensions of X & Y are not compatible")

    def dtw(self, x=None, y=None):
        """
        Dynamic Time-Warping distance
        """
        if x is not None or y is not None:
            self.__set(x, y)
        return dtw_std(self.x_a, self.x_b, dist_only=True, squared=True)

    def lcs(self, x=None, y=None, eps=10, delta=3):
        """
        Distance based on Longest Common Subsequence
        """
        if x is not None or y is not None:
            self.__set(x, y)
        result = lcs_real(self.x_a, self.x_b, eps=eps, delta=delta)
        # conversion en distance
        result = (len(self.x_a) - result[0]) / len(self.x_a)
        return result

    def simplex(self, x=None, y=None, sigma=50):
        """
        Simplex distance
        """
        if x is not None or y is not None:
            self.__set(x, y)
        return 1 - (np.sum((self.x_a - self.x_b) ** 2 / (2 * sigma ** 2)))

    def __mahalanobis(self, x=None, y=None):
        """
        Mahalanobis distance
        """
        if x is not None or y is not None:
            self.__set(x, y)
        try:
            vi = np.linalg.inv(np.cov(self.x_a, self.x_b, rowvar=0))
        except np.linalg.LinAlgError:
            logger.warning("Can't calculate the metric: singular \
                            covariance matriX.")
            return None
        return distance.mahalanobis(self.x_a, self.x_b, VI=vi)

    def __minkowski(self, x=None, y=None, p=2):
        """
        Minkowski distance
        """
        if x is not None or y is not None:
            self.__set(x, y)
        return distance.minkowski(u=self.x_a, v=self.x_b, p=p)

    def __jm(self, x=None, y=None):
        """
        Jeffries-Matusita Distance:
        Get 2 vectors or matrices (x & y) and return Jeffries-Matusita distance
        source : adapted from
            https://github.com/KolesovDmitry/i.jmdist/blob/master/i.jmdist
        """
        if x is not None or y is not None:
            self.__set(x, y)
        m_x, m_y = np.mean(self.x_a, axis=0), np.mean(self.x_b, axis=0)
        s_x, s_y = np.cov(self.x_a, rowvar=0), np.cov(self.x_b, rowvar=0)
        if s_x.ndim == 0:
            s_x = s_x.reshape([1, 1])
        if s_y.ndim == 0:
            s_y = s_y.reshape([1, 1])
        dm = (m_x - m_y)
        s_xy = (s_x + s_y) / 2
        try:
            invmatr = np.linalg.inv(s_xy)
        except np.linalg.LinAlgError:
            logger.warning("Can't calculate the metric: singular \
                            covariance matrix.")
            return None
        # Mahalanobis distance (mh):
        tmp = np.core.dot(dm.T, invmatr)
        tmp = np.core.dot(tmp, dm)
        mahalanobis = sqrt(tmp)

        # BhattacharYYa distance (B):
        tmp = np.linalg.det(s_xy) / sqrt(np.linalg.det(s_x) *
                                         np.linalg.det(s_y))
        tmp = log(tmp)
        B = mahalanobis / 8.0 + tmp / 2.0
        # J-M distance:
        return sqrt(2 * (1 - exp(-B)))

    def run(self, x=None, y=None, meth='euclidean'):
        """
        Distance calculation according to a specified method

        Args:
            * x (matrix)
            * y (matrix)
            * meth (str): name of the metric distance to use

        Returns:
            matrix of pairwise distance values
        """
        if x is not None or y is not None:
            self.__set(x, y)
        try:
            return pairwise_distances(self.x_a, self.x_b, n_jobs=-1,
                                      metric=self.methods[meth])
        except TypeError:
            return pairwise_distances(self.x_a, self.x_b,
                                      metric=self.methods[meth])

    def compare(self, x=None, y=None, methods=[]):
        """
        Compare pairwise distances got with different metrics

        Args:
            * x and y (matrices)
            * methods (list): list of metrics used to compute pairwise distance.
              if empty, every available metrics will be compared

        """
        print('** Comparaison des mesures de distance **')
        if x is not None or y is not None:
            self.__set(x, y)
        if len(methods) == 0:
            methods = self.methods.keys()

        # Compute pairwise distances using the specified metrics
        dct_results = dict()
        for i in methods:
            try:
                dct_results[i] = float(self.run(meth=i))
            except TypeError:
                dct_results[i] = None

        # Display distances in descending order
        for i in sorted(dct_results, key=dct_results.get, reverse=True):
            if dct_results[i] is not None:
                print('- %s : %.3f' % (i, dct_results[i]))
            else:
                print('- %s : None' % i)
