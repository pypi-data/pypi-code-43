# -*- coding: utf-8 -*-
"""
**Loads data from a file**

This class aims to feed a PackData. It gathers data from one or more files or
uses known datasets stored in a library
"""
from __future__ import print_function
from __future__ import unicode_literals

import os

import pandas as pd
import numpy as np
from sklearn import datasets

from maplearn.filehandler.imagegeo import ImageGeo
from maplearn.filehandler.shapefile import Shapefile
from maplearn.filehandler.excel import Excel
from maplearn.filehandler.csv import Csv
from maplearn.app.reporting import icon_msg

from maplearn import logger


class Loader(object):
    """
    Loads data from a file or a known dataset

    Args:
        * source (str): path the file to load or name of a dataset ("iris" for
          example)
        * **kwargs: other attributes to drive loading (handles NA, labels...)

    Attributes:
        * src (dct): informations about the source (type, path...)
        * X: samples' features
        * Y: samples' labels
        * aData:
        * matrix: (needed when loading from a raster file)
        * features
        * nomenclature

    Examples:
        * Loading data from a know dataset:

            >>> ldr = Loader('iris')
            >>> print(ldr)
            >>> print(ldr.X, ldr.Y)
            >>> print(ldr.data)

        * Loading data from a file (here a shapefile):

            >>> ldr = Loader(os.path.join('maplearn_path', 'datasets',
                                          'ex1.xlsx'))
            >>> print(ldr)
            >>> print(ldr.X, ldr.Y)
    """
    __DATASETS = ['iris', 'digits', 'boston']  # liste des datasets dispo dans le code

    def __init__(self, source, **kwargs):
        self.src = {'type': 'unknown', 'path': str(source).strip()}
        self.__data = {'df':None, 'X':None, 'Y':None, 'matrix':None,
                       'aData':None}
        self.__args = {'label_id': None, 'label':None, 'features':None,
                       'nomenclature':None, 'na':np.nan}

        if 'codes' in kwargs:
            self.__data['nomenclature'] = kwargs['codes']

        for i in self.__args:
            if i in kwargs:
                self.__args[i] = kwargs[i]
                logger.debug('parameter %s set to %s', i, str(kwargs[i]))

        if self.src['path'] in self.__DATASETS:
            self.__from_dataset()
        else:
            self.__from_file()
            self.run(**kwargs)

    @property
    def df(self):
        """
        Dataframe loaded
        """
        return self.__data['df']

    @property
    def X(self):
        """
        Matrix of values corresponding to samples
        """
        return self.__data['X']

    @property
    def Y(self):
        """
        Vector of labels describing samples. Values to be predicted by machine
        learning algorithm
        """
        return self.__data['Y']

    @property
    def aData(self):
        """
        Data to predict
        """
        return self.__data['aData']

    @property
    def matrix(self):
        """
        Data served as a matrix. Needed when loading data from an image
        """
        return self.__data['matrix']

    @property
    def features(self):
        """
        List of features that contains the dataset
        """
        if self.__args['features'] is None and self.df is not None:
            self.__args['features'] = list(self.df.columns)
        return self.__args['features']

    @property
    def nomenclature(self):
        """
        Legends of labels. Dictionnary combining labels codes and their
        corresponding names
        """
        return self.__args['nomenclature']

    @nomenclature.setter
    def nomenclature(self, codes):
        self.__args['nomenclature'] = codes

    def __from_dataset(self):
        """
        Loads data from a known dataset included in scikit-learn library
        """
        if self.src['path'] not in self.__DATASETS:
            raise IOError("Source inconnue : %s" % self.src['path'])

        logger.info('Loading %s dataset...', self.src['path'])
        ds_load = eval('datasets.load_%s()' % self.src['path'])

        if 'feature_names' in ds_load.keys():
            __feat = list(ds_load.feature_names)
            self.__data['df'] = pd.DataFrame(data=ds_load.data,
                                             columns=__feat)
            # select features
            if self.__args['features'] is not None:
                self.__data['df'] = self.__data['df'].loc[:, self.__args['features']]
            self.__data['X'] =self.__data['df'].values
        else:
            self.__data['X'] = ds_load.data
        
        self.__data['Y'] = ds_load.target
        if np.any(self.__data['Y'] == 0):
            logger.debug('"0" is not accepted as a label (considered as NA) \
                         later => labels are recoded')
            self.__data['Y'] += 1

        logger.info('Dataset %s loaded : %i data * %i features',
                    self.src['path'], self.__data['X'].shape[0],
                    self.__data['X'].shape[1])

        # Création de la nomenclature (code classe : libelle de classe)
        if 'target_names' in ds_load.keys():
            libelles = [str(n) for n in ds_load.target_names]
            self.__data['nomenclature'] = dict(zip(np.unique(ds_load.target),
                                                   libelles))
        else:
            logger.warning('%s dataset has no target names', self.src['path'])

        self.src['type'] = 'dataset'

    def __from_file(self):
        """
        Loads data from a file
        """
        logger.info('Reading from file: %s', self.src['path'])
        s_ext = os.path.splitext(self.src['path'])[1].lower()
        if s_ext in ['.xls', '.xlsx']:
            self.src['type'] = 'Excel'
        elif s_ext == '.csv':
            self.src['type'] = 'Csv'
        elif s_ext == '.shp':
            self.src['type'] = 'Shapefile'
        elif s_ext == '.tif' or s_ext == '':
            self.src['type'] = 'ImageGeo'
        else:
            raise IOError("Unknown format file: %s" % self.src['path'])
        ofi_src = eval('%s(r"%s")' % (self.src['type'], self.src['path']))
        ofi_src.read()
        if self.src['type'] == 'ImageGeo':
            self.__data['matrix'] = ofi_src.data
            self.__data['df'] = ofi_src.img_2_data()
        else:
            self.__data['df'] = ofi_src.data
        
        # handle NA data value -> each row containing tue specified value is
        # set to NA
        self.__data['df'].replace(self.__args['na'], np.nan, inplace=True)
        ofi_src = None
        self.__args['features'] = list(self.__data['df'].columns)

    def __set_y(self):
        """
        Defines Y as a vector containing labels. Labels can be floating values
        or integer
        """
        if self.__args['label_id'] is not None:
            self.__data['Y'] = np.array(self.df[self.__args['label_id']])

        else:
            self.__data['Y'] = np.zeros(self.df.shape[0], dtype=np.int)
            labels = self.df[self.__args['label']].values
            for i in np.unique(labels):
                self.__data['Y'][np.where(labels == i)] = [k for (k, v) \
                    in self.__args['nomenclature'].items() if v == i]

    def __set_features(self):
        """
        Set dataset's features, and exclude features that are not to be used
        for fitting and prediction
        """
        features = self.features
        if features is None:
            logger.warning('No features found')
            return None

        logger.info('%i features found', len(features))

        # exclusion des colonnes correspondant aux classes
        for i in ['label_id', 'label']:
            if self.__args[i] is not None and self.__args[i] in features:
                features.remove(self.__args[i])
        logger.info('%i features will be used', len(features))
        self.__args['features'] = features

    def __set_nomenclature(self, label_id, label):
        """
        Set legends based on 2 columns

        Args:
            * label_id (str): column with codes of the labels
            * label (str): column with name of the labels
        """
        if label is not None and label_id is not None:
            codes = self.df[[label_id, label]].drop_duplicates()
            codes[label] = codes[label].astype(str)
            dct_codes = codes.set_index(label_id)[label].to_dict()
        elif label is not None and label_id is None:
            codes = pd.DataFrame(data=self.df[[label]].drop_duplicates())
            codes[label] = codes[label].astype(str)
            try:
                codes.sort_values(by=label, inplace=True)
            except AttributeError:
                #PATCH: deal with pandas version < 17
                codes = codes.sort(label)
            codes['label_id'] = range(1, codes.shape[0] + 1)
            dct_codes = codes.set_index('label_id')[label].to_dict()
        elif label is None and label_id is not None:
            codes = self.df[[label_id]].drop_duplicates()
            pd.DataFrame(data=codes)
            codes = codes[codes.notnull()]
            codes['label'] = codes[label_id].astype(str)
            dct_codes = codes.set_index(label_id)['label'].to_dict()
        else:
            dct_codes = None
        self.__args['nomenclature'] = dct_codes
        logger.info('Legend set')

    def run(self, **kwargs):
        """
        Gets samples (X with features and Y containing labels)

        Args:
            * **kwargs:
                * features (list): features to load
                * label (str): column with class labels (description)
                * label_id (str): column with labels codes
        """
        for i in self.__args:
            if i in kwargs:
                self.__args[i] = kwargs[i]

        # NOMENCLATURE : recuperation des codes et libelles des labels
        logger.debug('Building nomenclature [label_id:%s - label:%s]...',
                     self.__args['label_id'], self.__args['label'])
        if self.nomenclature is None:
            self.__set_nomenclature(self.__args['label_id'],
                                    self.__args['label'])

        self.__set_features()
        col = None
        # 1 (or 2) column(s) designated with labels => samples 
        if self.__args['label'] is not None or \
            self.__args['label_id'] is not None:
            # creation de X
            self.__data['X'] = self.df.loc[:, self.__args['features']].values
            self.__set_y()
            # Exclusion des NA (si NA dans X)
            col = [c for c in [self.__args['label'], self.__args['label_id']] if c is not None]
            if len(col) > 0:
                col = col[0]
            logger.info('Samples loaded: %i data * %i features',
                    self.__data['X'].shape[0], self.__data['X'].shape[1])

        self._select(col)
                    
        # no column with labels => DATA
        if self.__args['label'] is None and self.__args['label_id'] is None:
            if self.src['type'] == 'ImageGeo':
                logger.warning('Features can not be used with Images. Be sure \
                                features and bands share the same order.')
                self.__data['aData'] = self.df.values
            else:
                self.__data['aData'] = self.df.loc[:, self.__args['features']].values


    def _select(self, col):
        """
        Extracts individuals with corresponding samples and gives this
        distinction:
            * X & Y: features and associated labels => samples
            * aData: features of the whole dataset
        
        Arg:
            * column (str): name of the column that contains labels 
        """
        if col is not None:
            # exclude X, Y when Y is null
            idx = self.__data['df'][col].notnull().values
            if len(idx) > 0:
                self.__data['aData'] = np.copy(self.__data['X'])
                self.__data['X'] = self.__data['X'][idx, :]
                self.__data['Y'] = self.__data['Y'][idx]
        
            # exclude samples with NAS, then data
            idx = pd.isnull(self.__data['X']).any(1)
            if len(idx) > 0:
                self.__data['X'] = self.__data['X'][~idx, :]
                self.__data['Y'] = self.__data['Y'][~idx]

        if self.__data['df'] is not None:
            # handle NA in data
            self.__data['df'].dropna(inplace=True)

    def __str__(self):
        return icon_msg('**Source** : %s' % self.src['path'])
