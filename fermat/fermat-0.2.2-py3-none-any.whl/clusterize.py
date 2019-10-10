import numpy as np
from sklearn.base import ClusterMixin, BaseEstimator
from sklearn.metrics import euclidean_distances

from fermat import Fermat
from fermat import kmedoids


class FermatKMeans(BaseEstimator, ClusterMixin):

    def __init__(self,
                 cluster_qty=8,
                 alpha=2, path_method='FW', k=None, landmarks=None, estimator=None, seed=None,
                 iterations=5, max_faults=5, log=False,
                 distance='euclidean'
                 ):
        """
        :param cluster_qty: Number of clusters to find
        :param distance: Must be 'euclidean' or 'matrix'. Default value = 'euclidean'
        :param alpha: Alpha for Fermat distance. See fermat.Fermat
        :param path_method: Must be 'FW', 'D' or 'L'. See fermat.Fermat
        :param k: Number of neighbors when path_method 'D' or 'L'. See fermat.Fermat
        :param landmarks: Number of landmarks when path_method is 'L'. See fermat.Fermat
        :param estimator: Landmark variant when path_method is 'L'. See fermat.Fermat
        :param iterations: Number of runs for wich the KMedoids algorithm will return the best result
        :param max_faults: Number of times that the algorithm can fail to reduce the actual cost
        :param log: Allows logging for the Kmeans Algorithm (kmedoids.logs)
        :param seed: Random seed.
        """
        self.cluster_qty = cluster_qty
        self.alpha = alpha
        self.path_method = path_method
        self.k = k
        self.landmarks = landmarks
        self.estimator = estimator
        self.seed = seed
        self.iterations = iterations
        self.max_faults = max_faults
        self.log = log
        self.distance = distance
        self.distance_matrix_ = None
        self.labels_ = None

    def fit(self, X):
        if self.distance not in ('euclidean', 'matrix'):
            raise ValueError("Unknown value for distance parameter: {}".format(self.distance))

        if self.distance == 'euclidean':
            X = euclidean_distances(X, X)
        X = X / np.mean(X)

        fermat = Fermat(
            alpha=self.alpha,
            path_method=self.path_method,
            k=self.k,
            landmarks=self.landmarks,
            estimator=self.estimator,
            seed=self.seed
        )

        fermat.fit(X)

        km = kmedoids.KMedoids(
            iterations=self.iterations,
            max_faults=self.max_faults,
            log=self.log,
            seed=self.seed
        )

        self.distance_matrix_ = fermat.get_distances()
        self.labels_ = km(self.distance_matrix_, self.cluster_qty)
        return self
