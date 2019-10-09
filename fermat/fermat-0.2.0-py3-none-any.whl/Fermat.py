from collections import Callable
from typing import Dict

import numpy as np
from sklearn.base import BaseEstimator


class Fermat(BaseEstimator):

    def __init__(self, alpha, path_method='L', k=None, landmarks=None, estimator='up', seed=None):
        """
        Parameters
        -----------
        alpha: float
            Parameter of the Fermat distance.

        path_method: string ['FW','D','L']

            Options are:

                    'FW'    -- Computes the exact Fermat distance using the Floyd-Warshall algorithm. The complexity is
                             O[N^3] where N is the number of data points.

                    'D'     --  Computes an approximation of the Fermat distance using k nearest neighbours and the
                             Dijkstra algorithm. The complexity is O[N*(k*N*log N)]

                    'L'     -- Computes an approximation of the Fermat distance using landmarks and k-nn. The complexity
                             is O[l*(k*N*log N)] where l is the number of landmarks considered.

        k: integer, optional
            Number of nearest neighbors to be considered.
            Not used when path_method == 'FW'

        landmarks: integer, optional
            Number of landmarks considered in the Fermat distance computation.
            Only used when path_method = 'L'

        estimator: string ['up', 'down', 'mean', 'no_lca'] (default: 'up')
            When computing an approximation of the Fermat distance, there are lower and upper bounds of the true value.
            If estimator == 'no_lca', the distance for a pair of points is calculated as the minimum sum of the distance
                from both points to one of the landmarks.
            If estimator == 'up', the distance for a pair of points is calculated as the minimum sum of the distance
                from both points to the lowest common ancestor in the distance tree of one of the landmarks.
            If estimator == 'down', the distance for a pair of points is calculated as the maximum difference of the
                distance from both points to one of the landmarks.
            If estimator == 'mean', the  mean between 'up' and 'down' estimators.
            Only used when path_method = 'L'

        seed: int, optional
            Only used when path_method = 'L'


        Returns
        -----------
        Fermat class object


        Examples


        # init an exact Fermat distance model

        f_exact = Fermat(alpha = 3, path_method='FW', seed = 1)


        # init an approx Fermat distance model

        f_aprox = Fermat(alpha, path_method='L', k=10, landmarks=50)

        """
        self.alpha = alpha
        self.path_method = path_method
        self.k = k
        self.landmarks = landmarks
        self.estimator = estimator
        self.seed = seed

        self.method_ = None

    def fit(self, distances: np.ndarray):
        """

        Parameters
        -----------
        distances: np.ndarray
            Matrix with pairwise distances

        """
        self.method_ = Methods().by_name(**self.get_params()).fit(distances)
        return self

    def get_distance(self, a, b):
        """

        Parameters
        -----------
        a: int
            Index of a data point

        b: int
            Index of a data point

        Returns
        -----------
        Float: the Fermat distance between points a and b


        """

        return self.method_.get_distance(a, b)

    def get_distances(self):
        """

        Parameters
        -----------
        -

        Returns
        -----------
        np.matrix with the pairwise Fermat distances

        """

        return self.method_.get_distances()


class Methods:

    from fermat.path_methods import LandmarksMethod, FloydWarshallMethod, DijkstraMethod, DistanceCalculatorMethod

    methods = {
        'FW': FloydWarshallMethod,
        'D': DijkstraMethod,
        'L': LandmarksMethod,
    }  # type: Dict[str, Callable[[Fermat], DistanceCalculatorMethod]]

    @staticmethod
    def by_name(path_method, **kwargs) -> DistanceCalculatorMethod:
        if path_method in Methods.methods.keys():
            return Methods.methods[path_method](**kwargs)
        else:
            raise ValueError('Invalid value for parameter `path_method`: {}'.format(path_method))
