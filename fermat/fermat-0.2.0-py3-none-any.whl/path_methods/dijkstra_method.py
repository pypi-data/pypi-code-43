import heapq

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

from fermat.path_methods.distance_calculator_method import DistanceCalculatorMethod


class DijkstraMethod(DistanceCalculatorMethod):

    def __init__(self, alpha, k, **kwargs):
        super().__init__(alpha)
        self.k = k
        self.distances_ = None

    def fit(self, distances):

        adj_matrix = self.create_adj_matrix(distances)
        self.distances_ = shortest_path(
            csgraph=adj_matrix.power(self.alpha),
            method='D'
        )
        return self

    def create_adj_matrix(self, distances):
        
        k = self.k
        n = distances.shape[0]
        
        rows = []
        columns = []
        values = []
        
        for i in range(n):
            smallest_values_and_columns = heapq.nsmallest(k, zip(distances[i].tolist(), list(range(n))))
            vs, cs = zip(*smallest_values_and_columns)

            rows.extend([i]*k)
            columns.extend(cs)
            values.extend(vs)
        
        return csr_matrix((values+values, (rows+columns, columns+rows)), shape=(n, n))

    def get_distance(self, a, b):
        return self.distances_[a, b]

    def get_distances(self):
        return self.distances_
