import numpy as np
from scipy.sparse.csgraph import shortest_path

from fermat.path_methods import DistanceCalculatorMethod


class FloydWarshallMethod(DistanceCalculatorMethod):

    def __init__(self, alpha, **kwargs):
        super().__init__(alpha, **kwargs)
        self.distances_ = None

    def fit(self, distances):
        # noinspection PyTypeChecker
        self.distances_ = shortest_path(
            csgraph=np.power(distances, self.alpha),
            method='FW',
            directed=False
        )  # type: np.ndarray
        return self

    def get_distance(self, a, b):
        return self.distances_[a, b]

    def get_distances(self):
        return self.distances_
