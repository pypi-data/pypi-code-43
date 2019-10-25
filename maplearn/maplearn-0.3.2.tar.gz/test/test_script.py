# -*- coding: utf-8 -*-
"""
Created on Tue May  2 21:56:14 2017

@author: thomas_a
"""

import os
import unittest

from test import DIR_TMP, DIR_EX, DIR_DATA

class TestScript(unittest.TestCase):
    """ 
    Unitary tests about using Mapping Learning as a script (maplearn binary)
    """
    def test_install(self):
        """ 
        Check if maplearn script exists
        """
        self.assertEqual(os.system('maplearn -h'), 0)

    def test_override_io_samples(self):
        """
        Use an example of configuration file (with samples stored in a file and
        override it with one of available samples ('iris')
        """
        cfg_file = os.path.join(DIR_EX, 'example2.cfg')
        _output = os.path.join(DIR_TMP, 'override_io_samples')
        result = os.system('maplearn -c %s --io-samples iris --io-output %s' 
                           % (cfg_file, _output))
        self.assertEqual(result, 0)

    def test_override_io(self):
        """
        Use an example of configuration file (with samples stored in a file and
        override every filepath arguments
        """
        _cfg = os.path.join(DIR_EX, 'example3.cfg')
        _sample = os.path.join(DIR_DATA, 'samples_landsat_rennes.tif')
        _data = os.path.join(DIR_DATA, 'landsat_rennes.tif')
        _output = os.path.join(DIR_TMP, 'override_io')
        s_cmd = "maplearn -c %s --io-samples %s --io-data %s \
                 --io-output %s" % (_cfg, _sample, _data, _output)
        print(s_cmd)
        result = os.system(s_cmd)
        self.assertEqual(result, 0)
        
    def test_several_algos(self):
        """
        Use an example of configuration file (with samples stored in a file and
        override it with one of available samples ('iris')
        """
        cfg_file = os.path.join(DIR_EX, 'example2.cfg')
        result = os.system('maplearn -c %s -algo=lda,nearestc' % cfg_file)
        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
