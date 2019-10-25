# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 21:49:24 2017

@author: thomas_a
"""
import os
import unittest
import random
import re

from test import DIR_TMP
from maplearn.app.reporting import ReportWriter, str_synthesis, str_extend

class TestReporting(unittest.TestCase):
    """
    Unit tests about reporting class and associated functions
    """
    def test_str_synthesis(self):
        """
        Check that the synthesis of results (numbers) are given in string and
        well formatted
        """
        nbrs = [random.uniform(-10, 10) for i in range(10)]
        result = str_synthesis(nbrs)
        self.assertIsInstance(result, str)
        pattern = re.compile("-?\d+\.\d{0,2} \(\+/-\d+\.\d{0,2}")
        match = pattern.match(str(result)) is not None
        self.assertTrue(match, result)

    def test_str_extend(self):
        """
        Check that a number formatted in string with a given length is well
        formatted
        """
        nbr = round(random.uniform(-100, 100), 3)
        size = random.randint(10, 30)
        result = str_extend(nbr, size=size)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), size, result)

    def test_reportwriter(self):
        """
        Check that the ReportWriter creates a well parsed html file
        
        TODO : read one of the example file with config class
               Write and html based on metadata section
        """
        out_file = os.path.join(DIR_TMP, 'output')
        reporter = ReportWriter(out_file)
        reporter.write('test')
        reporter.close()
        self.assertTrue(os.path.exists(out_file + '.html'))

if __name__ == '__main__':
    unittest.main()
