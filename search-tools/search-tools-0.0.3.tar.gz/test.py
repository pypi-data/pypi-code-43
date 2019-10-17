import unittest
import numpy as np

from search_tools.metrics import ndcg_at_k, dcg_with_rel, ranking_ndcg_at_k
from search_tools.metrics import ndcg_at_k_constructor, ranking_ndcg_at_k_constructor



class MetricsTest(unittest.TestCase):

    def test_dcg_with_rel(self):
        rels = [.5, .3, .6, .8]
        result = dcg_with_rel(rels)
        assert np.abs((result - 1.137)) < 0.01


    def test_ndcg_at_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) < 0.01

    def test_ndcg_at_k_with_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels, k=4)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) < 0.01

    def test_big_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels, k=10)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) < 0.01

    def test_little_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels, k=2)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) > 0.01

    def test_ndcgatk_with_zeros(self):
        rels = [0, 0, 0, 0]
        result = ndcg_at_k(rels, k=None)
        assert result == 0

    def test_ordered_ndcgatk(self):
        best = [123, 332, 101, 100, 777, 9, 456]
        best = [str(x) for x in best]
        other = [101, 456, 332, 100, 999]
        other = [str(x) for x in other]

        return ranking_ndcg_at_k(best, other, k=None)

    def test_constructors(self):
        func = ndcg_at_k_constructor(k=5)
        func = ranking_ndcg_at_k_constructor(k=5)

if __name__ in "__main__":
    unittest.main()
