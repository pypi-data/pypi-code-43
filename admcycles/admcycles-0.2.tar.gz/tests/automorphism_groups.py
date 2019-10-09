#*****************************************************************************
#       Copyright (C) 2019 Vincent Delecroix <vincent.delecroix@u-bordeaux.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  https://www.gnu.org/licenses/
#*****************************************************************************

import unittest
import itertools

from admcycles import stable_graph
from admcycles.stable_graph import StableGraph, GraphIsom

from utils.stable_graph_randomize import randomly_multiply_edges, randomly_add_loops, randomize_genera

# list of stable graphs to be tested
Glist = [
    # single vertex (not stable)
    StableGraph([0], [[]], []),

    # paths
    StableGraph([0, 0], [[1], [2]], [(1,2)]),
    StableGraph([0, 0, 0], [[1], [2,3], [4]], [(1,2), (3,4)]),
    StableGraph([0, 0, 0, 0], [[1], [2,3], [4,5], [6]], [(1,2), (3,4), (5,6)]),

    # cycles
    StableGraph([0, 0, 0], [[1,2], [3,4], [5,6]], [(2,3), (4,5), (6,1)]),
    StableGraph([0, 0, 0, 0], [[1,2], [3,4], [5,6], [7,8]], [(2,3), (4,5), (6,7), (8,1)]),

    # complete graphs
    StableGraph([0, 0, 0, 0], [[1,2,3], [4,5,6], [7,8,9], [10,11,12]],
            [(1,4),(2,7),(3,10),(5,8),(6,11),(9,12)])
]

class TestAutomorphisms(unittest.TestCase):
    def random_iterator(self, add_loop_proba=0.1, add_loop_repeat=2,
            multiply_edge_mult=2, multiply_edge_repeat=2,
            genera_max=5, genera_repeat=1):
        for G0 in Glist:
            yield G0
            for G1 in randomly_add_loops(G0, add_loop_proba, add_loop_repeat):
                yield G1
                for G2 in randomly_multiply_edges(G1, multiply_edge_mult, multiply_edge_repeat):
                    yield G2
                    for G3 in randomize_genera(G2, genera_max, genera_repeat):
                        yield G3

    def assertOldAndNewCoincide(self, G):
        r"""
        Check implementation using sage automorphism (the class functions
        ``vertex_automorphism_group`` and ``leg_automorphism_group``)
        versus Pixton original ``GraphIsom`` function.
        """
        if not isinstance(G, StableGraph):
            raise TypeError
        Isomlist = GraphIsom(G, G)
        Av = G.vertex_automorphism_group()
        Al = G.leg_automorphism_group()

        self.assertEqual(len(Isomlist), Al.cardinality())
        domv = Av.domain()
        doml = Al.domain()
        for autov, autol in Isomlist:
            gv = Av([autov[x] for x in domv])
            gl = Al([autol[x] for x in doml])
            self.assertEqual(G.leg_automorphism_induce(gl), gv)

    def assertCorrectlyLiftsAndProjects(self, G):
        r"""
        Check that ``G.leg_automorphism_induce(G.vertex_automorphism_lift(...))`` is
        identity.
        """
        Av = G.vertex_automorphism_group()
        Al = G.leg_automorphism_group()
        for _ in range(5):
            gv = Av.random_element()
            gl = G.vertex_automorphism_lift(gv)
            self.assertTrue(gl in Al)
            ggv = G.leg_automorphism_induce(gl)
            self.assertEqual(gv, ggv)

    def test_lifting(self):
        for G in self.random_iterator():
            self.assertCorrectlyLiftsAndProjects(G)

    def test_automorphisms(self):
        for G in self.random_iterator(add_loop_proba=0.2, add_loop_repeat=2,
            multiply_edge_mult=2, multiply_edge_repeat=3,
            genera_max=5, genera_repeat=2):
            self.assertOldAndNewCoincide(G)

if __name__ == '__main__':
    unittest.main(verbosity=2)
