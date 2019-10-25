# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:07:52 2016

@author: thomas_a
"""
import unittest
import os
import pandas as pd
import numpy as np

from maplearn.filehandler.shapefile import Shapefile
from test import DIR_DATA, DIR_TMP


class TestShapefile(unittest.TestCase):
    """ Tests unitaires de la classe Shapefile
    """

    def test_load(self):
        """
        Chargement d'un shapefile à partir d'un des fichiers exemples
        """
        shp = Shapefile(os.path.join(DIR_DATA, 'echantillon.shp'))
        shp.read()
        test = isinstance(shp.data, pd.DataFrame)
        self.assertTrue(test)

    def test_read(self):
        """
        Chargement d'un shapefile à partir d'un des fichiers exemples
        """
        shp = Shapefile(os.path.join(DIR_DATA, 'echantillon.shp'))
        shp.read()
        test = shp.data.shape[0] == 111 and shp.data.shape[1] == 6
        self.assertTrue(test)

    def test_copy(self):
        """
        Reecriture d'un shapefile à partir d'un des fichiers exemples
        """
        shp = Shapefile(os.path.join(DIR_DATA, 'echantillon.shp'))
        dims = shp.read().shape
        shp.write(os.path.join(DIR_TMP, 'echantillon.shp'), shp.data,
                  overwrite=True)
        shp = None
        shp = Shapefile(os.path.join(DIR_TMP, 'echantillon.shp'))
        shp.read()
        self.assertEqual(dims, shp.data.shape)

    def test_write(self):
        """
        Ecriture d'un shapefile à partir d'un jeu de données composée de 2
        colonnes
        """
        shp = Shapefile(os.path.join(DIR_DATA, 'echantillon.shp'))
        dims = shp.read().shape
        data = pd.DataFrame({'A': np.zeros(dims[0], dtype=np.int),
                              'B': np.ones(dims[0], dtype=np.int)})
        shp.write(os.path.join(DIR_TMP, 'echantillon.shp'), data,
                  overwrite=True)
        shp = None
        shp = Shapefile(os.path.join(DIR_TMP, 'echantillon.shp'))
        shp.read()
        self.assertEqual((dims[0], 2), shp.data.shape)

if __name__ == '__main__':
    unittest.main()
