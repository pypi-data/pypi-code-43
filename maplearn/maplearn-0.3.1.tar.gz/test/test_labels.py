# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 21:56:56 2016

@author: thomas_a
"""
import unittest
import numpy as np

from maplearn.datahandler.labels import Labels


class TestLabels(unittest.TestCase):
    """ Tests unitaires concernant les échantillons
    """

    def test_set_wrong_dims(self):
        """
        Essaie de créer des échantillons avec une matrice à plus d'une
        dimension
        """
        self.assertRaises(IndexError, Labels, np.arange(10).reshape(5, 2))

    def test_set_wrong_codes(self):
        """
        Essaie d'utiliser un dico mal forme
        Après un warning, les codes sont recodés de 1 à x
        """
        codes = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        ech = Labels(np.arange(1, 5), codes)
        np.testing.assert_array_equal([1,2,3,4], ech.Y)

    def test_set_y_codes(self):
        """
        Essaie de créer des échantillons avec une nomenclature incomplète
        => la nomenclature va être automatiquement complétée
        """
        ech = Labels(np.arange(10), codes={1: 'os1', 2: 'os2', 3: 'os3',
                                                10: 'os10', 11: 'os11'})
        self.assertEqual(len(ech.dct_codes), 12)

    def test_set_codes_doublon(self):
        """
        Utilise une nomenclature avec des doublons (même libellé, codes
        différents) => les doublons vont être recodés
        """
        ech = Labels(np.arange(10), codes={1: 'os1', 2: 'os1', 3: 'os3',
                                                10: 'os10', 11: 'os3'})
        self.assertEqual(len(ech.dct_codes), 10)

if __name__ == '__main__':
    unittest.main()
