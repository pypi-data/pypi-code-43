# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:17:10 2016

@author: thomas_a
"""
import os
import unittest
import random
import time

from timeit import default_timer as timer

import numpy as np

from test import DIR_TMP#, empty_folder
from maplearn.datahandler.loader import Loader
from maplearn.datahandler.signature import Signature

SLOW_TEST_THRESHOLD = .5

class TestSignature(unittest.TestCase):
    """ Tests unitaires de la classe Signature
    """

    def setUp(self):
        #empty_folder(DIR_TMP)
        loader = Loader('iris')
        self.__data1 = np.copy(loader.X)
        self.__Y1 = np.copy(loader.Y)
        self.__feat1 = ['Sepal length', 'Sepal width', 'Petal length',
                        'Petal width']
        loader = None
        
        loader = Loader('digits')
        self.__data2 = np.copy(loader.X)
        self.__Y2 = np.copy(loader.Y)
        loader = None

        # example of "big" dataset
        n_feat = random.choice(range(5, 20))
        n_ind = 1000000
        self.__bigd = np.random.random((n_ind, n_feat))
        self.__y_bigd = np.random.randint(1, 10, size=n_ind)
        self._started_at = time.time()

    def test_boxplot(self):
        """
        Boxplot chart
        """
        out_file = "boxplot.png"
        sig = Signature(self.__data1, features=self.__feat1, output=DIR_TMP,
                        model='boxplot')
        sig.plot(file=out_file)
        sig = None
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig', out_file)))
    
    def test_boxplot_cl(self):
        """
        Makes a boxplot for each class
        """
        sig = Signature(self.__data1, features=self.__feat1, output=DIR_TMP,
                        model='boxplot')
        for i in np.unique(self.__Y1):
            out_file = 'boxplot_cl%i.png' % i
            self.assertNotEqual(sig.plot_class(self.__data1[self.__Y1==i,:], label=i,
                                           file=out_file), "")
            self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                        out_file)))
        sig = None

    def test_plot(self):
        """
        Plot
        """
        out_file = 'plot.png'
        sig = Signature(self.__data2, output=DIR_TMP, model='plot')
        sig.plot(file=out_file)
        sig = None
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    out_file)))

    def test_plot_cl(self):
        """
        Makes a plot for each class
        """
        sig = Signature(self.__data2, output=DIR_TMP, model='plot')
        __y = np.random.choice(np.unique(self.__Y2), 2, replace=False)
        for i in __y:
            out_file = 'plot_cl%i.png' % i
            sig.plot_class(self.__data2[self.__Y2==i,:], label=i,
                           file=out_file)
            self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                        out_file)))
        sig = None

    def test_factorplot_cl(self):
        """
        Makes a plot for each class
        """
        sig = Signature(self.__data1, features=self.__feat1, output=DIR_TMP,
                        model='plot')
        __y = np.random.choice(np.unique(self.__Y1), 2, replace=False)
        for i in __y:
            out_file = 'fp_cl%i.png' % i
            sig.plot_class(self.__data1[self.__Y1==i,:], label=i,
                           file=out_file)
            self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                        out_file)))
        sig = None
    
    def test_plot_bigdata(self):
        """
        Plot big data should not take too long
        """
        sig = Signature(self.__bigd, output=DIR_TMP, model='plot')
        out_file = 'plt_bigdata.png'
        _time = timer()
        sig.plot(file=out_file)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    out_file)))
        # each plot should spend  <= 3s.
        self.assertLessEqual(timer() - _time, 3)        
        
        # plot the most common class
        __counts = np.bincount(self.__y_bigd)
        __y = np.argmax(__counts)

        out_file = 'plt_bigD_cl%i.png' % __y
        _time = timer()
        sig.plot_class(self.__bigd[self.__y_bigd == __y,:], label=__y,
                          file=out_file)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig', out_file)))
        self.assertLessEqual(timer() - _time, 3)
        sig = None

    def test_boxplot_bigdata(self):
        """
        Boxplot big data should not take too long
        """
        sig = Signature(self.__bigd[:,:5], output=DIR_TMP, model='boxplot')
        out_file = 'bp_bigdata.png'
        _time = timer()
        sig.plot(file=out_file)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig', out_file)))
        # each plot should spend  <= 3s.
        self.assertLessEqual(timer() - _time, 3)        

        __y = np.random.choice(np.unique(self.__y_bigd), 2, replace=False)        
        for i in __y:
            out_file = 'bp_bigD_cl%i.png' % i
            _time = timer()
            sig.plot_class(self.__bigd[self.__y_bigd == i,:5], label=i,
                              file=out_file)
            self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig', out_file)))
            # each plot should spend  <= 3s.
            self.assertLessEqual(timer() - _time, 3)
        sig = None

    def tearDown(self):
        elapsed = time.time() - self._started_at
        if elapsed > SLOW_TEST_THRESHOLD:
            print('{} ({}s)'.format(self.id(), round(elapsed, 2)))

if __name__ == '__main__':
    unittest.main()
