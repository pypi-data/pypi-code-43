# -*- coding: utf-8 -*-
"""
**Main class** *(one class to rule the others)*

This class is the engine powering Mapping Learning. It uses every other classes
to load data, apply preprocesses and finally process the dataset, using one or
several algorithm(s). The results are synthetized and compared.

The class can apply classification, clustering and regression processes.

Examples:
    >>> from maplearn.app.main import Main

    * Apply 2 different classifications on a known dataset

    >>> ben = Main('.', type='classification', algorithm=['knn', 'lda'])
    >>> ben.load('iris')
    >>> ben.preprocess()
    >>> ben.process(True)

    * Apply every available clustering algorithm(s) on the same dataset

    >>> ben = Main('.', type='clustering')
    >>> ben.load('iris')
    >>> ben.preprocess()
    >>> ben.process(False) # do not predict results

    * Apply regression on another known dataset

    >>> ben = Main('.', type='regression', algorithm='lm')
    >>> ben.load('boston')
    >>> ben.preprocess()
    >>> ben.process(False) # do not predict results

"""
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import numpy as np
import pandas as pd

from maplearn.ml.classification import Classification
from maplearn.ml.clustering import Clustering
from maplearn.ml.regression import Regression
from maplearn.datahandler.loader import Loader
from maplearn.datahandler.packdata import PackData
from maplearn.datahandler.writer import Writer

# import maplearn's logger to add a filehandler later
from maplearn import logger

