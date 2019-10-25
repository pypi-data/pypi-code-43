# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 21:48:26 2016

@author: thomas_a
"""
import os
import unittest
import numpy as np
from random import randint

from maplearn.datahandler.loader import Loader
from maplearn.datahandler.packdata import PackData
from test import DIR_TMP, DIR_DATA, empty_folder


class TestPackData(unittest.TestCase):
    """ Tests unitaires concernant les jeux de données
    """

    def setUp(self):

        loader = Loader('iris')
        empty_folder(DIR_TMP)
        self.__data = PackData(X=loader.X, Y=loader.Y, data=loader.aData, 
                               dirOut=DIR_TMP)

    def test_empty_pack(self):
        """
        Tries to create an empty packdata (x, y et data are None)
        """
        self.assertRaises(ValueError, PackData)
    
    def test_features(self):
        """
        Check features are available from Packdata class
        """
        __lder = Loader('iris')
        __data = PackData(X=__lder.X, Y=__lder.Y, data=__lder.aData,
                          features=__lder.features, dirOut=DIR_TMP)
        self.assertListEqual(__lder.features, __data.features)

    def test_features_after(self):
        """
        Check features can be set after loading data
        """
        __lder = Loader('iris')
        __data = PackData(X=__lder.X, Y=__lder.Y, data=__lder.aData,
                          dirOut=DIR_TMP)
        # number of features
        __n = __data.X.shape[1]
        self.assertListEqual(__data.features, [str(i) for i in range(__n)])
        __data.features = __lder.features
        self.assertListEqual(__data.features, __lder.features)

    def test_wrong_nb_features(self):
        """
        Assign features with length different to number of features 
        -> indexError 
        """
        try:
            self.__data.features = [i for i in range(100)]
        except IndexError:
            pass
        else:
            self.fail('Wrong features have been assigned')
        
    def test_from_scratch(self):
        """
        Creating a full PackData (X, Y, data) from scratch
        """
        n_feat = randint(1, 10)
        n_ind = randint(7, 10)
        y = np.random.randint(1, 10, size=n_ind)
        x = np.random.random((n_ind, n_feat))
        data = np.random.random((n_ind, n_feat))
        ds = PackData(x, y, data)
        self.assertEqual(x.shape, ds.X.shape)
        self.assertEqual(y.shape, ds.Y.shape)
        self.assertEqual(data.shape, ds.data.shape)

    def test_load_from_shp(self):
        src = os.path.join(DIR_DATA, 'echantillon.shp')
        loader = Loader(src, label='ECH')
        ds = PackData(loader.X, loader.Y, data=loader.aData)
        self.assertEqual(len(np.unique(ds.Y)), 3)

    def test_xy_wrong_dim(self):
        """
        Loading X & Y with different number of features -> IndexError
        """
        y = np.random.randint(1, 10, size=10)
        x = np.random.random((5, 5))
        self.assertRaises(IndexError, PackData, x, y)
        self.assertRaises(IndexError, self.__data.load, x)

    def test_xy_data_wrong_dim(self):
        """
        Chargement d'un jeu de données complet (X, Y, data) où data
        a des dimensions incompatibles avec X
        """
        y = np.random.randint(1, 10, size=10)
        x = np.random.random((10, 5))
        data = np.random.random((10, 6))
        self.assertRaises(IndexError, PackData, x, y, data)

    def test_balance(self):
        """
        Rééquilibrage d'un échantillon déséquilibré
        """
        y = np.concatenate((np.ones(40, dtype=np.int),
                           np.random.randint(2, 10, size=10)))
        x = np.random.random((50, 5))
        pckdata = PackData(X=x, Y=y)
        pckdata.balance()
        print(pckdata.classes)
        self.assertLess(pckdata.Y.shape[0], 50)

    def test_scale(self):
        """
        Mise à l'échelle
        """
        try:
            self.__data.scale()
        except:
            self.fail("Scaling raised an exception")

    def test_reduct_tranform(self):
        """
        PCA transformation of a packdata
        """
        pd = self.__data
        i = randint(1, pd.X.shape[1])
        pd.reduit('pca', ncomp=i)
        self.assertEqual(pd.X.shape[1], i)

    def test_balance_few_classes(self):
        """
        Rééquilibrage d'un échantillon déséquilibré avec que 2 classes
        """
        y = np.concatenate((np.ones(40, dtype=np.int),
                           np.random.randint(2, 3, size=10)))
        x = np.random.random((50, 5))
        pckdata = PackData(X=x, Y=y)
        pckdata.balance()
        print(pckdata.classes)
        self.assertLess(pckdata.Y.shape[0], 50)

if __name__ == '__main__':
    unittest.main()
