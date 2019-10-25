# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 18:57:34 2016

@author: thomas_a
"""
import os
import unittest
import random

import numpy as np
import pandas as pd

from test import DIR_DATA, DIR_TMP
from maplearn.datahandler.loader import Loader
from maplearn.datahandler.writer import Writer
from maplearn.filehandler.csv import Csv
from maplearn.filehandler.shapefile import Shapefile
from maplearn.filehandler.imagegeo import ImageGeo


class TestLoader(unittest.TestCase):
    """
    Unittary tests about loading dataset from files or existing dataset
    """
    def test_missing_file(self):
        """
        Try to load dataset from a missing file -> IOError
        """
        self.assertRaises(IOError, Loader, '/fichier/inexistant')

    def test_dataset(self):
        """
        Try to load a dataset provided in scikit
        """
        data = random.choice(['boston', 'iris', 'digits'])
        loader = Loader(data)
        test = loader.X is None or loader.Y is None
        self.assertFalse(test)

    def test_dataset_feat(self):
        """
        Load a dataset provided in scikit and keep only a few features
        """
        __feat = ['sepal length (cm)', 'sepal width (cm)']
        loader = Loader('iris', features=__feat)
        self.assertEqual(loader.X.shape[1], len(__feat))
        self.assertEquals(__feat, loader.features)

    def test_unknown_ext(self):
        """
        Try to load dataset from a file with unknown extension -> IOError
        """
        self.assertRaises(IOError, Loader, '/fichier/inexistant.shp.xml')

    def test_shapefile(self):
        """
        Compare le chargement d'1 shapefile avec la classe
        dédiée et le résultat de la classe loader
        """
        src = os.path.join(DIR_DATA, 'echantillon.shp')
        shp = Shapefile(src)
        shp.read()
        loader = Loader(src, label='ECH')
        self.assertEqual(loader.aData.shape[0], shp.data.shape[0])
        self.assertEqual(loader.aData.shape[1], shp.data.shape[1] - 1)
        self.assertEqual(len(np.unique(loader.Y)), 3)

    def test_csv(self):
        """
        Loading a csv file using Loader or CSV class should give datasets:
            * with the same number of individuals (rows)
            * loader's one can contain the same number of features (columns)
              or less (label & label_id columns)
        """
        src = os.path.join(DIR_DATA, 'echantillon_rennes.csv')
        csv_file = Csv(src)
        csv_file.read()
        loader = Loader(src, label='classe', label_id='classe_id')
        self.assertEqual(loader.aData.shape[0], csv_file.data.shape[0])
        # 2 columns are excluded from loader's dataset (label + label_id)
        self.assertEqual(loader.aData.shape[1], csv_file.data.shape[1] - 2)

    def test_image(self):
        """
        Loading a raster using Loader or ImageGeo class should result with the
        same dataset
        """
        src = os.path.join(DIR_DATA, 'landsat_rennes.tif')
        img = ImageGeo(src)
        img.read()
        loader = Loader(src)
        self.assertEqual(loader.aData.shape[0],
                         img.data.shape[0] * img.data.shape[1])
        self.assertEqual(loader.aData.shape[1], img.data.shape[2])

    def test_na(self):
        """
        When loading a dataset with NA, they should be excluded from the output
        dataset
        """
        __df = pd.DataFrame({'label_id':[1, 2, 3] * 3,
                          'x':np.random.random(9), 'y':np.random.random(9),
                          'z':np.random.random(9)})
        __sel = (1, 3)
        __df.loc[__sel, ('x', 'y', 'z')] = 999
        __file = os.path.join(DIR_TMP, 'na.csv')
        __df.to_csv(__file, index=False)
        l = Loader(__file, label_id='label_id', na=999)
        #self.assertEqual(l.aData.shape[0], __df.shape[0] - len(__sel))
        #self.assertEqual(l.df.shape[0], __df.shape[0] - len(__sel))
        self.assertEqual(l.X.shape[0], __df.shape[0] - len(__sel))

    def test_na_image(self):
        """
        When loading an image with NA, they should be excluded from the output
        dataset        
        """
        src = os.path.join(DIR_DATA, 'landsat_rennes.tif')
        img = ImageGeo(src)
        img.read()
        ori_size = (img.data.shape[0]*img.data.shape[1])
        k = 200
        img.data[:k,:k,:] = 255
        __file = os.path.join(DIR_TMP, 'img_na.tif')
        img.write(__file)
        loader = Loader(__file, na=255)
        self.assertNotEqual(loader.df.shape[0], ori_size)
        self.assertEqual(loader.df.shape[0], ori_size-k**2)

    def test_reserved_column_names(self):
        """
        Try to load a dataset with columns that could be an issue:
        * label
        * label_id
        """
        df1 = pd.DataFrame({'label_id':[1, 2, 3] * 3,
                          'label':['a', 'b', 'c'] * 3,
                          'x':np.random.random(9), 'y':np.random.random(9),
                          'z':np.random.random(9)})
        tmp_file = os.path.join(DIR_TMP, 'reserved_names.csv')
        df1.to_csv(tmp_file, index=False)
        l = Loader(tmp_file, label_id='label_id', label='label')
        self.assertEqual(l.X.shape[1], 3)
        l = Loader(tmp_file, label='label')
        self.assertEqual(l.X.shape[1], 4)
        df2 = pd.DataFrame({'label':[1, 2, 3] * 3,
                          'label_id':['a', 'b', 'c'] * 3,
                          'x':np.random.random(9), 'y':np.random.random(9),
                          'z':np.random.random(9)})
        tmp_file = os.path.join(DIR_TMP, 'reserved_names2.csv')
        df2.to_csv(tmp_file, index=False)
        l = Loader(tmp_file, label_id='label', label='label_id')
        self.assertEqual(l.X.shape[1], 3)

if __name__ == '__main__':
    unittest.main()
