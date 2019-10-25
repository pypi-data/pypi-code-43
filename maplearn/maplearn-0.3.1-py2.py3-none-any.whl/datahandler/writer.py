# -*- coding: utf-8 -*-
"""
**Writes data into a file**


This class is to be used with PackData. It puts data into one file (different
formats are useable).


"""
from __future__ import print_function
import os

import pandas as pd

from maplearn.filehandler.shapefile import Shapefile
from maplearn.filehandler.excel import Excel
from maplearn.filehandler.imagegeo import ImageGeo

from maplearn import logger


class Writer(object):
    """
    Writes data in a file (different formats available)
    
    Args:
        * path (str): path towards the file to write data into
        * **kwargs:
            * origin (str): path to the original file used as a model 
    """
    def __init__(self, path=None, **kwargs):
        self.__path = None
        self.__driver = None
        self.__origin = None
        if 'origin' in kwargs:
            if not os.path.exists(kwargs['origin']):
                raise IOError('Missing origin file : %s', kwargs['origin'])
            self.__origin = kwargs['origin']
        self.path = path

    @property
    def path(self):        
        return self.__path

    @path.setter
    def path(self, path):
        if path is not None:
            self.__path = str(path).strip()
            logger.info('Output defined as %s', self.__path)
            self.__to_file()

    def __to_file(self):
        """
        Accesses the file specified in the constructor, before writing into it
        """
        logger.info('Looking driver for %s', self.__path)
        s_ext = os.path.splitext(self.__path)[1].lower()
        
        if s_ext in ['.xls', '.xlsx']:
            self.__driver = Excel(None)
            return None            
        if s_ext == '.shp':
            self.__driver = Shapefile(self.__origin)
        elif s_ext in ['.tif', '']:
            self.__driver = ImageGeo(self.__origin)
        else:
            raise IOError("Unknown format file: %s" % self.__path)
        if self.__driver is not None:
            self.__driver.open_()
        
        if self.__origin is not None:
            self.__driver.read()

    def run(self, data, path=None, na=None, dtype=None):
        """
        Writes data into a file
        
        Args:
            * data (pandas dataframe): dataset to write
            * path (str): path towards the file to write data into
            * na : value used as a code for "NoData"
            * dtype (np.dtype): desired data type
        """
        self.path = path
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        __columns = list(data.columns) # keep columns for later
        if data.shape[1] <= 0:
            logger.warning('No data to save into %s', self.__path)
            return None
        if isinstance(self.__driver, ImageGeo):
            data = self.__driver.data_2_img(data, overwrite=True, na=na)
        if dtype is not None:
            try:
                data = data.astype(dtype)
            except:
                logger.warning('Unable to set dtype to %s' % dtype)
        logger.info('Writing data (%i, %i) into file %s...', data.shape[0],
                    data.shape[1], self.__path)
        self.__driver.write(path=self.__path, data=data, na=na,
                            columns=__columns)
        logger.info('Data saved in %s', self.__path)
