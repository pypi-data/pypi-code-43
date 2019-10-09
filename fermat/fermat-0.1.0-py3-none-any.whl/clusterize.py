import numpy as np
from sklearn.metrics import euclidean_distances

from fermat import Fermat
from fermat import kmedoids


class FermatKMeans:

    def __init__(self,
                 cluster_qty,
                 alpha, path_method='FW', k=None, landmarks=None, estimator=None, seed=None,
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
        if distance not in ('euclidean', 'matrix'):
            raise ValueError("Unknown value for distance parameter: {}".format(self.distance))
        self.distance = distance
        self.fermat = Fermat(alpha, path_method, k, landmarks, estimator, seed)
        self.kmedoids = kmedoids.KMedoids(iterations, max_faults, log, seed)
        self.cluster_qty = cluster_qty
        self.distance_matrix = None

    def fit_predict(self, data):
        if self.distance == 'euclidean':
            data = euclidean_distances(data, data)
        data /= np.mean(data)
        self.fermat.fit(data)
        self.distance_matrix = self.fermat.get_distances()
        return self.kmedoids(self.distance_matrix, self.cluster_qty)

