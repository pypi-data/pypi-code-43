#*****************************************************************************
#       Copyright (C) 2019 Vincent Delecroix <vincent.delecroix@u-bordeaux.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  https://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.prandom import random, randrange
from sage.all import floor

from admcycles.stable_graph import StableGraph

def randomize_genera(G, max_gen, repeat):
    r"""
    Return an iterator over stable graphs identical to ``G`` but where the
    genera of vertices have been randomized.

    INPUT:

    - ``G`` - a stable graph
    - ``max_gen`` - an upper bound on the genus (must be > 0)
    - ``repeat`` - number
    """
    n = len(G.genera)
    legs = G.legs
    edges = G.edges

    for _ in range(repeat):
        yield StableGraph([randrange(0, max_gen) for _ in range(n)], legs, edges)

def randomly_multiply_edges(G, max_mult, repeat):
    r"""
    Return an iterator that add multiplicity to edges in G

    INPUT:

    - ``G`` - a `StableGraph`
    - ``max_mult`` - maximum multiplicity
    - ``repeat`` - length of the iterator
    """
    if not G.edges:
        yield G
        return

    leg_to_vertex = {l: G.vertex(l) for l in G.leglist()}
    genera = G.genera
    orig_legs = G.legs
    orig_edges = G.edges
    orig_leg = G.maxleg + 1

    for _ in range(repeat):
        legs = [l[:] for l in orig_legs]
        edges = orig_edges[:]
        leg = orig_leg

        for e in orig_edges:
            k = floor(max_mult * random())
            if k:
                u = leg_to_vertex[e[0]]
                v = leg_to_vertex[e[1]]
                legs[u].extend(range(leg, leg + k))
                legs[v].extend(range(leg + k, leg + 2*k))
                edges.extend((l, l+k) for l in range(leg, leg + k))
                leg += 2*k

        yield StableGraph(genera, legs, edges)

def randomly_add_loops(G, p, repeat):
    r"""
    Return an iterator that add loops to vertices in the stable graph ``G``.

    INPUT:

    - ``G`` - a stable graph
    - ``p`` - probability to add a loop
    - ``repeat`` - length of the iterator
    """
    genera = G.genera
    orig_legs = G.legs
    orig_edges = G.edges
    orig_leg = G.maxleg + 1

    for _ in range(repeat):
        legs = [l[:] for l in orig_legs]
        edges = orig_edges[:]
        leg = orig_leg

        for v in range(len(genera)):
            if random() < p:
                legs[v].append(leg)
                legs[v].append(leg + 1)
                edges.append((leg, leg + 1))
                leg += 2

        yield StableGraph(genera, legs, edges)
