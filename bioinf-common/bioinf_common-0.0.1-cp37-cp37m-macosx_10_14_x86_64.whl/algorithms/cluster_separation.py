from typing import Set, Any, List, Dict, Optional

import numpy as np
import networkx as nx


def get_node_distances(
    ns1: Set[Any], ns2: Set[Any],
    graph: nx.Graph, is_inter_cluster: bool,
    precomputed_distances: Optional[Dict[str, Dict[str, int]]] = None
) -> List[int]:
    """ For each node in `ns1` compute shortest distance to any node from `ns2`
    """
    # select distance function
    if precomputed_distances is None:
        dist_func = lambda source, target: nx.shortest_path_length(graph, source=source, target=target)  # noqa: E501, E731
    else:
        dist_func = lambda source, target: precomputed_distances[source][target]  # noqa: E501, E731

    # compute
    min_dist_list = []
    for n in ns1:
        dists = [dist_func(n, n2)
                 for n2 in ns2 if (is_inter_cluster or n != n2)]
        min_dist = min(dists)
        min_dist_list.append(min_dist)

    return min_dist_list


def get_avg_node_distances(
    ns1: Set[Any], ns2: Set[Any],
    graph: nx.Graph, is_inter_cluster: bool,
    precomputed_distances: Optional[Dict[str, Dict[str, int]]] = None
) -> float:
    """ Average computed node distances.
        `is_inter_cluster` should be False if `ns1` and `ns2` semantically
        describe the same set of nodes. If they have different origins
        (but could still be equal) it should be True.
    """
    len_list = get_node_distances(
        ns1, ns2, graph, is_inter_cluster,
        precomputed_distances=precomputed_distances)
    len_list += get_node_distances(
        ns2, ns1, graph, is_inter_cluster,
        precomputed_distances=precomputed_distances)

    return np.mean(len_list) if len(len_list) > 0 else np.nan


def cluster_separation(
    ns1: Set[Any], ns2: Set[Any], graph: nx.Graph,
    precomputed_distances: Optional[Dict[str, Dict[str, int]]] = None
) -> float:
    """ Compute measure from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4435741/
    """
    ns1 = set(ns1) & set(graph.nodes())
    ns2 = set(ns2) & set(graph.nodes())

    assert len(ns1) > 1, ns1
    assert len(ns2) > 1, ns2

    inter_clus = get_avg_node_distances(
        ns1, ns2, graph, True, precomputed_distances=precomputed_distances)
    intra_clus01 = get_avg_node_distances(
        ns1, ns1, graph, False, precomputed_distances=precomputed_distances)
    intra_clus02 = get_avg_node_distances(
        ns2, ns2, graph, False, precomputed_distances=precomputed_distances)

    return inter_clus - (intra_clus01 + intra_clus02) / 2
