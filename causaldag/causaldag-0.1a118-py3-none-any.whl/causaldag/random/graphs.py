import numpy as np
from ..classes.dag import DAG
import itertools as itr


def _coin(p, size=1):
    return np.random.binomial(1, p, size=size)


def directed_erdos(n, s, size=1):
    if size == 1:
        arcs = {(i, j) for i, j in itr.combinations(range(n), 2) if _coin(s)}
        return DAG(nodes=set(range(n)), arcs=arcs)
    else:
        return [directed_erdos(n, s) for _ in range(size)]






