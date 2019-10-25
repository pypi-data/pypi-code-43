# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:10:14 2016

@author: thomas_a
"""
import unittest
import os

import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np

from test import DIR_DATA, DIR_TMP
from maplearn.filehandler.excel import Excel


class TestExcel(unittest.TestCase):
    """ Tests unitaires concernant les fichiers Excel
    """

    def test_read(self):
        """
        Lecture d'un fichier
        """
        exc = Excel(os.path.join(DIR_DATA, 'ex1.xlsx'))
        exc.read()
        test = exc.data.shape[0] == 366 and exc.data.shape[1] == 9
        if not test:
            print(exc.data.shape)
        self.assertTrue(test)

    def test_copy(self):
        """
        Rewrites an existing Excel File
        """
        exc_in = Excel(os.path.join(DIR_DATA, 'ex1.xlsx'))
        exc_in.read()
        out_file = os.path.join(DIR_TMP, 'ex1.xlsx')
        exc_in.write(out_file)
        self.assertTrue(os.path.exists(out_file))
        exc_out = Excel(out_file)
        exc_out.read()
        self.assertEqual(exc_in.data.shape, exc_out.data.shape)
        self.assertSequenceEqual(set(exc_in.data.columns),
                                 set(exc_out.data.columns))        

    def test_write(self):
        """
        Creates an Excel File from scratch
        """
        out_file = os.path.join(DIR_TMP, 'scratch.xlsx')
        exc = Excel(None)
        # creates a dataframe
        df = pd.DataFrame({ 'A' : 1,
                            'B' : pd.Timestamp('20130102'),
                            'C' : pd.Series(2,index=list(range(4)),dtype='int64'),
                            'D' : np.array([3] * 4,dtype='int64')})
        exc.write(path=out_file, data=df)
        exc = None
        self.assertTrue(os.path.exists(out_file))
        exc = Excel(out_file)
        exc.read()
        self.assertEqual(df.shape, exc.data.shape)
        self.assertSequenceEqual(set(df.columns), set(exc.data.columns))

if __name__ == '__main__':
    unittest.main()
