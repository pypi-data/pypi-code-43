import os
import sys

from io import BytesIO

import numpy as np
import networkx as nx

from typing import (
    TypeVar, Any, List, Iterable,
    Dict, Optional, Tuple)

try:
    import graph_tool as gt
    from graph_tool import generation, topology

    NETWORKX_FALLBACK = False
except ImportError:
    NETWORKX_FALLBACK = True


T = TypeVar('T')


def ls(mylist: Iterable[T]) -> List[T]:
    """ Used for dealing with problems arising when comparing unordered
        Node-/Edge-views and lists
    """
    return list(sorted(mylist))


if NETWORKX_FALLBACK:
    def convert_networkx_to_graphtool(nx_graph: nx.Graph) -> 'gt.Graph':
        raise NotImplementedError('graph-tool not installed')
else:
    def convert_networkx_to_graphtool(nx_graph: nx.Graph) -> gt.Graph:
        """ Convert a networkx to a graph-tool network
        """
        gt_graph = gt.Graph(directed=nx_graph.is_directed())

        # set properties
        gt_graph.vertex_properties['id'] = gt_graph.new_vertex_property('string')  # noqa: E501

        # assert that given nodes are strings
        for node in nx_graph.nodes():
            if not isinstance(node, str):
                raise RuntimeError(
                    f'All nodes must be strings ("{node}" is not)')

        # add nodes
        node_map = {}
        for node, data in sorted(nx_graph.nodes(data=True)):
            v = gt_graph.add_vertex()
            gt_graph.vp['id'][v] = str(node)
            node_map[node] = v

        # add edges
        for src, dst, data in nx_graph.edges(data=True):
            gt_graph.add_edge(node_map[src], node_map[dst])

        # sanity checks
        assert _get_gtgraph_nodes(gt_graph) == ls(nx_graph.nodes())

        return gt_graph


def _get_gtgraph_nodes(gt_graph: 'gt.Graph') -> List[str]:
    """ Node names are assumed to be stored in the vertex property-map 'id'
    """
    return gt_graph.vp['id'].get_2d_array([0])[0].tolist()


def _get_gtgraph_edges(gt_graph: 'gt.Graph') -> List[Tuple[str, str]]:
    get_name = lambda v: gt_graph.vp['id'][gt_graph.vertex(v)]  # noqa: E731

    edges = [(get_name(src_idx), get_name(dst_idx))
             for src_idx, dst_idx in gt_graph.get_edges()]
    if not gt_graph.is_directed():
        edges += [(get_name(dst_idx), get_name(src_idx))
                  for src_idx, dst_idx in gt_graph.get_edges()]

    return ls(set(edges))


def _get_nxgraph_edges(nx_graph: nx.Graph) -> List[Tuple[str, str]]:
    """ Take care of possibly undirected edges
    """
    edges = list(nx_graph.edges())
    if not nx_graph.is_directed():
        edges += [(v, u) for u, v in nx_graph.edges()]
    return ls(set(edges))


def convert_graphtool_to_networkx(gt_graph: 'gt.Graph') -> nx.Graph:
    # save graph as graphml-object
    reader = BytesIO()
    gt_graph.save(reader, fmt='graphml')
    reader.seek(0)

    # restore graphml-object
    GraphClass = nx.DiGraph if gt_graph.is_directed() else nx.Graph
    nx_graph = GraphClass(nx.read_graphml(reader))

    # set node names correctly
    nx.relabel_nodes(
        nx_graph,
        {n: d['id'] for n, d in nx_graph.nodes(data=True)},
        copy=False)

    return nx_graph


def rewire_graph(nx_graph: nx.Graph) -> nx.Graph:
    """ Rewire the given graph
    """
    gt_graph = convert_networkx_to_graphtool(nx_graph)
    generation.random_rewire(
        gt_graph,
        model='configuration',
        n_iter=2, edge_sweep=True,
        parallel_edges=False, self_loops=False,
        verbose=True)
    return convert_graphtool_to_networkx(gt_graph)


