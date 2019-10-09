from collections import namedtuple
from typing import List, Optional, Tuple

import numpy as np
from numpy.random import RandomState

Log = namedtuple("Log", ['centers', 'cost'])


class KMedoids:

    def __init__(self, iterations=5, max_faults=5, log=False, seed: int = None):
        self.max_faults = max_faults
        self.iterations = iterations
        self.log = log
        self.logs = []  # type: List[List[Log]]
        self.best = -1
        self.rs = RandomState(seed)

    def find_clusters(self, data: np.ndarray, centers_idx: np.ndarray) -> np.ndarray:
        return centers_idx[data[centers_idx].argmin(axis=0)]

    def sum_distances_to_centers(self, data: np.ndarray, clusters: np.ndarray) -> float:
        return data[np.arange(len(data)), clusters].sum()

    def to_groups(self, clusters: np.ndarray) -> List[List[int]]:
        groups = [[] for _ in clusters]  # type: List[List[int]]
        for i, center in enumerate(clusters):
            groups[center].append(i)
        return [group for group in groups if group]

    def find_centers(self, data: np.ndarray, clusters: np.ndarray) -> np.ndarray:
        return np.array([
            group[data[np.ix_(group, group)].sum(axis=0).argmin()]
            for group in self.to_groups(clusters)
        ])

    def choose_initial_centers(self, data: np.ndarray, qty: int):
        points = np.arange(len(data))
        p = np.ones_like(points) / len(points)

        res = []
        for _ in range(qty):
            res.append(self.rs.choice(points, p=p))
            p = data[res].min(axis=0)
            p /= p.sum()

        return np.array(res)

    def k_medoids_run(self, data: np.ndarray, qty) -> Tuple[np.ndarray, float]:

        last_cost = np.inf
        faults = 0

        if self.log:
            self.logs.append([])

        centers_idx = self.choose_initial_centers(data, qty)

        while True:
            clusters = self.find_clusters(data, centers_idx)
            cost = self.sum_distances_to_centers(data, clusters)

            if self.log:
                self.logs[-1].append(Log(centers=centers_idx, cost=cost))

            faults += cost >= last_cost

            if faults >= self.max_faults:
                break

            last_cost = cost
            new_centers_idx = self.find_centers(data, clusters)
            if set(centers_idx) == set(new_centers_idx):
                break

            centers_idx = new_centers_idx

        return clusters, cost

    def __call__(self, data: np.ndarray, qty: int):
        self.best = -1

        runs = (
            [*self.k_medoids_run(data, qty), i]
            for i in range(self.iterations)
        )

        res, cost, self.best = min(runs, key=lambda x: x[1])

        return res
