# -*- coding: utf-8 -*-
"""
Unittary tests about (supervised) classification

Created on Wed Aug 17 22:22:42 2016
@author: thomas_a
"""
import os
import unittest
import numpy as np
import random
from timeit import default_timer as timer

from sklearn.datasets import make_classification

from test import DIR_DATA, DIR_TMP, empty_folder
from maplearn.datahandler.loader import Loader
from maplearn.datahandler.packdata import PackData
from maplearn.filehandler.imagegeo import ImageGeo
from maplearn.filehandler.shapefile import Shapefile
from maplearn.ml.classification import Classification, TUNE_ALGO


class TestClassification(unittest.TestCase):
    """ 
    Unittary tests about (supervised) classification
    """

    def setUp(self):
        loader = Loader('iris')
        empty_folder(DIR_TMP)
        self.__data = PackData(X=loader.X[:,:2], Y=loader.Y,
                               data=loader.X[:,:2],
                               type='classification')
        self.__data.scale()
        self.__algos = ['knn', 'rforest']
        self.__algo = random.choice(self.__algos)
        self.__clf = Classification(data=self.__data, dirOut=DIR_TMP,
                                    algorithm=self.__algo, kfold=2)
        X, Y = make_classification(n_samples=30, n_features=3, n_informative=2,
                                   n_redundant=0, n_classes=2, shift=10)
        Y += 1
        self.__toy_data = PackData(X=X.astype('float16'), Y=Y,
                                   type='classification')
        self.__n_class = len(np.unique(self.__data.Y))

    def test_unknown_algorithm(self):
        """
        Try to use an unavailable algorithm
        """
        self.assertRaises(KeyError, Classification, self.__data, 'inexistant')

    def test_unknowns_algos(self):
        """
        Try to use several algorithms. Some exist and some others do not.
        """
        self.assertRaises(KeyError, Classification, self.__data,
                          algorithm=['lda', 'inexistant', 'nimporte'])

    def test_fit(self):
        """ 
        Training a classification algorithm -> should not raise an exception +
        attribute _fitted = True
        """
        clf = Classification(data=self.__data, dirOut=DIR_TMP,
                             algorithm=self.__algo)
        clf.fit_1(self.__algo)
        self.assertTrue(clf._fitted)
    
    def test_predict_1(self):
        """ 
        Apply supervised classification to data using one algorihm -> should
        not raise exception
        """
        self.__clf.fit_1(self.__algo)
        self.__clf.predict_1(self.__algo)
        self.assertIn(self.__algo, self.__clf.result.keys())
        self.assertLessEqual(len(np.unique(self.__clf.result[self.__algo])),
                             len(np.unique(self.__data.Y)))

    def test_optimize(self):
        """
        Try to optimize an algorithm. Should not raise an exception and spend
        less than 15sec. each
        """
        __thres = 15 # acceptable elapsed time
        i = random.choice(tuple(TUNE_ALGO.keys()))
        __clf = Classification(data=self.__toy_data, algorithm=i,
                               dirOut=DIR_TMP, kfold=2)
        _time = timer()
        __clf.optimize(i)
        _time = timer() - _time
        out_feat = i + '.optim'
        self.assertIn(out_feat, __clf.algorithm)
        if _time > __thres:
            self.fail('Algorithm %s took too long time (%.1fs.)' % (i, _time))
            self.assertLess(_time, __thres, '%s is too long: %.1fs.' % (i, _time))

    def test_few_algos(self):
        """ 
        Apply supervised classification using a few algorithms. Should not
        raise exception and results should appear in 'result' attribute
        """
        self.__clf.run(True)
        for i in self.__clf.algorithm:
            self.assertIn(i, self.__clf.result.columns)
            self.assertLessEqual(len(np.unique(self.__clf.result[i])),
                                 len(np.unique(self.__data.Y)))

    def test_without_samples(self):
        """
        Supervised classification needs samples. Give only 'data' (no X nor Y)
        to classification should raise an AttributeError
        """
        __lder = Loader('digits')
        __data = PackData(data=__lder.X, type='clustering')
        self.assertRaises(AttributeError, Classification, data=__data,
                          algorithm=self.__algo, dirOut=DIR_TMP)

    def test_image_without_samples(self):
        """
        Try to apply supervised classification to an image without samples ->
        should raise AttributeError
        """
        src = os.path.join(DIR_DATA, 'landsat_rennes.tif')
        img = ImageGeo(src)
        img.read()
        data = PackData(data=img.img_2_data(), type='classification')
        self.assertRaises(AttributeError, Classification, data=data,
                          algorithm=self.__algo, dirOut=DIR_TMP)

    def test_image(self):
        """
        Try to apply supervised classification to an image. Y labels are
        included into a 2nd image. X (samples' features) have to be extracted
        -> should not raise Exception. Output image should exist and contain
        the expected number of different labels
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        img.read()
        samples = ImageGeo(os.path.join(DIR_DATA,
                                        'samples_landsat_rennes.tif'))
        samples.read()
        y = samples.img_2_data()
        x = img.img_2_data()
        idx = y[y.columns[0]]>0
        x = x[idx]
        y = np.ravel(y[idx])

        data = PackData(X=x, Y=y, data=img.img_2_data(),
                        type='classification',
                codes={'urbain': 1, 'sol nu': 2, 'bois': 3, 'veg. basse': 4})
        clf = Classification(data=data, algorithm=self.__algo, kfold=2,
                             dirOut=DIR_TMP)
        clf.optimize(self.__algo)
        clf.run(True)
        img.data_2_img(clf.result, True)
        out_file = os.path.join(DIR_TMP, 'classif_img.tif')
        img.write(out_file)

        # Check the output image exists
        self.assertTrue(os.path.exists(out_file))
        img = ImageGeo(out_file)
        img.read()

        # Check the ouput image only contains integer values with the expected
        # number of different labels
        self.assertLessEqual(len(np.unique(img.data)), 4)

    def test_shapefile(self):
        """
        Classification supervisée appliquée à un shapefile
        """
        in_file = os.path.join(DIR_DATA, 'echantillon.shp')
        shp = Loader(in_file, features=['Brightness', ], label='ECH')
        shp.run()

        data = PackData(X=shp.X, Y=shp.Y, data=shp.aData,
                        type='classification',)
        clf = Classification(data=data, algorithm=self.__algo, kfold=2,
                             dirOut=DIR_TMP)
        clf.run(True)
        out_file = os.path.join(DIR_TMP, 'classif.shp')
        shp = Shapefile(in_file)
        shp.read()
        shp.write(out_file, clf.result)
        # vérifie que l'image existe et qu'il s'agit bien d'une matrice entière
        self.assertTrue(os.path.exists(out_file))

        shp = Shapefile(out_file)
        shp.read()

        # verifie le nombre de classes dans la classif
        self.assertLessEqual(len(np.unique(shp.data)), 3)

    def test_all_algos(self):
        """
        Try to fit every existing algorithms on a toy dataset
        -> each algorithm should spend less than a few seconds. 
        """
        __thres = 4 # acceptable elapsed time (seconds)
        __clf = Classification(data=self.__toy_data, algorithm=None,
                               dirOut=DIR_TMP, kfold=2)
        _timers = {}
        _longest = 0
        for i in __clf.algorithm:
            #TODO: remove this patch when bagging will be reasonnably fast
            #(later version of sciki-learn)
            if i == 'bag':
                continue
            _time = timer()
            __clf.fit_1(i)
            _time = timer() - _time
            self.assertTrue(__clf._fitted)
            if _time > __thres:
                _timers[i] = '%.1f' % _time
            if _time > _longest: _longest = _time
        if _longest > __thres:
            self.fail('%i algo(s) took too long:\n%s' % (len(_timers),
                                                         str(_timers)))

    def test_exclude_poor_classes(self):
        """
        Classes without enough individuals (n < kfold) should be ignored
        """
        loader = Loader('iris')
        # remove lots of individual from class '1'
        n_classes=len(np.unique(loader.Y))
        __y = loader.Y[48:]
        __x = loader.X[48:,:]
        __data = PackData(X=__x, Y=__y, data=loader.aData,
                               type='classification')
        clf = Classification(data=__data, algorithm=self.__algo,
                             dirOut=DIR_TMP)
        try:
            clf.run(False)
        except Exception as e:
            self.fail("Fail to use data with a class to exclude first\n%s" % e)
        self.assertEqual(len(np.unique(clf._data.Y)), n_classes - 1)

if __name__ == '__main__':
    unittest.main()
