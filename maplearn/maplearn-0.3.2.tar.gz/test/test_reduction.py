# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 21:59:27 2016

@author: thomas_a
"""
import unittest
from random import randint

from test import DIR_TMP, empty_folder
from maplearn.datahandler.loader import Loader
from maplearn.datahandler.packdata import PackData
from maplearn.ml.reduction import Reduction


class TestReduction(unittest.TestCase):
    """ Tests unitaires de la classe Reduction
    """

    def setUp(self):
        loader = Loader('iris')
        empty_folder(DIR_TMP)
        self.__data = PackData(X=loader.X, Y=loader.Y, data=loader.aData)

    def test_unknown_algorithm(self):
        """
        Essaie d'utiliser une classification non disponible
        """
        self.assertRaises(KeyError, Reduction, None, 'inexistant')

    def test_set_vector(self):
        """
        Essaie d'affecter un vecteur au lieu d'un Packdata
        """
        i = randint(1, 7)
        self.assertRaises(TypeError, Reduction, i, 'pca')

    def test_pca(self):
        """
        Vérifie que la dimension du jeu de données réduit correspond bien à
        nos attentes
        """
        i = randint(1, self.__data.X.shape[1])
        r = Reduction(data=self.__data, algorithm='pca', ncomp=i,
                      dirOut=DIR_TMP)
        r.run()
        self.assertEqual(r.algorithm[0], 'pca')
        self.assertEqual(r.result['data'].shape[1], i)

    def test_lda_ss_echantillons(self):
        """
        Essaie d'appliquer la LDA alors que le jeu de données ne contient pas
        d'échantillons => renvoie le jeu de données d'origine
        """
        data = self.__data
        data.Y = None
        r = Reduction(data=data, algorithm='lda', ncomp=3, dirOut=DIR_TMP)
        self.assertRaises(TypeError, r.run())

    def test_lda(self):
        """
        Reducing dimensions using LDA
        Check if number of dimensions matches the expected number of dimensions
        """
        i = randint(1, self.__data.X.shape[1])
        r = Reduction(data=self.__data, algorithm='lda', ncomp=i,
                      dirOut=DIR_TMP)
        r.run()
        self.assertEqual(r.algorithm[0], 'lda')
        self.assertLessEqual(r.result['data'].shape[1], i)

    def test_rfe(self):
        """
        Reducing dimensions using RFE

        RFE(cv) estimates the optimal number of dimensions. Check if dimensions
        are really reduced
        """
        i = randint(1, self.__data.X.shape[1])
        r = Reduction(data=self.__data, algorithm='rfe', ncomp=i,
                      dirOut=DIR_TMP)
        r.run()
        self.assertEqual(r.algorithm[0], 'rfe')
        self.assertLessEqual(r.result['data'].shape[1], self.__data.X.shape[1])

    def test_kernel_pca(self):
        """
        Reducing dimensions using Kernel PCA
        """
        i = randint(1, self.__data.X.shape[1])
        r = Reduction(data=self.__data, algorithm='kernel_pca', ncomp=i,
                      dirOut=DIR_TMP)
        r.run()
        self.assertLessEqual(r.result['data'].shape[1], i)

if __name__ == '__main__':
    unittest.main()
