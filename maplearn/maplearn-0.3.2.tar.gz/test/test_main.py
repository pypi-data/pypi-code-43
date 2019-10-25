# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 22:00:54 2015

@author: thomas_a
"""
from __future__ import print_function

import os
import unittest
from shutil import rmtree
import random

import numpy as np

from test import DIR_DATA, DIR_TMP, DIR_EX
from maplearn.filehandler.imagegeo import ImageGeo
from maplearn.filehandler.shapefile import Shapefile
from maplearn.app.main import Main
from maplearn.app.config import Config

def algo_alea(_type='classification'):
    """
    Returns a randomly chosen algorithm

    Arg:
        type (str): type of process (classification, regression or clustering)
    """
    if _type == 'classification':
        __algos = ['knn', 'nearestc', 'lda']
    return random.choice(__algos)

class TestMain(unittest.TestCase):
    """ Unitary tests about main application class
    """
    def setUp(self):
        for i in os.listdir(DIR_TMP):
            i = os.path.join(DIR_TMP, i)
            try:
                os.remove(i)
            except OSError:
                rmtree(i)
        src_data = os.path.join(DIR_DATA, 'landsat_rennes.tif')
        src_samples = os.path.join(DIR_DATA, 'samples_landsat_rennes.tif')
        self.__appli_img = Main(DIR_TMP, type='classification', kfold=2,
                                algorithm=algo_alea())
        self.__appli_img.load(src_samples)
        self.__appli_img.load_data(src_data)
        self.__appli_img.preprocess()
        self.__appli = Main(DIR_TMP, type='classification',
                            algorithm=algo_alea(), kfold=2)
        self.__appli.load('iris')
        self.__appli.preprocess(scale=True)

    def test_load_image(self):
        """
        loading samples from an image
        """
        self.assertGreater(self.__appli_img.dataset.X.shape[0], 0)
        self.assertEqual(self.__appli_img.dataset.X.shape[0],
                         self.__appli_img.dataset.Y.shape[0])

    def test_classification(self):
        """
        Apply classification on a known dataset
        """
        try:
            self.__appli.process(False)
        except Exception as e:
            self.fail(e)

    def test_clustering(self):
        """
        Apply clustering on a known dataset
        """
        ben = Main(DIR_TMP, type='clustering', algorithm='mkmeans')
        ben.load('iris')
        ben.preprocess()
        try:
            ben.process(False)
        except Exception as e:
            self.fail(e)
        finally:
            ben = None

    def test_regression(self):
        """
        Apply regression on a known dataset
        """
        ben = Main(DIR_TMP, type='regression', algorithm='lm', kfold=2)
        ben.load('boston')
        ben.preprocess()
        try:
            ben.process(False)
        except Exception as e:
            self.fail(e)
        finally:
            ben = None

    def test_classify_reducted(self):
        """
        Apply reduction to IRIS dataset and then classify
        """
        self.__appli.preprocess(reduction='lda')
        try:
            self.__appli.process(False)
        except Exception as e:
            self.fail(e)

    def test_classify_csv_image(self):
        """
        Classify an image, using samples loaded from a csv file
        """
        src_data = os.path.join(DIR_DATA, 'landsat_rennes.tif')
        src_samples = os.path.join(DIR_DATA, 'echantillon_rennes.csv')
        output = os.path.join(DIR_TMP, 'export_csv_img')
        __appli = Main(output, type='classification', kfold=2,
                       algorithm=algo_alea())
        __appli.load(src_samples, label='classe', label_id='classe_id')
        __appli.load_data(src_data)

        __appli.preprocess()
        __appli.process(True)
        __appli = None
        out_file = os.path.join(output, 'results', 'classification.tif')
        self.assertTrue(os.path.exists(out_file))

    def test_classify_image(self):
        """
        Supervised classification applied to an image
        """
        out_file = os.path.join(DIR_TMP, 'results', 'classification.tif')
        self.__appli_img.process(True)
        self.assertTrue(os.path.exists(out_file))
        img = ImageGeo(out_file)
        img.read()
        # check that the image contains integer values, and that the number of
        # unique values is as expected
        self.assertLessEqual(len(np.unique(img.data)), 4)

    def test_classify_shp(self):
        """
        Classification of a shapefile
        """
        out_file = os.path.join(DIR_TMP, 'results', 'classification.shp')
        __appli = Main(DIR_TMP, type='classification', kfold=2,
                       algorithm=algo_alea())
        __appli.load(os.path.join(DIR_DATA, 'echantillon.shp'),
                     features=None, label='ECH')
        __appli.load_data(os.path.join(DIR_DATA, 'data.shp'))
        __appli.preprocess()
        __appli.process(True)
        __appli = None

        # check that a shapefile containing result has been created
        self.assertTrue(os.path.exists(out_file))
        shp = Shapefile(out_file)
        shp.read()
        # check the content of the output shapefile
        self.assertLessEqual(len(np.unique(shp.data)), 3)

    def test_with_config(self):
        """
        Run main using config class
        """
        __cfg = Config(os.path.join(DIR_EX, 'example5.cfg'))
        # set kfold to 2 to speed up processing
        __cfg.process['kfold'] = 2
        __cfg.io['output'] = os.path.join(DIR_TMP, 'main_with_cfg')
        __ml = Main(__cfg.io['output'], codes=__cfg.codes, **__cfg.process)
        __params = {i: __cfg.io[i] for i in ('label', 'label_id', 'features',
                                             'na')}
        __ml.load(__cfg.io['samples'], **__params)
        __ml.load_data(__cfg.io['data'], features=__cfg.io['features'])
        __ml.preprocess(**__cfg.preprocess)
        __ml.process(optimize=__cfg.process['optimize'],
                     predict=__cfg.process['predict'])
        out_file = os.path.join(__cfg.io['output'], 'results',
                                '%s.shp' % __cfg.process['type'])
        __ml = None
        __cfg = None
        self.assertTrue(os.path.exists(out_file))

if __name__ == '__main__':
    unittest.main()
