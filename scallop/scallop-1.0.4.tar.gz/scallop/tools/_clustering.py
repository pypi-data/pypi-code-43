import leidenalg
from scanpy.utils import get_igraph_from_adjacency
import numpy as np


def run_leiden(adj, resolution: float, random_state: int = None, use_weights: bool = True):
    # Remember that use_weights should be True to obtain a more realistic graph from the adjacency matrix.
    g = get_igraph_from_adjacency(adj, directed=True)

    weights = np.array(g.es['weight']).astype(np.float64) if use_weights else None
    part = leidenalg.find_partition(g, leidenalg.RBConfigurationVertexPartition, resolution_parameter=resolution,
                                    weights=weights, seed=random_state)
    groups = np.array(part.membership)
    return groups
