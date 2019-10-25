import os
import time
import random
import collections

import networkx as nx

import numpy as np
from numpy.testing import assert_array_equal

import pytest

from ..tools.graph_tool_wrapper import (
    convert_networkx_to_graphtool, convert_graphtool_to_networkx,
    compute_node_distances, _compute_nx_distances, _compute_gt_distances,
    _get_gtgraph_nodes, _get_gtgraph_edges, _get_nxgraph_edges,
    NETWORKX_FALLBACK, ls
)


# graph definitions
def nx_graph_func():
    random.seed(42)

    nx_graph = nx.fast_gnp_random_graph(10, .2)
    nx.relabel_nodes(nx_graph, {n: str(n) for n in nx_graph.nodes()}, copy=False)
    nx.relabel_nodes(nx_graph, {'3': 'foo', '8': 'bar'}, copy=False)

    assert len(list(nx.connected_components(nx_graph))) == 2
    return nx_graph.to_directed()

@pytest.fixture
def nx_graph():
    return nx_graph_func()

large_graph = nx.Graph(
    [(str(i), str(j)) for i, j in np.random.choice(range(100), size=(100, 2))])

graph_list = [
    nx.Graph(), nx.DiGraph(),
    nx.Graph([('a', '2')]), nx.Graph([('a', '2'), ('2', 'a')]),
    nx.DiGraph([('a', '2')]), nx.DiGraph([('a', '2'), ('2', 'a')]),
    nx.Graph(nx_graph_func()), nx_graph_func(),
    large_graph, large_graph.to_directed()
]


# test functions
@pytest.mark.skipif(NETWORKX_FALLBACK, reason='graph-tool not installed')
@pytest.mark.parametrize('p_nx_graph', graph_list)
def test_network_conversion(p_nx_graph):
    # nx -> gt
    gt_graph = convert_networkx_to_graphtool(p_nx_graph)
    assert gt_graph.num_vertices() == p_nx_graph.number_of_nodes()
    assert _get_gtgraph_nodes(gt_graph) == ls(p_nx_graph.nodes())
    assert gt_graph.num_edges() == p_nx_graph.number_of_edges()
    assert _get_gtgraph_edges(gt_graph) == _get_nxgraph_edges(p_nx_graph)

    # gt -> nx
    nx_graph_rev = convert_graphtool_to_networkx(gt_graph)
    assert gt_graph.num_vertices() == nx_graph_rev.number_of_nodes()
    assert ls(p_nx_graph.nodes()) == ls(nx_graph_rev.nodes())
    assert gt_graph.num_edges() == nx_graph_rev.number_of_edges()
    assert _get_nxgraph_edges(p_nx_graph) == _get_nxgraph_edges(nx_graph_rev)

@pytest.mark.skipif(NETWORKX_FALLBACK, reason='graph-tool not installed')
@pytest.mark.parametrize('p_nx_graph', [
    nx.Graph([('a', 2)]), nx.DiGraph([(0, 1)])
])
def test_string_node_requirement(p_nx_graph):
    with pytest.raises(RuntimeError) as excinfo:
        convert_networkx_to_graphtool(p_nx_graph)
    assert 'All nodes must be strings' in str(excinfo.value)

@pytest.mark.skipif(NETWORKX_FALLBACK, reason='graph-tool not installed')
def test_specific_distance_calculation(nx_graph):
    starting_nodes = ['1', 'bar', '9']
    end_nodes = ['foo', '4', '7']

    nx_dists = _compute_nx_distances(nx_graph, starting_nodes, end_nodes)
    gt_dists = _compute_gt_distances(
        convert_networkx_to_graphtool(nx_graph),
        sources=starting_nodes, targets=end_nodes)

    assert_array_equal(nx_dists, gt_dists)

@pytest.mark.skipif(NETWORKX_FALLBACK, reason='graph-tool not installed')
def test_onetoall_calculation(nx_graph):
    starting_nodes = ['bar', '4']
    end_nodes = ls(nx_graph.nodes())

    nx_dists = _compute_nx_distances(
        nx_graph, starting_nodes, end_nodes)
    gt_dists = _compute_gt_distances(
        convert_networkx_to_graphtool(nx_graph),
        sources=starting_nodes, targets=end_nodes)

    assert_array_equal(nx_dists, gt_dists)

@pytest.mark.skipif(NETWORKX_FALLBACK, reason='graph-tool not installed')
@pytest.mark.parametrize('p_nx_graph', graph_list)
def test_allpair_distance_calculation(p_nx_graph):
    all_nodes = ls(p_nx_graph.nodes())

    nx_dists = _compute_nx_distances(
        p_nx_graph, all_nodes, all_nodes)
    gt_dists = _compute_gt_distances(
        convert_networkx_to_graphtool(p_nx_graph),
        sources=all_nodes, targets=all_nodes)

    assert_array_equal(nx_dists, gt_dists)

@pytest.mark.parametrize('p_nx_graph', graph_list)
def test_wrapper_function(tmpdir, p_nx_graph):
    fname = os.path.join(tmpdir, 'data.dat')

    all_nodes = ls(p_nx_graph.nodes())
    nx_dist_dict = dict(nx.shortest_path_length(p_nx_graph))
    dist_dict = compute_node_distances(p_nx_graph, fname=fname)

    # test caching
    assert os.path.exists(fname + '.npz')
    data = np.load(fname + '.npz')

    assert_array_equal(ls(p_nx_graph.nodes()), data['graph_nodes'])
    assert_array_equal(_get_nxgraph_edges(p_nx_graph), data['graph_edges'])
    assert_array_equal(ls(p_nx_graph.nodes()), data['sources'])
    assert_array_equal(ls(p_nx_graph.nodes()), data['targets'])
    assert_array_equal(
        _compute_nx_distances(p_nx_graph, all_nodes, all_nodes),
        data['dist_array'])

    dist_dict_cache = compute_node_distances(p_nx_graph, fname=fname)

    # test computation result
    assert dist_dict == dist_dict_cache
    assert nx_dist_dict == dist_dict
