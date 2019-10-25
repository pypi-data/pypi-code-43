# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:24:50 2016

@author: thomas_a
"""
import unittest
import numpy as np

from maplearn.ml.distance import Distance


class TestDistance(unittest.TestCase):
    """ Tests unitaires de la classe Distance
    """

    def setUp(self):
        __n = 3
        self.__data = {'a': np.random.random(__n),
                       'b': np.random.random(__n),
                       'c': np.random.random(__n)}
        self.dist = Distance()

    def test_greaterzero(self):
        """
        Distance between 2 random vectors >= 0
        """
        d1 = self.dist.run(x=self.__data['a'], y=self.__data['b'])
        self.assertGreaterEqual(np.min(d1), 0)

    def test_symmetry(self):
        """
        Distance should be symmetrical: d(a,b) == d(b,a)
        """
        d1 = self.dist.run(x=self.__data['a'], y=self.__data['b'])
        d2 = self.dist.run(x=self.__data['b'], y=self.__data['a'])
        self.assertTrue(np.allclose(d1, np.transpose(d2)))

    def test_triangle_inequality(self):
        """
        Triangle inequality : d(a,c) <= d(a,b)+d(b,c)
        """
        d1 = self.dist.run(x=self.__data['a'], y=self.__data['c'])
        d2 = self.dist.run(x=self.__data['a'], y=self.__data['b'])
        d2 += self.dist.run(x=self.__data['b'], y=self.__data['c'])
        self.assertGreaterEqual(np.sum(d2), np.sum(d1))

if __name__ == '__main__':
    unittest.main()
