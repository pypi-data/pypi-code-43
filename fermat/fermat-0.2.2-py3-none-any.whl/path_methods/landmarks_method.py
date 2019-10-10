import heapq
import numpy as np

from scipy.sparse import csr_matrix, dok_matrix
from scipy.sparse.csgraph import shortest_path

from fermat.path_methods.distance_calculator_method import DistanceCalculatorMethod


class DistanceOnTree:

    def __init__(self, root, prev, distances):
        self.n = len(prev)
        self.et = self.euler_tour(root, prev)
        self.root = root
        self.distances = distances
        self.right = self.get_right(self.et, self.n)
        self.rmq = self.get_rmq([distances[x] for x in self.et])

    def euler_tour(self, root, prev):
        children = [[] for _ in prev]
        for node, parent in enumerate(prev):
            if node != root and parent >= 0:  # -9999 is used to indicate that there is no previous node
                children[parent].append(node)

        res = []

        def aux(cur):
            res.append(cur)
            for child in children[cur]:
                aux(child)
                res.append(cur)

        aux(root)

        return res

    def get_right(self, et, n):
        res = [-1] * n
        for index, node in enumerate(et):
            res[node] = index
        return res

    def get_rmq(self, xs):
        r = np.array(xs)
        res = [r]
        n = len(xs)
        p = 1

        while p < n:
            r = np.append(np.min([r[:n - p], r[p:n]], axis=0), r[n - p:])
            res.append(r)
            p *= 2

        return res

    def get_lca_distance(self, a, b):
        r = self.right
        x = r[a]
        y = r[b]
        if x > y:
            x, y = y, x
        d = (y - x).bit_length() - 1
        level = self.rmq[d]
        return min(level[x], level[y - (1 << d) + 1])

    def get_distance(self, a, b):
        return a - b and self.distances[a] + self.distances[b] - 2 * self.get_lca_distance(a, b)


class LandmarksMethod(DistanceCalculatorMethod):

    def __init__(self, alpha, landmarks, k, estimator, seed, **kwargs):
        super().__init__(alpha)
        self.n = None
        self.k = k
        self.estimator = estimator
        self.landmarks = landmarks
        self.seed = seed
        self.landmarks_trees_ = []

    def get_near_points(self, distances):

        n = distances.shape[0]

        columns = []
        values = []

        for i in range(n):
            smallest_values_and_columns = heapq.nsmallest(self.k + 1, zip(distances[i].tolist()[0], list(range(n))))
            vs, cs = zip(*smallest_values_and_columns)

            columns.append(cs)
            values.append(vs)

        return columns, values

    def create_adj_matrix(self, l, near_columns, near_values, distances):

        n = distances.shape[0]
        m = dok_matrix((n, n), dtype='d')

        for row in range(n):
            for column, value in zip(near_columns[row], near_values[row]):
                m[row, column] = m[column, row] = value

            m[row, l] = m[l, row] = distances[l, row]

        return m

    def create_adj_matrix_all(self, landmarks, distances):

        n = distances.shape[0]

        columns = []
        rows = []
        values = []

        for i in range(n):
            if i in landmarks:
                values.extend(distances[i, j] for j in range(n))
                columns.extend(range(n))
                rows.extend([i] * n)
            else:
                smallest_values_and_columns = heapq.nsmallest(
                    self.k + 1,
                    zip(distances[i], list(range(n)))
                )
                vs, cs = zip(*smallest_values_and_columns)
                values.extend(vs)
                columns.extend(cs)
                rows.extend([i] * len(vs))

        return csr_matrix((values, (rows, columns)), shape=(n, n))

    def fit(self, distances):

        self.n = distances.shape[0]

        landmarks = np.random.RandomState(seed=self.seed).choice(range(distances.shape[0]), self.landmarks)

        adj = self.create_adj_matrix_all(landmarks, distances)

        distance, prev = shortest_path(
            csgraph=adj.power(self.alpha),
            method='D',
            return_predecessors=True,
            directed=False,
            indices=landmarks
        )

        for i in range(len(landmarks)):
            landmark_tree = DistanceOnTree(landmarks[i], prev=prev[i], distances=distance[i])
            self.landmarks_trees_.append(landmark_tree)

        return self

    def up(self, a, b):
        return min(lt.get_distance(a, b) for lt in self.landmarks_trees_)

    def down(self, a, b):
        return max(abs(lt.distances[a] - lt.distances[b]) for lt in self.landmarks_trees_)

    def no_lca(self, a, b):
        return min(lt.distances[a] + lt.distances[b] for lt in self.landmarks_trees_)

    def get_distance(self, a, b):
        if self.estimator == 'up':
            return self.up(a, b)
        if self.estimator == 'down':
            return self.down(a, b)
        if self.estimator == 'mean':
            return (self.up(a, b) + self.down(a, b)) / 2
        if self.estimator == 'no_lca':
            return self.no_lca(a, b)

    def get_distance_calculator(self):
        if self.estimator == 'up':
            return self.up
        if self.estimator == 'down':
            return self.down
        if self.estimator == 'mean':
            return lambda a, b: (self.up(a, b) + self.down(a, b)) / 2
        if self.estimator == 'no_lca':
            return self.no_lca

    def get_distances(self):
        res = np.zeros((self.n, self.n))
        d = self.get_distance_calculator()
        for i in range(self.n):
            for j in range(i):
                res[i, j] = d(i, j)
        return res + res.T
