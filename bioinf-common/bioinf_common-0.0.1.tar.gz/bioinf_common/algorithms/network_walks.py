import random

from typing import TypeVar, Any, Set, Dict, Iterable, Union, Tuple, List

import numpy as np
import networkx as nx


T = TypeVar('T')


def random_walk(
    graph: nx.Graph, p: int = 1,
    num: int = 100, rw_len: int = 30,
    rw_type: str = 'normal'
) -> Iterable[Any]:
    """ `p` is the probability of choosing node in neighborhood.
        Otherwise another random node form the graph is chosen.
    """
    gcc = max(nx.connected_component_subgraphs(graph), key=len)
    gcc_nodes = set(gcc.nodes())

    if rw_type == 'normal':
        for _ in range(num):
            init_node = random.choice(list(gcc_nodes))
            last_node = init_node

            rw = set([init_node])
            while len(rw) < rw_len:
                if random.random() < p:
                    n_set = set(graph.neighbors(last_node))
                else:
                    n_set = gcc_nodes

                next_node = random.choice(list(n_set))
                rw.add(next_node)
                last_node = next_node

            assert len(rw) == rw_len, rw
            yield rw
    elif rw_type == 'dense':
        for _ in range(num):
            init_node = random.choice(list(gcc_nodes))

            rw = set([init_node])
            for _ in range(rw_len-1):
                if random.random() < p:
                    n_set = set([nei
                                 for n in rw
                                 for nei in graph.neighbors(n)])
                else:
                    n_set = gcc_nodes

                next_node = random.choice(list(n_set - rw))
                rw.add(next_node)

            assert len(rw) == rw_len, rw
            yield rw
    else:
        raise RuntimeError(f'Invalid RW-type: "{rw_type}"')


def degree_walk(
    graph: nx.Graph, p: int = 1,
    num: int = 100, rw_len: int = 30
) -> Iterable[Any]:
    """ Discard the graph's topology and walk according to
        node degree distribution.
        `p` is the probability of choosing according to node degree.
        With `1-p` choose uniformly.
    """
    gcc = max(nx.connected_component_subgraphs(graph), key=len)
    gcc_nodes = set(gcc.nodes())

    for _ in range(num):
        node_set = set([random.choice(list(gcc_nodes))])
        for _ in range(rw_len-1):
            if random.random() < p:  # choose degree-scaled
                nodes = list(gcc_nodes - node_set)
                degs = [graph.degree[n] for n in nodes]
                deg_sum = sum(degs)

                next_node = np.random.choice(
                    nodes, p=[d / deg_sum for d in degs])
            else:  # choose uniformly
                next_node = random.choice(list(gcc_nodes - node_set))

            node_set.add(next_node)

        assert len(node_set) == rw_len, node_set
        yield node_set


def go_walk(
    groups: Dict[str, Set[T]], p: int = 1,
    num: int = 100, rw_len: int = 30,
    return_used_pathways: bool = False
) -> Union[Iterable[T], Tuple[Iterable[T], List[str]]]:
    """ `p` is the probability of choosing node in same GO catgeory.
        Otherwise choose from other category.
    """
    term_list = set(groups.keys())

    for _ in range(num):
        # choose initial term
        cur_term = random.choice(list(term_list))

        walk: Set[T] = set()
        used_pathways = []
        for _ in range(rw_len):
            # make sure that current term has unused nodes
            cur_group_nodes = set(groups[cur_term])
            remaining_nodes = cur_group_nodes - walk

            while len(remaining_nodes) == 0:  # current term is exhausted
                cur_term = random.choice(list(term_list - {cur_term}))

                cur_group_nodes = set(groups[cur_term])
                remaining_nodes = cur_group_nodes - walk

            # choose gene from current term
            cur_node = random.choice(list(remaining_nodes))
            walk.add(cur_node)
            used_pathways.append(cur_term)

            # determine next term
            if random.random() < p:  # keep current term
                pass
            else:  # choose new term
                cur_term = random.choice(list(term_list - {cur_term}))

        assert len(walk) == rw_len, walk

        if return_used_pathways:
            yield walk, used_pathways
        else:
            yield walk
