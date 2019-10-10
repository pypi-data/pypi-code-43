import os
import unittest

import networkx as nx

from GN import GN
from GN_old import GN_OLD

class TestGN(unittest.TestCase):
    def test_gn_wrapper(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        g = nx.readwrite.gml.read_gml(os.path.join(current_dir, 'karate.gml'), label=None)
        gn = GN()
        gn.fit(g)
        
        n_nodes = len(g.nodes)
        # relabel nodes, starting from zero
        mapping = {i+1:i for i in range(n_nodes)}
        G = nx.relabel_nodes(g, mapping)
        gn_old = GN_OLD()
        gn_old.fit(G)
        
        self.assertEqual(len(gn.partition_list), len(gn_old.partition_list))
        for i in range(len(gn.partition_list)):
            self.assertEqual(gn.partition_list[i], gn_old.partition_list[i])
            
if __name__ == '__main__':
    unittest.main()
