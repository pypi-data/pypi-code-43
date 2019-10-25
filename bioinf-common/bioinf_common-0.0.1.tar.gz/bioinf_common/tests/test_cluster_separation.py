import networkx as nx

import pytest

from ..algorithms.cluster_separation import get_node_distances, get_avg_node_distances, cluster_separation
from ..algorithms.cluster_separation_cpp import cluster_separation_cpp


@pytest.fixture
def network_setup():
    graph = nx.Graph()

    graph.add_edges_from([
        (0,1), (2,1), (1,3), (4,3), (5,3), (3,6), (3,7), (3,8), (3,9), (6,7),
        (9,10), (7,10), (11,10), (10,8), (8,12), (7,12), (12,13), (13,14),
        (8,15), (8,16), (12,16), (12,17), (16,17), (15,18), (19,18), (20,18),
        (15,21), (15,22), (15,23), (15,16), (16,23), (21,22), (22,23),
        (22,24), (23,25)
    ])

    cluster_1 = [5, 3, 7, 14]
    cluster_2 = [7, 10, 8, 17, 22]

    return graph, cluster_1, cluster_2

def test_pairwise_distances(network_setup):
    graph, clus1, clus2 = network_setup

    # intra-cluster
    res = get_node_distances(clus1, clus1, graph, is_inter_cluster=False)
    assert res == [1,1,1,3]
    res = get_avg_node_distances(clus1, clus1, graph, is_inter_cluster=False)
    assert res == 3/2

    res = get_node_distances(clus2, clus2, graph, is_inter_cluster=False)
    assert res == [1,1,1,2,2]
    res = get_avg_node_distances(clus2, clus2, graph, is_inter_cluster=False)
    assert res == 7/5

    # inter-cluster
    res = get_node_distances(clus1, clus2, graph, is_inter_cluster=True)
    assert res == [2,1,0,3]
    res = get_node_distances(clus2, clus1, graph, is_inter_cluster=True)
    assert res == [0,1,1,2,3]

    res_12 = get_avg_node_distances(clus1, clus2, graph, is_inter_cluster=True)
    res_21 = get_avg_node_distances(clus2, clus1, graph, is_inter_cluster=True)
    assert res_12 == 13/9 == res_21

def test_separation(network_setup):
    graph, clus1, clus2 = network_setup

    res_12 = cluster_separation(clus1, clus2, graph)
    res_21 = cluster_separation(clus2, clus1, graph)
    assert res_12 == pytest.approx(-1/180) == res_21

def test_precomputed_distances(network_setup):
    graph, clus1, clus2 = network_setup
    nx_dists = dict(nx.shortest_path_length(graph))

    res_12 = cluster_separation(
        clus1, clus2, graph, precomputed_distances=nx_dists)
    res_21 = cluster_separation(
        clus2, clus1, graph, precomputed_distances=nx_dists)
    assert res_12 == pytest.approx(-1/180) == res_21

def test_cpp_implementation(network_setup):
    graph, clus1, clus2 = network_setup
    nx.relabel_nodes(graph, {n: str(n) for n in graph.nodes()}, copy=False)
    clus1 = list(map(str, clus1))
    clus2 = list(map(str, clus2))

    nx_dists = dict(nx.shortest_path_length(graph))

    res_12 = cluster_separation_cpp(
        clus1, clus2, precomputed_distances=nx_dists)
    res_21 = cluster_separation_cpp(
        clus2, clus1, precomputed_distances=nx_dists)
    assert res_12 == pytest.approx(-1/180) == res_21

    # test single node clusters
    res = cluster_separation_cpp(['5'], ['10'], nx_dists)
    assert res == -2147483644.0  # NaN
