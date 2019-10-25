# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:12:07 2016

@author: thomas_a
"""
import unittest
import os

from maplearn.filehandler.filehandler import FileHandler
from test import DIR_DATA, DIR_TMP


class TestFileHandler(unittest.TestCase):
    """ Tests unitaires concernant les fichiers
    """

    def test_read_missing(self):
        """
        Lecture d'un fichier manquant
        """
        fh = FileHandler(path=os.path.join(DIR_DATA, 'nimporte.quoi'))
        self.assertRaises(IOError, fh.read)

    def test_write_existing(self):
        """
        Ecriture d'un fichier (sans droit d'ecraser)
        """
        str_path = os.path.join(DIR_TMP, 'file2overwrite')
        with open(str_path, 'w') as f:
            f.write('Fichier existant ne pouvant etre ecrase')

        fh = FileHandler(str_path)
        self.assertRaises(IOError, fh.write, data='efface', overwrite=False)

    def test_overwriting(self):
        """
        Reecriture d'un fichier
        """
        str_path = os.path.join(DIR_TMP, 'file2overwrite')
        with open(str_path, 'w') as f:
            f.write('Fichier qui va ecrase')

        fh = FileHandler(str_path)
        try:
            fh.write(data='efface', overwrite=True)
        except:
            self.fail("Exception levee lors de la reecriture")

if __name__ == '__main__':
    unittest.main()
