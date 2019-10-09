import numpy as np
from scipy.sparse.csgraph import shortest_path

from fermat.Fermat import DistanceCalculatorMethod


class FloydWarshallMethod(DistanceCalculatorMethod):

    def fit(self, distances):
        # noinspection PyTypeChecker
        self.distances = shortest_path(
            csgraph=np.power(distances, self.fermat.alpha),
            method='FW',
            directed=False
        )  # type: np.ndarray
        return self

    def get_distance(self, a, b):
        return self.distances[a, b]

    def get_distances(self):
        return self.distances
