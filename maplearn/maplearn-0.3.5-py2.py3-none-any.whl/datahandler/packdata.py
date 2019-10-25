# -*- coding: utf-8 -*-
"""
**PackData: a container for datasets**

A PackData contains:

* **samples** (Y and X) to fit algorithm(s)
    * Y is a vector with samples' labels
    * X is a matrix with samples' features
* **data** onto which algorithm(s) make prediction

PackData checks if samples are compatible with data (same features...) and can
be used later with Machine Learning algorithm(s)

Example:
    >>> import numpy as np
    >>> data = np.random.random((10, 5))
    >>> x = np.random.random((10, 5))
    >>> y = np.random.randint(1, 10, size=10)
    >>> ds = PackData(x, y, data)
    >>> print(ds)
"""
from __future__ import print_function
from __future__ import unicode_literals
from random import sample

import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_samples
from sklearn.preprocessing import StandardScaler

from maplearn.datahandler.labels import Labels
from maplearn.datahandler.plotter import Plotter
from maplearn.datahandler.signature import Signature
from maplearn.ml.reduction import Reduction
from maplearn.ml.distance import Distance
from maplearn.app.reporting import str_table


from maplearn import logger


pd.set_option('display.precision', 2)
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 700)

class PackData(object):
    """
    Dataset container with:

    * Y: a vector with labels of samples
    * X: matrix with features of samples
    * data: matrix with features to use for prediction

    Args:
        * X (array): 2d matrix with features of samples
        * Y (array): vector with labels of samples
        * data (array): 2d matrix with features
        * **kwargs: other parameters about dataset (features, na...)

    Attributes:
        * not_nas: vector with non-NA indexes
    """

    def __init__(self, X=None, Y=None, data=None, **kwargs):
        self.__data = {'X': None, 'Y': None, 'data': None}
        self.not_nas = None
        self.__metadata = {'type':None, 'codes': None, 'features': None,
                           'source': None, 'na': np.nan,
                           'outfile': '', 'images': '', 'dirOut':None}
        self.__lbl = None
        self.__metadata.update(kwargs)
        self.load(X=X, Y=Y, data=data, features=self.__metadata['features'])

    @property
    def X(self):
        """
        X (array): 2d matrix with features of samples
        """
        return self.__data['X']

    @X.setter
    def X(self, x):
        """
        Sets features of samples
        """
        if x is None:
            self.__data['X'] = None
            logger.debug('X (re)initialized')
            return self.__data['X']
        if x.ndim != 2:
            logger.critical('Samples features should be a 2d matrix')

        # X is stored
        self.__data['X'] = np.copy(x)

        if self.__metadata['features'] is None:
            self.features = self.__data['X']
        else:
            if self.__data['X'].shape[1] != len(self.__metadata['features']):
                str_msg = 'Features (%i) in conflict with X (%i)' \
                         % (len(self.__metadata['features']),
                            self.__data['X'].shape[1])
                logger.critical(str_msg)
                raise IndexError(str_msg)

    @property
    def Y(self):
        """
        Y (array): vector with labels of samples
        """
        return self.__data['Y']

    @Y.setter
    def Y(self, y):
        """
        Sets vector of samples' labels
        """
        if y is None:
            self.__data['y'] = None
            logger.debug('Y (re)initialized')
            return self.__data['Y']

        if isinstance(y, list):
            y = np.array(y)

        # check there are enough different classes
        if len(np.unique(y)) <= 1:
            raise ValueError('Number of classes too low : %i',
                             len(np.unique(y)))
        if y.ndim != 1:
            str_msg = 'Samples should be a vector. Got %id data.' % y.ndim
            raise ValueError(str_msg)

        if self.__metadata['type'] != 'regression':
            self.__lbl = Labels(y, self.__metadata['codes'],
                                self.__metadata['dirOut'])

        # Y is stored
        self.__data['Y'] = np.copy(y)

    @property
    def data(self):
        """
        data (array): 2d matrix with features
        """
        return self.__data['data']

    @data.setter
    def data(self, data):
        """
        Sets the features of data to predict

        Args:
            * data (array): data to set
        """
        if data is None:
            logger.debug('Data (re)initialized')
            self.__data['data'] = None
            return self.__data['data']

        if data.ndim not in [2, 3]:
            raise IndexError('Data should be a 2d/3d matrix. %i dimension is\
                             not accepted' % data.ndim)
        self.__data['data'] = np.copy(data)

        # gestion des na
        self.not_nas = np.all(self.__data['data'] != self.__metadata['na'],
                              axis=1)
        n_na = len(self.not_nas[self.not_nas == False])
        if n_na >= self.__data['data'].shape[0]:
            s_msg = 'All data are considered NA [%s]' % self.__metadata['na']
            logger.critical(s_msg)
            raise ValueError(s_msg)
        elif n_na > 0:
            logger.warning('%i/%i (%.1f%%) NA values detected', n_na,
                           self.__data['data'].shape[0],
                           (n_na * 100.) / self.__data['data'].shape[0])

        # data is stored
        self.__data['data'] = np.copy(self.__data['data'][self.not_nas, :])

        # features
        if self.__metadata['features'] is None:
            self.features = self.__data['data']
        else:
            if self.__data['data'].shape[1] != len(self.__metadata['features']):
                str_msg = 'Features (%i) in conflict with dataset (%i)' \
                           % (len(self.__metadata['features']),
                              self.__data['data'].shape[1])
                logger.critical(str_msg)
                raise IndexError(str_msg)

    @property
    def classes(self):
        """
        dict: labels classes and associated number of individuals
        """
        if self.Y is None or self.__metadata['type'] == 'regression':
            return None
        if self.__lbl.summary is None:
            self.__lbl.count()
        return self.__lbl.summary

    @property
    def features(self):
        """
        list: list of features of the dataset
        """
        if self.__metadata['features'] is None:
            if self.X is not None:
                self.features = self.X
            elif self.Y is not None:
                self.data = self.data
        return self.__metadata['features']

    @features.setter
    def features(self, items):
        """
        Sets the list of features

        Args:
            * items (list or array): list of features to set
        """
        if isinstance(items, list):
            __feat = [str(i) for i in items]
        elif isinstance(items, np.ndarray):
            __feat = [str(i) for i in range(items.shape[1])]
        elif isinstance(items, pd.DataFrame):
            __feat = [str(i) for i in items.columns]
        else:
            raise TypeError('Features should be given as a list, an array or \
                            a dataframe. Got %s' % type(items))
        if self.X is not None:
            n_feat = self.X.shape[1]
        elif self.data is not None:
            n_feat = self.data.shape[1]
        else:
            n_feat = len(__feat)
        if len(__feat) != n_feat:
            raise IndexError('Number of features (%i) given does not match \
                             size of data (%i)' % (len(__feat), n_feat))
        else:
            self.__metadata['features'] = __feat
        logger.info('Dataset with %i features',
                    len(self.__metadata['features']))

    def load(self, X=None, Y=None, data=None, features=None):
        """
        Loads data to the packdata

        Args:
            * X (array): 2d matrix with features of samples
            * Y (array): vector with labels of samples
            * data (array): 2d matrix with features
            * features (list): list of features

        """
        logger.debug('Loading data in PackData...')
        # samples are checked (if provided)
        if X is not None and Y is not None:
            # Check compatibility between X and Y (dimensions)
            if X.shape[0] != Y.shape[0]:
                str_msg = "Number of samples (%i) in conflict with \
                          number of datas (%i)" % (Y.shape[0], X.shape[0])
                logger.critical(str_msg)
                raise IndexError(str_msg)

            # Check if labels are non-values (<= 0)
            if self.__metadata['type'] == 'classification' and np.any(Y <= 0):
                logger.warning('Labels <= 0 are excluded')
                X = X[Y > 0, :]
                Y = Y[Y > 0]

        # samples are then loaded if provided
        if X is not None:
            self.X = X
        if Y is not None:
            if self.__metadata['type'] != 'regression':
                self.Y = Y.astype('int')
            else:
                self.Y = Y
        # then data is loaded (if provided)
        if data is not None:
            self.data = data
        # and finally, features are loaded (if provided)
        if features is not None:
            self.features = features

        logger.info('PackData loaded')
        self.__check()

    def __check(self):
        """
        Check compatibility between main properties of PackData:
        * X
        * Y
        * data
        """
        logger.debug('Checking dataset...')
        if self.X is None and self.Y is None and self.data is None:
            raise ValueError("Dataset is empty")

        # check compatibility based on number of features:
        if self.X is not None or self.Y is not None:
            if self.X.shape[0] != self.Y.shape[0]:
                raise IndexError("Numbers of features in data (%i) \
                                 and samples (%i) are different",
                                 self.X.shape[0], self.Y.shape[0])
        if self.data is not None and self.X is not None:
            if self.data.shape[1] != self.X.shape[1]:
                raise IndexError('Numbers of features in data (%i) and \
                                 samples (%i) are different',
                                 self.data.shape[1], self.X.shape[1])

        logger.info('Dataset checked => OK')

    def scale(self):
        """
        Normalizes data and X matrices
        """
        logger.debug('Normalizing dataset...')
        __scaler = StandardScaler(copy=True)
        __fitted = False
        for i in ('X', 'data'):
            if self.__data[i] is not None:
                if not __fitted:
                    __scaler.fit(self.__data[i])
                self.__data[i] = __scaler.transform(self.__data[i])
        logger.debug('Dataset normalized')

    def reduit(self, meth='lda', ncomp=None):
        """
        Reduces number of dimensions of data and X

        Args:
            * meth (str): reduction method to apply
            * ncomp (int): number of dimensions expected
        """
        logger.debug("Reducing dataset's dimensions...")

        red = Reduction(data=self, algorithm=meth,
                        features=self.features, ncomp=ncomp,
                        dirOut=self.__metadata['dirOut'])
        if self.data is not None:
            (self.__data['data'], self.__data['X'], self.__metadata['features']) = red.run()
        else:
            (self.__data['X'], _, self.__metadata['features']) = red.run()
        logger.info('Dataset reduced to %i dimensions',
                    len(self.__metadata['features']))

    def separability(self, metric='euclidean'):
        """
        Performs separability analysis between samples

        Arg:
            * metric (str): name of the distance used
        """
        logger.debug('Performing separability analysis (%s)...', metric)
        dist = Distance()
        mat_dist = dist.run(x=self.__data['X'], meth=metric)
        sep = silhouette_samples(X=mat_dist, labels=self.__data['Y'],
                                 metric="precomputed")
        print('\n## Analyse de separabilite (%s)\n' % metric)
        header = ['classe', 'mean', 'std', 'min', 'max', 'separable']
        dct_sep = {i:[] for i in header}
        for i in np.unique(self.__data['Y']):
            sep_cl = sep[np.where(self.__data['Y'] == i)]
            i = str(int(i))
            # Recode values (display)
            m_cl = np.mean(sep_cl)
            if m_cl > .5:
                str_msg = "++"
            elif m_cl > .25 and m_cl <= .5:
                str_msg = "+"
            elif m_cl < -.25 and m_cl >= -.5:
                str_msg = "-"
            elif m_cl < -.5:
                str_msg = "--"
            else:
                str_msg = ""
            dct_sep['classe'].append(i)
            dct_sep['mean'].append('%.2f' % m_cl)
            dct_sep['std'].append('%.2f' % np.std(sep_cl))
            dct_sep['min'].append('%.2f' % np.min(sep_cl))
            dct_sep['max'].append('%.2f' % np.max(sep_cl))
            dct_sep['separable'].append(str_msg)

        print(str_table(header=header, size=30, **dct_sep))
        logger.info('Separability analysis (%s) done', metric)

    def balance(self, seuil=None):
        """
        Balance samples and remove some individuals within the biggest classes.

        Args:
            * seuil (int): max number of samples inside a class
        """
        logger.debug('Balancing samples...')
        # NB: convert this in pd.Dataframe will make easier the rest of work...
        a_count = np.array(list(self.__lbl.summary.values()))
        if seuil is not None:
            seuil = int(seuil)
        else:
            # TODO : look for a reference to define this threshold
            if len(self.__lbl.summary) > 3:
                # default threshold = median *
                seuil = int(np.median(a_count) * 3)
            else:
                # When nber of classes is low -> number of individuals in the 
                # smallest class
                seuil = int(np.min(a_count))
        if np.max(a_count) <= seuil:
            print("Reequilibrage des echantillons (seuil : %i) => inutile"
                  % seuil)
        else:
            print("Reequilibrage des echantillons (seuil : %i)" % seuil)
            a_idx = np.ones(self.__data['Y'].shape, dtype=np.byte)
            # list of dominating classes (> seuil)
            lst_cl_dom = [k for k, v in self.__lbl.summary.items() if v > seuil]
            for l_os in lst_cl_dom:
                a_idx_os = np.where(self.__data['Y'] == l_os)
                print("Classe %i : %i => %i echantillons a eliminer"
                      % (l_os, len(a_idx_os[0]), len(a_idx_os[0]) - seuil))
                # select randomly samples to remove (code 0)
                a_idx_sel = sample(range(len(a_idx_os[0])),
                                   len(a_idx_os[0]) - seuil)
                a_idx[a_idx_os[0][a_idx_sel]] = 0
            # apply selection
            self.__data['Y'] = np.copy(self.__data['Y']
                                       [np.where(a_idx == 1)[0]])
            self.__data['X'] = np.copy(self.__data['X']
                                       [np.where(a_idx == 1)[0], :])
            # describe samples (once more) after balancing
            self.__lbl.Y = self.__data['Y']
        logger.info('Samples balanced')

    def plot(self, prefix='sig'):
        """
        Plots the dataset (signature):
        * one chart for the whole samples
        * one chart per samples' class

        Args:
            * prefix (str): prefix of output files to save charts in
        """
        logger.debug('Preparing charts of dataset')
        if self.data is not None:
            data = self.data
        elif self.X is not None:
            data = self.X
        else:
            logger.error('No available data')
            return

        # plots "signature" of dataset
        print("\n### Signature des donnees ###\n")
        sig = Signature(data, features=self.features,
                        output=self.__metadata['dirOut'])
        print(sig.plot(file='%s.png' % prefix))

        if self.X is not None and self.Y is not None:
            if self.__metadata['type'] == 'classification':
                for i in np.unique(self.Y):
                    # plot one class vs. data/every samples
                    str_file = "%s_cl%i.png" % (prefix, i)
                    print(sig.plot_class(self.X[self.Y == i, :], label=i,
                                   file=str_file))
            elif self.__metadata['type'] == 'regression':
                if self.data is not None:
                    # Plot samples vs. data
                    str_file = "%s_samples.png" % prefix
                    print(sig.plot_class(self.X, label="Echantillons", file=str_file))

        del sig
        logger.info('Charts created')

    def __str__(self):

        str_msg = ""
        if self.__data['data'] is None and self.__data['X'] is None:
            str_msg += '\t=> Aucune donnee disponible'
        else:
            str_msg += str(self.__lbl) + '\n'
            str_msg += "\n### Description du jeu de donnees ###\n"
            if self.__data['data'] is None:
                _data = pd.DataFrame(self.__data['X'])
            else:
                _data = pd.DataFrame(self.__data['data'])

            n_data = _data.shape[0]
            n_feat = _data.shape[1]
            stats = str(_data.describe())
            str_msg += "* %i donnees\n" % n_data
            str_msg += "* %i feature(s) : %s\n" % (n_feat, list(_data))
            str_msg += "* Resume statistique :\n\n"
            str_msg += '<pre>'+stats+'</pre>\n'
            str_msg += '\n\n<div style="clear:both;">\n</div>\n'
            if self.data is not None and self.Y is not None:
                str_msg += "\n### Echantillons vs. donnees ###\n"
                __plt = Plotter(output=self.__metadata['dirOut'],
                                style="vertical", css="small")
                str_msg += __plt.barplot(x=['data', 'samples'],
                                         palette=['lightgrey', 'darkgrey'],
                                         y=[self.data.shape[0], self.X.shape[0]],
                                         file='cnt_data_samples.png',
                                         title="Nombre d'individus")
                __plt = None
        
        return str_msg
