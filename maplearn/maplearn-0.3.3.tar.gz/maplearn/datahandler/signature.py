# -*- coding: utf-8 -*-
"""
**Signature**

This class makes charts about a dataset:

* spectral signature
* temporal signature

Example:
    >>> from maplearn.datahandler.loader import Loader
    >>> from maplearn.datahandler.signature import Signature
    >>> ldr = Loader('iris')
    >>> sig = Signature()
    >>> sig.plot(ldr.X, title='test')
"""
from __future__ import unicode_literals

import pandas as pd

from maplearn.datahandler.plotter import Plotter
from maplearn.datahandler.plotter import IND_THRES, FEAT_THRES

from maplearn import logger

COLOR = "darkgrey"#"#BDE96B"#"#424242"#"#BDE96B"#"#E9D66B"#"#F7D358"


class Signature(object):
    """
    Makes charts about a dataset:

    * one global graph
    * one graph per class in samples (if samples are available)

    Args:
        * data (array or DataFrame): data to plot
        * features (list): name of columns
        * model (str): how to plot signature (plot or boxplot)
        * ouput (str): path to the output directory where will be saved plots
    """

    def __init__(self, data, features=None, model='boxplot', output=None):

        self.__features = features
        if data.shape[0] > IND_THRES[0]:
            logger.warning('Too many individuals. Plots will use summarized data')
            self.__data = data
        else:
            self.__data = self.__to_df(data)
            self.__data_stack = self.__stack(self.__data)
            if features is None:
                self.__features = self.__data.columns

        self.__plotter = Plotter(output=output, style="white",
                                 css='sigclass_wide')
        self.__model = model
        # Change the type of chart according to the number of features
        if self.__data.shape[1] > FEAT_THRES[0] and self.__model == 'boxplot':
            logger.warning('Too many features for boxplot, simple plot will \
                           be used instead)')
            self.__model = 'plot'

    def __to_df(self, data):
        """
        Puts into a dataframe with name of columns
        """
        if self.__features is None and hasattr(data, 'columns'):
            self.__features = data.columns
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data, columns=self.__features)
        return data

    def __stack(self, data, source='data'):
        """
        Change data structure in 2 columns

        Arg:
            * data (dataframe): data wich structure is to be changed
            * origin (str): where comes the data from? will be indicated in a
                column called source

        Returns:
            * __stack (dataframe): data with 3 columns (feature, value, origin)
        """
        logger.debug('Stacking dataset prior to making chart...')
        
        data = self.__to_df(data)

        __stack = pd.DataFrame(data.stack())
        __stack.reset_index(1, inplace=True)
        __stack.columns = ['feature', 'value']
        __stack['source'] = source
        logger.debug('Dataset Stack: OK')
        return __stack

    def plot(self, title='Signature du jeu de donnees', file=None):
        """
        Plots (spectral) signature of data as boxplots or points depending of
        the number of features

        Args:
            * title (str): title to add to the plot
            * file (str): name of the output file
        """
        if self.__data.size > max(IND_THRES):
            logger.error('Too many individuals to plot. Give-up')
            return False
        __msg = ""
        logger.debug('Preparing to chart...')
        if self.__data.shape[0] > min(IND_THRES):
            __msg += self.__plotter.plot_sum(data=self.__data, file=file, 
                                             title=title)
        else:
            if self.__model == 'boxplot':
                __msg += self.__plotter.boxplot(data=self.__data, file=file,
                                                title=title)
            else:
                __msg += self.__plotter.factorplot(data=self.__data, file=file,
                                                   title=title)
        return __msg

    def plot_class(self, data_class, label='', file=None):
        """
        Plots the signature of one class above the whole dataset

        Args:
            * data_class (dataframe): data of one class
            * label (str): label of the class to plot
            * file (str): path to the file to save the chart in
        """
        __msg = ""
        title = "Signature spectrale : classe %s" % str(label)
        __n_data = (self.__data.shape[0] + data_class.shape[0]) * \
                    self.__data.shape[1]

        if __n_data > max(IND_THRES):
            logger.error('Too many individuals to plot. Give-up')
            return False
        elif __n_data <= min(IND_THRES):
            data_class = self.__to_df(data_class)
            if self.__model == 'boxplot':
                __msg = self.__bp_class(data_class, title=title, file=file)
            else:
                __msg = self.__fp_class(data_class, title=title, file=file)
        else:
            __msg = self.__plotter.plot_sum(data=data_class, file=file,
                                            title=title)
        return __msg

    def __fp_class(self, data, title='', file=None):
        """
        Creates a plot for the whole dataset and adds plot corresponding
        to one class to show signatures

        Args:
            * data_class: data of one class
            * title (str): title of the boxplot
            * file (str): path to the file to save the chart in
        """
        __data_class = self.__stack(data, source='samples')
        data = pd.concat([self.__data_stack, __data_class])
        data['source'] = data['source'].astype('category')

        return self.__plotter.factorplot(data=data, file=file, title=title,
                                         hue='source', x='feature', y='value',
                                         legend_out=True,
                                         palette={'data':'lightgrey',
                                                  'samples':'darkgrey'})

    def __bp_class(self, data, title='', file=None):
        """
        Creates a boxplot for the whole dataset and adds boxplot corresponding
        to one class to show signatures

        Args:
            * data_class: data of one class
            * title (str): title of the boxplot
            * file (str): path to the file to save the chart in
        """
        logger.debug('Initializing chart...')
        self.__plotter.boxplot(data=self.__data, file=None)
        self.__plotter.edit_style(alpha=.3)

        # a 2nd chart overlays the first
        ax2 = self.__plotter.fig.twinx()
        ax2.set(ylim=self.__plotter.fig.get_ylim())

        # sets transparency
        for patch in ax2.artists:
            __col = patch.get_facecolor()
            __col[-1] = .3
            patch.set_facecolor(__col)
            patch.set_edgecolor(__col)
        
        # overlay 2nd boxplot about the current class
        self.__plotter.boxplot(data=data, file=None, ax=ax2,
                               saturation=0.3)

        if file is not None:
            return self.__plotter.save(file=file, title=title)

    def __del__(self):
        self.__plotter = None
