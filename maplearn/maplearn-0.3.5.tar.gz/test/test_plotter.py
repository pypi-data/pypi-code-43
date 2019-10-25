# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:17:10 2016

@author: thomas_a
"""
import os
import unittest
import time

import numpy as np
import pandas as pd

from test import DIR_TMP, empty_folder
from maplearn.datahandler.loader import Loader
from maplearn.datahandler.plotter import Plotter

SLOW_TEST_THRESHOLD = 0.5

class TestPlotter(unittest.TestCase):
    """ 
    Unit tests about plotting
    """
    def setUp(self):
        #empty_folder(DIR_TMP)
        loader = Loader('iris')
        self.__data = pd.DataFrame(data=loader.X, columns=loader.features)
        self.__Y = loader.Y
        self.__features = loader.features
        self.__plotter = Plotter(DIR_TMP)
        self._started_at = time.time()

    def test_boxplot(self):
        """
        Check the boxplot exists
        """
        self.__plotter.boxplot(self.__data)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    'boxplot.png')))

    def test_factorplot(self):
        """
        Check the factorplot exists
        """
        self.__plotter.factorplot(self.__data)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    'factorplot.png')))
    def test_summarized_plot(self):
        """
        Check the summarized plot exists
        """
        self.__plotter.plot_sum(self.__data)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    'plot_summarized.png')))

    def test_factorplot_digits(self):
        """
        Factorplot of a bigger dataset : digits
        """
        loader = Loader('digits')
        outfile = 'factorplot_dgt.png'
        __data = pd.DataFrame(data=loader.X, columns=loader.features)
        self.__plotter.factorplot(__data, file=outfile)
        loader = None
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    outfile)))

    def test_barplot(self):
        """
        Barplot
        """
        data = pd.DataFrame({'value':[57, 43, 31], 'features':['A', 'B', 'C']})
        self.__plotter.barplot(data, x='features', y='value')
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    'barplot.png')))

    def test_dist(self):
        """
        Distribution plot
        """
        test = np.random.random(100)*100
        test = test.astype('int')
        self.__plotter.dist(test)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig', 
                                                    'distribution.png')))
    
    def test_regression(self):
        """
        Regression plot (prediction vs. true)
        """
        __data = pd.DataFrame({'Mesures':np.random.random(100)*100,
                               'Prediction':np.random.random(100)*100})
        self.__plotter.regression(__data,
                                  title="Exemple de sortie de regression")
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig', 
                                                    'regression.png')))
        # compute residuals
        __res = __data['Mesures'] - __data['Prediction']
        self.__plotter.qqplot(data=__res.values)
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig', 
                                                    'qqplot.png')))
    
    def test_donut(self):
        """
        Donut (pie) chart
        """
        __data = np.random.randint(1, 5, size=20)
        __counts = np.unique(__data, return_counts=True)
        self.__plotter.donut(data=__counts[1], labels=__counts[0])
        self.assertTrue(os.path.exists(os.path.join(DIR_TMP, 'fig',
                                                    'donut.png')))

    def tearDown(self):
        elapsed = time.time() - self._started_at
        if elapsed > SLOW_TEST_THRESHOLD:
            print('{} ({}s)'.format(self.id(), round(elapsed, 2)))

if __name__ == '__main__':
    unittest.main()
