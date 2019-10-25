# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:22:42 2016

@author: thomas_a
"""
import os
import unittest
import numpy as np
import random
from timeit import default_timer as timer

from test import DIR_TMP, empty_folder
from maplearn.datahandler.loader import Loader
from maplearn.datahandler.packdata import PackData
#from maplearn.filehandler.imagegeo import ImageGeo
#from maplearn.filehandler.shapefile import Shapefile
from maplearn.ml.regression import Regression


class TestRegression(unittest.TestCase):
    """ Unit tests about regression
    """
    def setUp(self):
        loader = Loader('boston')
        empty_folder(DIR_TMP)
        self.__data = PackData(X=loader.X, Y=loader.Y, data=loader.aData)
        lst_algos = ['lm', 'tree']
        self.__algo = random.choice(lst_algos)

    def test_unknown_algo(self):
        """
        Try to use one unavailable algorithm => KeyError
        """
        self.assertRaises(KeyError, Regression, self.__data, 'inexistant')

    def test_unknowns_algos(self):
        """
        Try to use several algorithms (some available and some other not)
        => KeyError
        """
        self.assertRaises(KeyError, Regression, self.__data,
                          algorithm=['lm', 'inexistant', 'nimporte'])

    def test_fit(self):
        """ 
        Fitting using with one algorithm => _fitted = True
        """
        reg = Regression(data=self.__data, dirOut=DIR_TMP)
        reg.fit_1(self.__algo)
        self.assertTrue(reg._fitted)

    def test_predict(self):
        """ Prediction using one algorithm
        """
        reg = Regression(data=self.__data, algorithm=self.__algo,
                             dirOut=DIR_TMP)
        try:
            reg.run(False)
        except Exception as ex:
            print(self.__data)
            self.fail(ex)

    def test_optimize(self):
        """
        Try to optimize an algorithm. Should not raise an exception and spend
        less than 15sec. each
        """
        __thres = 15 # acceptable elapsed time
        __algo = 'tree'
        __reg = Regression(data=self.__data, algorithm=__algo,
                           dirOut=DIR_TMP)
        _time = timer()
        __reg.optimize(__algo)
        _time = timer() - _time
        out_feat = __algo + '.optim'
        self.assertIn(out_feat, __reg.algorithm)
        if _time > __thres:
            self.fail('Algorithm %s took too long time (%.1fs.)' \
                      % (__algo, _time))
            self.assertLess(_time, __thres, '%s is too long: %.1fs.' \
                            % (__algo, _time))
        __reg.predict_1(out_feat)
        self.assertGreater(np.max(__reg.result[out_feat]),
                           np.min(__reg.result[out_feat]))
        out_file = os.path.join(DIR_TMP, 'reg_result.csv')
        __reg.result.to_csv(out_file)
        self.assertTrue(os.path.exists(out_file))

    def test_algos(self):
        """ Prediction using several algorithms
        """
        reg = Regression(data=self.__data,
                             algorithm=['lm', ],
                             dirOut=DIR_TMP)
        for algo in reg.algorithm:
            try:
                reg.predict_1(algo)
            except Exception as ex:
                self.fail("Algo %s: failure\n%s" % (algo, ex))

    def test_nn(self):
        """ Prediction using neural network
        """
        reg = Regression(data=self.__data,
                             algorithm=['mlp', ],
                             dirOut=DIR_TMP)
        for algo in reg.algorithm:
            try:
                reg.predict_1(algo)
            except Exception as ex:
                self.fail("Algo %s: failure\n%s" % (algo, ex))


if __name__ == '__main__':
    unittest.main()
