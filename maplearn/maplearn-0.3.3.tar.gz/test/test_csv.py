# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:10:14 2016

@author: thomas_a
"""
import unittest
import os

import pandas as pd
import numpy as np

from test import DIR_DATA, DIR_TMP
from maplearn.filehandler.csv import Csv


class TestCsv(unittest.TestCase):
    """ Unitary tests about csv files
    """
    def setUp(self):
        self.__files = [os.path.join(DIR_DATA, 't11-t22.csv'), ]

    def test_read(self):
        """
        Lecture d'un fichier
        """
        _csv = Csv(self.__files[0])
        _csv.read()
        test = _csv.data.shape[0] == 366 and _csv.data.shape[1] == 17
        if not test:
            print(_csv.data.shape)
        self.assertTrue(test)

    def test_copy(self):
        """
        Rewrites an existing Csv File
        """
        _csv = Csv(self.__files[0])
        _csv.read()
        out_file = os.path.join(DIR_TMP, 'copy.csv')
        _csv.write(out_file)
        self.assertTrue(os.path.exists(out_file))
        csv_out = Csv(out_file)
        csv_out.read()
        self.assertEqual(_csv.data.shape, csv_out.data.shape)
        self.assertSequenceEqual(set(_csv.data.columns),
                                 set(csv_out.data.columns))

    def test_write(self):
        """
        Creates an Excel File from scratch
        """
        out_file = os.path.join(DIR_TMP, 'write.csv')
        csv = Csv(None)
        # creates a dataframe
        df = pd.DataFrame({ 'A' : 1,
                            'B' : pd.Timestamp('20130102'),
                            'C' : pd.Series(2,index=list(range(4)),dtype='int64'),
                            'D' : np.array([3] * 4,dtype='int64')})
        csv.write(path=out_file, data=df)
        csv = None
        self.assertTrue(os.path.exists(out_file))
        csv = Csv(out_file)
        csv.read()
        self.assertEqual(df.shape, csv.data.shape)
        self.assertSequenceEqual(set(df.columns), set(csv.data.columns))

if __name__ == '__main__':
    unittest.main()
