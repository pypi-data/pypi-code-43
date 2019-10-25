# import networkx as nx
#
# import pytest
#
# from ..tools import Graph
#
#
# big_network = nx.fast_gnp_random_graph(100, .4)
# nx.relabel_nodes(
#     big_network,
#     {n: str(n) for n in big_network.nodes()},
#     copy=False)
#
# @pytest.mark.parametrize('graph', [
#     nx.Graph(), nx.DiGraph(),
#     nx.Graph([('a', '2')]), nx.Graph([('a', '2'), ('2', 'a')]),
#     nx.DiGraph([('a', '2')]), nx.DiGraph([('a', '2'), ('2', 'a')]),
#     big_network, nx.DiGraph(big_network)
# ])
# def test_graph_constructor(graph):
#     g = Graph(graph)
#
#     import IPython; IPython.embed()
#     exit()
#
#     assert graph.is_directed() == g.isDirected()
#     assert list(graph.nodes()) == g.getNodes()
#     assert set(nx.DiGraph(graph).edges()) == set(g.getEdges())
#
#     for n in graph.nodes():
#         assert list(graph.neighbors(n)) == g.getNeighbors(n)
