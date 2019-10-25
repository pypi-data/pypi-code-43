# -*- coding: utf-8 -*-
"""
Shapefile reader and writer


With this class, you can read a shapefile or more precisely get attributes from
a shapefile. You can also write a new shapefile using geometry from an original
shapefile and adding the attributes you want.

Examples:

    >>> shp = Shapefile(os.path.join('maplearn path', 'datasets', 
                                     'echantillon.shp'))
    >>> shp.read()
    >>> print(shp.data)

TODO: 
    Guess character encoding in shapefile's attributes
"""
#from __future__ import unicode_literals

import os
import logging
#import unicodedata

import pandas as pd
import numpy as np
from osgeo import ogr

ogr.GetUseExceptions()

from maplearn.filehandler.filehandler import FileHandler

from maplearn import logger

# NB: np.float128 incompatible with windows OS (?) => removed
DCT_OGR_TYPES = {ogr.OFTString: [str, ],
                 ogr.OFTInteger: [int, np.int, np.int8, np.int16, np.int32,
                                  np.int64],
                 ogr.OFTReal: [float, np.float, np.float16, np.float32,
                               np.float64]}

class Shapefile(FileHandler):
    """
    Handler to read and write attributes in a shapefile. It inherits from the 
    abstract class *FileHandler*.
    
    Attributes:
    
        * FileHandler's attributes
        * str_type (str): kind of geometry (polygon, point...)
        * lst_flds (list): list of fields in dataset
    """

    def __init__(self, path):
        super(Shapefile, self).__init__(path=path, format='Shapefile')
         # driver pour pouvoir lire/écrire un fichier shapefile
        self._drv = ogr.GetDriverByName('ESRI Shapefile')
        self.__ds = None
        self.__lyr = None
        self.str_type = None  # type de géométrie
        self.lst_flds = None
        self._nb_feat = 0

    def open_(self):
        """
        Opens the shapefile and put in __ds attribute, so attributes can then
        be read
        """
        FileHandler.open_(self)
        self.__ds = self._drv.Open(self.dsn['path'])
        self.__lyr = self.__ds.GetLayer()
        self._nb_feat = self.__lyr.GetFeatureCount()
        self.str_type = ogr.GeometryTypeToName(self.__lyr.GetGeomType())

        self.lst_flds = self.__lyr.GetFeature(0).keys()
        logger.info('Shapefile chargé : %i %s(s) - %i Attributs',
                     self._nb_feat, self.str_type, len(self.lst_flds))

    def read(self):
        """ 
        Reads attributes associated to entities in the shapefile
        
        Returns:
            Pandas Dataframe: data (attributes) available in the shapefile
        """
        FileHandler.read(self)
        self.data = pd.DataFrame(index=np.arange(self._nb_feat),
                                 columns=self.lst_flds)
        for i in range(self._nb_feat):
            feat = self.__lyr.GetFeature(i)
            for str_fld in self.lst_flds:
                self.data.set_value(i, str_fld, feat.GetField(str_fld))
        logger.info('Data read (%i*%i)', self.data.shape[0],
                     self.data.shape[1])
        return self.data

    def __get_fld_type(self, column):
        """
        Get the field type (ogr codes) according to (Pandas) dataframe field 
        type. This conversion is based on DCT_OGR_TYPES dictionnary.
        
        Args:
            column (str): column's name in dataframe which we should guess ogr
                          field type

        Returns:
            field type: field type compatible with ogr library
        """
        type_ogr = None
        if isinstance(self.data[column].dtypes, object):
            type_feat = type(self.data[column][0])
        else:
            type_feat = self.data[column].dtypes
        
        logger.debug('Looking for the field type of %s (%s)', column,
                     type_feat)

        if type_feat is None:
            logger.warning("Can't guess %s's field type => use string instead",
                           column)
            type_ogr = ogr.OFTString
        else:
            for k in DCT_OGR_TYPES.keys():
                if type_feat in DCT_OGR_TYPES[k]:
                    type_ogr = k
                    logger.debug('Found field type : %s', DCT_OGR_TYPES[k])
                    break
        if type_ogr is None:
            str_msg = 'Field %s : unknow type (%s)' % (column, type_feat)
            logger.critical(str_msg)
            raise TypeError(str_msg)
        return type_ogr

    def write(self, path=None, data=None, overwrite=True, **kwargs):
        """
        Write attributes (and only attributes) in a new shapefile, using
        geometries of an original shapefile.
        
        Args:
            * path (str): path to the shapefile to create and write
            * data (pandas DataFrame): dataset to write in the shapefile
            * overwrite (bool): should the output shapefile be overwritten ?
        """
        """
        if 'origin' in kwargs and not kwargs['origin'] is None:
            self.dsn['path'] = kwargs['origin']
            data = self.read()
        else:
            raise IOError('Cannot write shapefile without geometries')
        """
        FileHandler.write(self, path=path, data=data, overwrite=overwrite)

        # creates the new shapefile
        if overwrite and os.path.exists(path):
            self._drv.DeleteDataSource(path)
        ds_out = self._drv.CreateDataSource(path)

        if ds_out is None:
            raise IOError("Unable to create file: %s" % path)

        # creates the layer
        str_lyr = os.path.splitext(os.path.basename(path))[0]
        #A TypeError is raised when str_lyr contains a Unicode string that
        #cannot be converted to a const char * or when containing bytes
        #str(str_lyr) does the trick with Python 2/3
        lyr_out = ds_out.CreateLayer(str(str_lyr), geom_type=ogr.wkbPolygon,
                                     srs=self.__lyr.GetSpatialRef())

        # creates table (attributes)
        for name in data.columns:
            name = str(name)
            type_ogr = self.__get_fld_type(name)
            fdefn = ogr.FieldDefn(name, type_ogr)
            lyr_out.CreateField(fdefn)
            logger.debug('Column added to table definition : %s (%s)', name,
                         type_ogr)
        fld_defn = lyr_out.GetLayerDefn()
        logger.info('Table defined : %i columns', len(data.columns))

        # writing data
        feat_in = self.__lyr.GetNextFeature()
        i = 0
        while i < self._nb_feat:
            feat_out = ogr.Feature(fld_defn)
            feat_out.SetGeometry(feat_in.GetGeometryRef())
            for name in data.columns:
                name = str(name)
                try:
                    feat_out.SetField(name, data.at[i, name])
                except NotImplementedError:
                    feat_out.SetField(name, np.asscalar(data.at[i, name]))
            lyr_out.CreateFeature(feat_out)

            feat_in.Destroy()
            feat_out.Destroy()

            # incrementation
            feat_in = self.__lyr.GetNextFeature()
            i += 1
        logger.info('%i entities written in %s', i + 1, path)
        ds_out = None

    def __del__(self):
        super(Shapefile, self).__del__()
        self.__ds = None
        self.__lyr = None
