import sys
import random

from typing import Sequence, Optional, Any, List

import numpy as np
import networkx as nx


def get_fraction_of_nonisolated_nodes(
    nodes: Sequence[Any], graph: nx.Graph,
    nc_type: str = 'overall'
) -> float:
    """ Control as
         * len(non_isolated_nodes) / len(all_nodes)
         * len(non_isolated_nodes) / (len(isolated_nodes) + 1)
    """
    ns = set(nodes)
    isolated_nodes = []
    non_isolated_nodes = []
    for n in nodes:
        neighs = graph.neighbors(n)
        if (ns-{n}).intersection(neighs):
            non_isolated_nodes.append(n)
        else:
            isolated_nodes.append(n)

    assert len(isolated_nodes) == len(set(isolated_nodes))
    assert len(non_isolated_nodes) == len(set(non_isolated_nodes))
    assert len(isolated_nodes) <= len(nodes)
    assert len(non_isolated_nodes) <= len(nodes)

    if nc_type == 'overall':
        return len(non_isolated_nodes) / len(nodes)
    elif nc_type == 'overiso':
        return len(non_isolated_nodes) / (len(isolated_nodes) + 1)
    else:
        raise RuntimeError(f'Invalid NC-type "{nc_type}"')


def compute_network_coherence(
    graph: nx.Graph, nodes: Sequence[Any],
    random_nodes: Optional[Sequence[Any]] = None, reps: int = 1000,
    fail_on_zero_std: bool = False, nc_type: str = 'overall'
) -> float:
    """ Compute z-score of non-isolated node fraction (network coherence)
    """
    if len(nodes) == 0:
        return np.nan

    assert len(set(nodes)) == len(nodes), nodes
    random_nodes = list(random_nodes or graph.nodes())

    rand_node_list: List[Any] = []
    while len(rand_node_list) < reps:
        cur = random.sample(random_nodes, len(nodes))

        assert len(set(cur)) == len(nodes)
        rand_node_list.append(cur)

    # network coherence
    act_num = get_fraction_of_nonisolated_nodes(nodes, graph, nc_type)
    rand_nums = [get_fraction_of_nonisolated_nodes(rn, graph, nc_type)
                 for rn in rand_node_list]

    # handle case where no z-score can be computed
    if np.std(rand_nums) == 0:
        if fail_on_zero_std or len(nodes) == 1:
            return np.nan
        else:  # retry if sensible
            next_rep_num = reps*3
            print(
                'Uniform random results, retrying with more iterations '
                f'({reps} -> {next_rep_num})', file=sys.stderr)
            return compute_network_coherence(
                graph, nodes, random_nodes=random_nodes,
                reps=next_rep_num, fail_on_zero_std=True)

    z_score = (act_num - np.mean(rand_nums)) / np.std(rand_nums)
    return z_score