def _compute_nx_distances(
    nx_graph: nx.Graph,
    sources: List[Any], targets: List[Any]
) -> np.ndarray:
    dist_array = np.zeros((len(sources), len(targets)))
    for i, sn in enumerate(sources):
        for j, en in enumerate(targets):
            try:
                dist_array[i, j] = nx.shortest_path_length(
                    nx_graph, source=sn, target=en)
            except nx.exception.NetworkXNoPath:
                dist_array[i, j] = np.inf
    return dist_array


def _compute_gt_distances(
    gt_graph: 'gt.Graph',
    sources: List[Any], targets: List[Any],
    inf_thres: float = 1e9
) -> np.ndarray:
    nodes = _get_gtgraph_nodes(gt_graph)

    source_indices = None \
        if sources == nodes \
        else [nodes.index(n) for n in sources]
    target_indices = None \
        if targets == nodes \
        else [nodes.index(n) for n in targets]

    # compute distances
    if source_indices is None:  # distances from all sources
        tmp = topology.shortest_distance(
            gt_graph, source=source_indices, target=target_indices)
        dist_array = tmp.get_2d_array(range(gt_graph.num_vertices()))
        dist_array = dist_array.astype(float)
        dist_array = dist_array.T
    else:  # distances from selected sources
        dist_array = np.zeros((
            len(source_indices),
            len(nodes) if target_indices is None else len(target_indices)
        ))
        for i, ns in enumerate(source_indices):
            tmp = topology.shortest_distance(
                gt_graph, source=ns, target=target_indices)
            dist_array[i, :] = tmp if isinstance(tmp, np.ndarray) else tmp.a

    # use proper infinity value
    dist_array[dist_array > inf_thres] = np.inf

    # handle graph with no nodes
    if dist_array.size == 0:
        dist_array = np.zeros((0, 0))

    return dist_array


def compute_node_distances(
    nx_graph: nx.Graph,
    sources: Optional[List[Any]] = None, targets: Optional[List[Any]] = None,
    fname: Optional[str] = None
) -> Dict[Any, Dict[Any, int]]:
    """ Efficiently compute node distances
    """
    sources = ls(sources or nx_graph.nodes())
    targets = ls(targets or nx_graph.nodes())

    if fname is not None and not fname.endswith('.npz'):
        fname += '.npz'

    # compute distances
    if fname is None or not os.path.exists(fname):
        if NETWORKX_FALLBACK:
            print(
                '[WARNING] graph-tool not installed. '
                'Falling back to networkx...',
                file=sys.stderr)

            dist_array = _compute_nx_distances(nx_graph, sources, targets)
        else:
            dist_array = _compute_gt_distances(
                convert_networkx_to_graphtool(nx_graph), sources, targets)

        if fname is not None:
            np.savez_compressed(
                fname,
                dist_array=dist_array,
                graph_nodes=ls(nx_graph.nodes()),
                graph_edges=_get_nxgraph_edges(nx_graph),
                sources=sources, targets=targets)
    else:
        print('Cached', fname)
        dist_array = np.load(fname)
        with np.load(fname) as data:
            dist_array = data['dist_array']
            loaded_graph_nodes = data['graph_nodes'].tolist()
            loaded_graph_edges = list(map(tuple, data['graph_edges']))
            loaded_sources = data['sources'].tolist()
            loaded_targets = data['targets'].tolist()

        # assert that expected values are used
        if (
            ls(nx_graph.nodes()) != loaded_graph_nodes or
            _get_nxgraph_edges(nx_graph) != loaded_graph_edges or
            sources != loaded_sources or
            targets != loaded_targets
        ):
            raise RuntimeError(
                'Invalid cache:\n'
                f' {ls(nx_graph.nodes())} != {loaded_graph_nodes}'
                '\nor\n'
                f' {_get_nxgraph_edges(nx_graph)} != {loaded_graph_edges}'
                '\nor\n'
                f' {sources} != {loaded_sources}'
                '\nor\n'
                f' {targets} != {loaded_targets}'
            )

    # sanity checks
    assert dist_array.shape == (len(sources), len(targets))

    # convert to dict
    dists = {
        source: {target: dist
                 for target, dist in zip(targets, target_arr)
                 if not np.isinf(dist)}
        for source, target_arr in zip(sources, dist_array)
    }

    return dists
