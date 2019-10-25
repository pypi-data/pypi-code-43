import networkx as nx

import pytest

from ..tools import graph_identity


big_network = nx.fast_gnp_random_graph(100, .4)
nx.relabel_nodes(
    big_network,
    {n: str(n) for n in big_network.nodes()},
    copy=False)

@pytest.mark.parametrize('graph', [
    nx.Graph(), nx.DiGraph(),
    nx.Graph([('a', '2')]), nx.Graph([('a', '2'), ('2', 'a')]),
    nx.DiGraph([('a', '2')]), nx.DiGraph([('a', '2'), ('2', 'a')]),
    big_network, nx.DiGraph(big_network)
])
def test_graph_identity(graph):
    graph_id = graph_identity(graph)

    assert nx.is_isomorphic(graph, graph_id)
    assert set(graph.nodes()) == set(graph_id.nodes())
    assert set(graph.edges()) == set(graph_id.edges())
