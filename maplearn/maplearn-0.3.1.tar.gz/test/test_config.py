# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 22:00:54 2015

@author: thomas_a
"""
from __future__ import print_function

import os
import random
import unittest

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from test import DIR_TMP, DIR_EX
from maplearn.app.config import Config

class TestConfig(unittest.TestCase):
    """ 
    Unitary tests about configuration class
    """
    def setUp(self):
        i = random.randint(1, 8)
        self._cfg = Config(os.path.join(DIR_EX, 'example%i.cfg' % i))
        self._cfg.read()

    def test_missing_file(self):
        """ 
        Try to load configuration from a missing file
        """
        self.assertRaises(configparser.Error, Config, 'missing_file.cfg')

    def test_check(self):
        """
        check that one example of configuration file is OK
        """
        self.assertEqual(self._cfg.check(), 0)

    def test_check_examples(self):
        """
        check every examples of configuration file
        """
        for i in os.listdir(DIR_EX):
            if os.path.splitext(i)[-1] == '.cfg':
                __cfg = Config(os.path.join(DIR_EX, i))
                self.assertEqual(__cfg.check(), 0)
                __cfg = None

    def test_get_legend(self):
        """
        check that legend (code/names of classes) given in a configuration file
        is well interpreted (7 codes here)
        """
        __cfg = Config(os.path.join(DIR_EX, 'example2.cfg'))
        self.assertEqual(__cfg.check(), 0)
        self.assertEqual(len(__cfg.codes), 7)

    def test_write(self):
        """
        check that a configuration can be written into a cfg file
        """
        output = os.path.join(DIR_TMP, 'cfg_write1.cfg')
        self._cfg.write(output)
        self.assertTrue(os.path.exists(output))
        __cfg2 = Config(output)
        self.assertDictEqual(self._cfg.io, __cfg2.io)
        self.assertDictEqual(self._cfg.preprocess, __cfg2.preprocess)
        self.assertDictEqual(self._cfg.process, __cfg2.process)
        
    def test_write_legend(self):
        """
        Obtenir une legende (code/libelle des classes) à partir d'un fichier
        de configuration (avec une nomenclature contenant 7 codes)
        """
        __cfg_in = Config(os.path.join(DIR_EX, 'example2.cfg'))
        fichier = os.path.join(DIR_TMP, 'cfg_write2.cfg')
        __cfg_in.write(fichier)
        __cfg_out = Config(fichier)
        
        self.assertEqual(len(__cfg_in.codes), len(__cfg_out.codes))
        self.assertDictEqual(__cfg_in.codes, __cfg_out.codes)

    def test_set_parameters(self):
        """
        Update several parameters in a configuration object
        """
        for i in ['scale', 'balance', 'separability']:
            self._cfg.preprocess[i] = False
            self.assertFalse(self._cfg.preprocess[i])
            self._cfg.preprocess[i] = True
            self.assertTrue(self._cfg.preprocess[i])

        for i in [random.randint(1,10) for _ in range(2)]:
            self._cfg.io['na'] = i
            self.assertEqual(i, self._cfg.io['na'])
            self._cfg.preprocess['ncomp'] = i
            self.assertEqual(i, self._cfg.preprocess['ncomp'])
            self._cfg.process['kfold'] = i
            self.assertEqual(i, self._cfg.process['kfold'])
            self._cfg.process['n_clusters'] = i
            self.assertEqual(i, self._cfg.process['n_clusters'])

    def test_set_wrong_parameters(self):
        """
        Try to set an unexisting parameter in configuration -> KeyError
        expected
        """
        i = 'unexisting'
        with self.assertRaises(KeyError):
            self._cfg.io[i]
        with self.assertRaises(KeyError):
            self._cfg.io[i] = 'test'
            #self._cfg.preprocess[i] = "test"
            #self._cfg.process[i] = "test"

    def test_set_kfold(self):
        """
        Loads configuration and then update list of features
        """
        kfold = self._cfg.process['kfold']
        kfold += 1
        self._cfg.process['kfold'] = kfold
        self.assertEqual(self._cfg.process['kfold'], kfold)
        out_file = os.path.join(DIR_TMP, 'cfg_kfold.cfg')
        self._cfg.write(out_file)
        __cfg = Config(out_file)
        print(__cfg)
        self.assertEqual(__cfg.process['kfold'], kfold)
        
    def test_set_features(self):
        """
        Loads configuration and then update list of features
        """
        print(self._cfg.io['features'])
        self._cfg.io['features'] = 'a'
        self._cfg.read()
        test = isinstance(self._cfg.io['features'], list) and \
               len(self._cfg.io['features']) == 1
        print(self._cfg.io['features'])
        self.assertTrue(test)
        self._cfg.io['features'] = 'a,b'
        self._cfg.read()
        test = isinstance(self._cfg.io['features'], list) and \
               len(self._cfg.io['features']) == 2
        self.assertTrue(test)        
        self._cfg.io['features'] = ['a', 'b', 'c']
        self._cfg.read()
        test = isinstance(self._cfg.io['features'], list) and \
               len(self._cfg.io['features']) == 3
        self.assertTrue(test)
        print(self._cfg.io['features'])
    
    def test_change(self):
        """
        Loads an existing configuration, change a few parameters and check if
        they are really stored
        """
        output = os.path.join(DIR_TMP, 'cfg_change.cfg')
        self._cfg.process['distance'] = 'manhattan'
        self._cfg.preprocess['reduce'] = 'pca'
        self._cfg.write(output)
        self.assertTrue(os.path.exists(output))
        __cfg2 = Config(output)
        __cfg2.read()
        self.assertEqual(self._cfg.process['distance'],
                         __cfg2.process['distance'])
        self.assertEqual(self._cfg.preprocess['reduce'],
                         __cfg2.preprocess['reduce'])

if __name__ == '__main__':
    unittest.main()
