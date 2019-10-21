import unittest

import networkx as nx

from bhcd import BHCD

class TestBHCD(unittest.TestCase):
    def test_predict(self):
        # not implement
        pass
        
    def test_fit(self):
        G = nx.Graph()
        G.add_edge(0,1)
        G.add_edge(2,3)    
        a = BHCD()
        a.fit(G)
        self.assertTrue(a.predict(0, 1))
        self.assertTrue(a.predict(2, 3))
        print(a.tree)
    
if __name__ == '__main__':
    unittest.main()