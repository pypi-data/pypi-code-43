# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:05:01 2016

@author: thomas_a
"""
import os
import unittest
import numpy as np

from test import DIR_TMP
from maplearn.ml.confusion import Confusion


class TestConfusion(unittest.TestCase):
    """
    Unit tests about confusion matrices
    """
    def setUp(self):
        self.__y_true = np.random.randint(1, 15, 100)
        self.__y_pred = np.random.randint(1, 15, 100)

    def test_cm_kappa_eq1(self):
        """
        Une matrice de confusion calculéeà partir de la confrontation d'un
        vecteur avec lui-même => kappa = 1
        """
        cm = Confusion(self.__y_true, self.__y_true)
        cm.calcul_matrice()
        self.assertEqual(cm.kappa, 1)

    def test_kappa(self):
        """
        Le kappa est compris entre -1 et 1 : -1 <= k <= 1
        """
        conf_mat = Confusion(self.__y_true, self.__y_pred)
        conf_mat.calcul_matrice()
        self.assertGreaterEqual(conf_mat.kappa, -1)
        self.assertLessEqual(conf_mat.kappa, 1)

    def test_cm_markdown(self):
        """
        Export d'une matrice de confusion
        """
        conf_mat = Confusion(self.__y_true, self.__y_pred)
        conf_mat.calcul_matrice()
        f_txt = os.path.join(DIR_TMP, 'cm_test.txt')
        f_plot = os.path.join(DIR_TMP, 'cm_test.png')
        conf_mat.export(fTxt=f_txt, fPlot=f_plot)
        self.assertTrue(os.path.exists(f_txt), os.path.exists(f_plot))
    
    def test_print(self):
        """
        Prints a confusion matrix with or without output files mentionned
        """
        conf_mat = Confusion(self.__y_true, self.__y_pred)
        conf_mat.calcul_matrice()
        try:
            print(conf_mat)
        except:
            self.fail("Error: unable to print confusion matrix")

if __name__ == '__main__':
    unittest.main()
