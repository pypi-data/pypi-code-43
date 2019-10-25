import random
import itertools

import numpy as np
import networkx as nx

import pytest

from ..algorithms.network_coherence import (
    get_fraction_of_nonisolated_nodes,
    compute_network_coherence)
from ..algorithms.network_coherence_cpp import (
    get_fraction_of_nonisolated_nodes_cpp,
    compute_network_coherence_cpp)


def powerset(iter):
    s = list(iter)
    return itertools.chain.from_iterable(
        (list(c) for c in itertools.combinations(s, r)) for r in range(1, len(s)+1))

def graph_func():
    graph = nx.Graph()
    graph.add_edges_from([('0','1'), ('1','2'), ('0','2')])
    graph.add_nodes_from(['3'])
    return graph

@pytest.fixture
def graph():
    return graph_func()

def test_fractions_overall(graph):
    nc_type = 'overall'

    res = get_fraction_of_nonisolated_nodes(['1'], graph, nc_type=nc_type)
    assert res == 0
    res = get_fraction_of_nonisolated_nodes(['0','1','2'], graph, nc_type=nc_type)
    assert res == 1

    res = get_fraction_of_nonisolated_nodes(['3'], graph, nc_type=nc_type)
    assert res == 0
    res = get_fraction_of_nonisolated_nodes(['0','3'], graph, nc_type=nc_type)
    assert res == 0
    res = get_fraction_of_nonisolated_nodes(['2','1','3'], graph, nc_type=nc_type)
    assert res == 2/3
    res = get_fraction_of_nonisolated_nodes(['2','1','3','0'], graph, nc_type=nc_type)
    assert res == 3/4

def test_fractions_overiso(graph):
    nc_type = 'overiso'

    res = get_fraction_of_nonisolated_nodes(['1'], graph, nc_type=nc_type)
    assert res == 0
    res = get_fraction_of_nonisolated_nodes(['0','1','2'], graph, nc_type=nc_type)
    assert res == 3

    res = get_fraction_of_nonisolated_nodes(['3'], graph, nc_type=nc_type)
    assert res == 0
    res = get_fraction_of_nonisolated_nodes(['0','3'], graph, nc_type=nc_type)
    assert res == 0
    res = get_fraction_of_nonisolated_nodes(['2','1','3'], graph, nc_type=nc_type)
    assert res == 1
    res = get_fraction_of_nonisolated_nodes(['2','1','3','0'], graph, nc_type=nc_type)
    assert res == 3/2

@pytest.mark.parametrize('nc_type,result', [
    ('overall', -.654),
    ('overiso', -.654)
])
def test_coherence(graph, nc_type, result):
    random.seed(3)
    res = compute_network_coherence(graph, ['0','1','3'], reps=10, nc_type=nc_type)
    assert pytest.approx(res, abs=.001) == result

def test_errors(graph):
    # redundant input
    with pytest.raises(AssertionError):
        res = get_fraction_of_nonisolated_nodes(['1','1','2'], graph)

    # invalid NC-types
    with pytest.raises(RuntimeError):
        get_fraction_of_nonisolated_nodes(['1','2'], graph, nc_type='invalid')

    with pytest.raises(RuntimeError):
        compute_network_coherence(graph, ['0','1'], reps=10, nc_type='invalid')

    # empty input
    res = compute_network_coherence(graph, [])
    assert np.isnan(res)

@pytest.mark.parametrize('graph', [
    nx.Graph(), nx.DiGraph(),
    nx.Graph([('a', '2')]), nx.Graph([('a', '2'), ('2', 'a')]),
    nx.DiGraph([('a', '2')]), nx.DiGraph([('a', '2'), ('2', 'a')]),
    graph_func(), nx.DiGraph(graph_func())
])
def test_cpp_implementation(graph):
    for nodes in powerset(graph.nodes()):
        # isolated nodes
        nin = get_fraction_of_nonisolated_nodes(nodes, graph)
        nin_cpp = get_fraction_of_nonisolated_nodes_cpp(nodes, graph)

        assert nin == nin_cpp

        # network coherence
        nc = compute_network_coherence(graph, nodes, reps=5000)
        nc_cpp = compute_network_coherence_cpp(graph, nodes, 5000)

        if np.isnan(nc):
            assert np.isnan(nc_cpp)
        else:
            assert pytest.approx(nc, abs=.1) == nc_cpp
