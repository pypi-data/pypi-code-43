# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:14:49 2016

@author: thomas_a
"""
import unittest
import os
import random
import numpy as np

from maplearn.filehandler.imagegeo import ImageGeo
from test import DIR_DATA, DIR_TMP


class TestImageGeo(unittest.TestCase):
    """
    Tests unitaires autour des images géographiques
    """

    def test_read(self):
        """
        Test de lecture
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        img.read()
        test = img.data.shape[0] == 674 and img.data.shape[1] == 561
        self.assertTrue(test)

    def test_copy(self):
        """
        Test de recopie d'une image
        """
        img_in = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        img_in.read()
        data_in = np.copy(img_in.data)
        img_in.write(os.path.join(DIR_TMP, 'landsat_rennes.tif'))
        img_in = None
        
        img_out = ImageGeo(os.path.join(DIR_TMP, 'landsat_rennes.tif'))
        img_out.read()
        self.assertEqual(img_out.data.shape, data_in.shape)
        self.assertTrue(np.alltrue(img_out.data == data_in))
        img_out = None

    def test_coord(self):
        """
        Test de conversion de coordonnees pixels <=> geographique
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        img.read()
        for _ in range(50):
            i = random.randint(0, img.data.shape[1])
            j = random.randint(0, img.data.shape[0])
            lon, lat = img.pixel2xy(j, i)
            self.assertEqual((j, i), img.xy2pixel(lon, lat))

    def test_coord_ul(self):
        """
        Test de conversion de coordonnees pixels <=> geographique, du coin
        haut-gauche
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        img.read()
        i = j = 0
        lon, lat = img.pixel2xy(j, i)
        self.assertEqual((j, i), img.xy2pixel(lon, lat))

    def test_coord_lr(self):
        """
        Test de conversion de coordonnees pixels <=> geographique, du coin
        bas à droite
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        img.read()
        j, i = img.data.shape[0], img.data.shape[1]
        lon, lat = img.pixel2xy(j, i)
        self.assertEqual((j, i), img.xy2pixel(lon, lat))

    def test_img_data(self):
        """
        Reformatte 1 image en jeux de données puis le retour
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        img.read()
        data_img = img.data_2_img(img.img_2_data())

        self.assertTrue((img.data == data_img).all())

    def test_export_classif(self):
        """
        Exporte une classification (matrice de nombres entiers)
        en utilisant la géographie d'une image source
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        out_file = os.path.join(DIR_TMP, 'test_export_classif.tif')
        img.read()
        classif = np.random.randint(1, 10, size=img.dims).astype(np.int8)
        img.write(out_file, data=classif, depth='uint8')
        img = ImageGeo(out_file)
        img.read()
        result = img.data
        self.assertTrue(result.dtype == 'uint8')
        self.assertTrue((img.data == classif).all())

    def test_export_many_bands(self):
        """
        Export an image with nbands > 6
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        out_file = os.path.join(DIR_TMP, 'img_bands.tif')
        img.read()
        size = (img.dims[0], img.dims[1], 7)
        classif = np.random.randint(1, 10, size=size).astype(np.int8)
        img.write(out_file, data=classif, depth='uint8')
        img = ImageGeo(out_file)
        img.read()
        result = img.data
        self.assertTrue(result.dtype == 'uint8')
        self.assertTrue((img.data == classif).all())

    def test_create_1band(self):
        """
        Creates a 1-band image from a multi-band image 
        """
        img = ImageGeo(os.path.join(DIR_DATA, 'landsat_rennes.tif'))
        out_file = os.path.join(DIR_TMP, 'img_1band.tif')
        i = random.randint(0,5)
        img.read()
        data = img.data[:,:,i]
        m = np.mean(data, axis=0)
        dims = (img.dims[0], img.dims[1], 1)
        # exports the 1st band
        img.write(data=data, path=out_file)
        img = None
        img = ImageGeo(out_file)
        img.read()
        #result = img.data
        self.assertTrue(os.path.exists(out_file))
        self.assertEqual(img.dims, dims)
        self.assertTrue(np.all(m == np.mean(img.data[:,:,0], axis=0)))
        

if __name__ == '__main__':
    unittest.main()