class Main(object):
    """
    Realizes every steps from loading dataset to processing

    Args:
        * dossier (str): output path where will be stored every results
        * **kwargs: parameters data and processing to apply on it

    Attributes:
        * dataset (PackData): dataset to play with
    """
    def __init__(self, dossier, **kwargs):
        self.dataset = None
        self.__machine = None
        self.__io = {'dossier': dossier, 'features': None, 'na':np.nan}
        # create output folder and subfolders if needed
        if not os.path.exists(self.__io['dossier']):
            os.makedirs(self.__io['dossier'])
        for i in ['fig', 'results']:
            if not os.path.exists(os.path.join(self.__io['dossier'], i)):
                os.mkdir(os.path.join(self.__io['dossier'], i))
        # set ouput log file
        __log_file = os.path.join(self.__io['dossier'], 'maplearn.log')
        __fhandler = logging.FileHandler(filename=__log_file, mode='w')
        __fmt = logging.Formatter('%(asctime)s || %(levelname)s || %(module)s || %(message)s',
                                  datefmt='%Y-%m-%d %H:%M')
        __fhandler.setFormatter(__fmt)
        logger.addHandler(__fhandler)

        logger.info('maplearn initializing...')
        if 'na' in kwargs:
            if kwargs['na'] is not None:
                self.__io['na'] = kwargs['na']
        if 'codes' in kwargs:
            self.__dct_codes = kwargs['codes']
        else:
            self.__dct_codes = None
        self.__metadata = dict(process=kwargs['type'])
        self.__machine = eval(kwargs['type'], {"__builtins__": None},
                              {"classification": Classification,
                               "clustering": Clustering,
                               "regression": Regression})(data=None,
                               dirOut=self.__io['dossier'], **kwargs)
        logger.info('maplearn initialized')

    def load(self, source, **kwargs):
        """
        Loads samples (labels with associated features) used for training
        algorithm(s)

        Args:
            * source (str): file to load or name of an available datasets
            * **kwargs: parameters to specify how to use datasets (which
              features to use...)
        """
        print('##1. Chargement des donnees ##\n')
        for i in ['label', 'label_id', 'features']:
            if i not in kwargs:
                kwargs[i] = None
        loading = Loader(source, label_id=kwargs['label_id'],
                         label=kwargs['label'],
                         features=kwargs['features'],
                         codes=self.__dct_codes, na=self.__io['na'])
        print(loading)
        source = os.path.basename(os.path.splitext(source)[0])
        self.__io['source'] = loading.src
        if self.__dct_codes is not None:
            codes = self.__dct_codes
        else:
            codes = loading.nomenclature

        if kwargs['features'] is None:
            kwargs['features'] = loading.features

        self.dataset = PackData(loading.X, loading.Y, data=loading.aData,
                                codes=codes, source=source,
                                features=kwargs['features'],
                                type=self.__metadata['process'],
                                na=self.__io['na'],
                                dirOut=self.__io['dossier'])

        if 'source' in self.__io and self.__io['source']['type'] != 'ImageGeo':
            self.__io['features'] = kwargs['features']

    def load_data(self, source, label_id=None, label=None, features=None):
        """
        Load dataset to predict with previously trained algorithm(s)

        Args:
            * source (str): path to load or name of an available dataset
            * label_id (optional[str]): column used to identify labels
            * label (optional[str]): column with labels' names
            * features (list): columns to use as features. Every available
              columns are used if None
        """
        if not features is None and not self.__io['features'] is None:
            # select features to keep
            features = [i for i in features if i in self.__io['features']]
        elif not self.__io['features'] is None:
            features = self.__io['features']

        loading = Loader(source, label_id=label_id, label=label,
                         features=features, codes=self.__dct_codes,
                         na=self.__io['na'])
        print(loading)
        if features is None:
            features = loading.features

        if 'source' in self.__io and self.__io['source']['type'] == 'ImageGeo':
            y = self.dataset.data
            idx = y[:,0] > 0
            y = np.ravel(y[idx])
            x = np.copy(loading.aData[idx])
            self.dataset = PackData(x, y, data=loading.aData,
                                    type=self.__metadata['process'],
                                    source=source, features=features,
                                    na=self.__io['na'],
                                    dirOut=self.__io['dossier'])
        else:
            self.dataset.data = loading.aData
        self.__io['data'] = loading.src

    def preprocess(self, **kwargs):
        """
        Apply preprocessings tasks asked by user and give the dataset to the
        Machine Learning processor

        Args:
            **kwargs: available preprocessing tasks (scaling dataset, reducing
            number of features...)
        """
        print('##2. Pretraitement ##\n')
        b_plot = False
        # resample samples (to get about the same number of individuals in each
        # class (specific to classification)
        if 'balance' in kwargs:
            if kwargs['balance']:
                self.dataset.balance()
                b_plot = True

        # Normalize
        if 'scale' in kwargs:
            if kwargs['scale']:
                self.dataset.scale()
                b_plot = True

        # Reduce dataset's number of dimensions
        if 'reduce' in kwargs and kwargs['reduce'] is not None:
            if 'ncomp' not in kwargs:
                kwargs['ncomp'] = None
            else:
                if kwargs['reduce'] != 'refcv':
                    self.dataset.reduit(meth=kwargs['reduce'],
                                        ncomp=kwargs['ncomp'])
            b_plot = True

        # Separability analysis
        if 'separability' in kwargs:
            if kwargs['separability']:
                if 'metric' in kwargs:
                    metric = kwargs['metric']
                else:
                    metric = 'euclidean'
                try:
                    self.dataset.separability(metric=metric)
                except ValueError:
                    logger.error("Separability can't be analysed")

        if 'reduce' not in kwargs or kwargs['reduce'] != 'refcv':
            print(self.dataset)

        # load data to the machine learning engine
        if self.__machine.load(data=self.dataset) != 0:
            raise IOError("Error when loading data")

            if 'reduce' in kwargs and kwargs['reduce'] == 'refcv':
                self.__machine.rfe(None)
                print(self.dataset)

        if b_plot:
            self.dataset.plot('sig_pr')

    def process(self, predict=False, optimize=False, proba=True):
        """
        Apply algorithm(s) to dataset

        Args:
            * predict (bool): should the algorithm(s) be only fitted on
              samples or also predict results ?
            * optimize (bool): should maplearn look for best hyperparameters
              for the algorithm(s) ?
            * proba (bool): should maplearn try to get probabilities
              associated to predictions ?

        """
        print('##3. Traitement ##\n')

        # optimization of algorithm(s) (look for best parameters)
        if optimize:
            # optimized algorithm(s) are added to list of algorithm(s)
            __algos = self.__machine.algorithm
            for algo in __algos:
                self.__machine.optimize(algo)

        # predicts or not results (using all algorithms)
        self.__machine.run(predict)

        if predict:
            dtype = np.float32
            if self.__metadata['process'] != 'regression':
                dtype = np.int16
            result = pd.DataFrame(data=np.zeros((len(self.dataset.not_nas),
                                                 len(self.__machine.result.columns))),
                                  columns=self.__machine.result.columns)
            result.ix[self.dataset.not_nas] = self.__machine.result.values
            if proba:
                probas = pd.DataFrame(data=np.zeros((len(self.dataset.not_nas),
                                                 len(self.__machine.proba.columns))),
                                  columns=self.__machine.proba.columns)
                probas.ix[self.dataset.not_nas] = self.__machine.proba.values

            # writes results of predictions in a file
            if self.__io['data']['type'] in ['ImageGeo', 'Shapefile']:
                # With Image and Shp, more informations are needed
                #(about geometry) => need an "original" file
                writer = Writer(self.__io['data']['path'],
                                origin=self.__io['data']['path'])
            else:
                writer = Writer(self.__io['data']['path'])
            ext = os.path.splitext(self.__io['data']['path'])[-1]
            out_file = os.path.join(self.__io['dossier'], 'results',
                                    self.__metadata['process'] + ext)

            writer.run(data=result, path=out_file, na=self.__io['na'],
                       dtype=dtype)
            if proba:
                out_file = os.path.join(self.__io['dossier'], 'results',
                                        "probabilities" + ext)
                writer.run(data=probas, path=out_file, na=self.__io['na'],
                           dtype=np.float32)
        logger.info('Mapping Learning: end of processes')
        print('<p class="signature">powered by \
              <a href="https://bitbucket.org/thomas_a/maplearn/">Mapping \
              Learning</a></p></body>')

    def __del__(self):
        self.__machine = None
        self.dataset = None
        self.__metadata = None
        self.__io = None
