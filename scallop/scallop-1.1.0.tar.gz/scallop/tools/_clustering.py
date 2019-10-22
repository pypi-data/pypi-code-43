import leidenalg
import louvain
from scanpy.utils import get_igraph_from_adjacency
import numpy as np


def do_clustering(alg_name, *args, **kwargs):
    supported_algnames = ['leiden', 'louvain']
    assert alg_name in supported_algnames, 'Supported algorithms are {}'.format(supported_algnames)

    if alg_name == 'leiden':
        return run_leiden(*args, **kwargs)
    elif alg_name == 'louvain':
        return run_louvain(*args, **kwargs)


def run_leiden(adj, resolution: float, random_state: int = None, use_weights: bool = True):
    # Remember that use_weights should be True to obtain a more realistic graph from the adjacency matrix.

    g = get_igraph_from_adjacency(adj, directed=True)

    weights = np.array(g.es['weight']).astype(np.float64) if use_weights else None
    part = leidenalg.find_partition(g, leidenalg.RBConfigurationVertexPartition, resolution_parameter=resolution,
                                    weights=weights, seed=random_state)
    groups = np.array(part.membership)
    return groups


def run_louvain(adj, resolution: float, random_state: int = None, use_weights: bool = True):
    g = get_igraph_from_adjacency(adj, directed=True)

    weights = np.array(g.es['weight']).astype(np.float64) if use_weights else None
    part = louvain.find_partition(g, louvain.RBConfigurationVertexPartition, resolution_parameter=resolution,
                                  weights=weights) # Todo: look if the update includes seed
    groups = np.array(part.membership)
    return groups

