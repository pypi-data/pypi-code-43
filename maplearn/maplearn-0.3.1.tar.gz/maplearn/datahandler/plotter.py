# -*- coding: utf-8 -*-
"""
**Plotter: a generic class to create plots**

"""
from __future__ import unicode_literals
import os

import numpy as np
import pandas as pd
import matplotlib
## agg backend is used to create plot as a .png file
matplotlib.use('agg')

from matplotlib import pyplot as plt
from statsmodels import api as sm
import seaborn as sns
from maplearn import logger

# Turn interactive plotting off
plt.ioff()

COLOR = "darkgrey"

# Thresholds about plotting
# <= 1st value : high quality chart
# > 2nd value : no chart
# between : "poor" quality chart
IND_THRES = (10000, 1000000000)
FEAT_THRES = (15, 200)


def color_box(boxplot, zorder, alpha):
    """
    Colours boxes in the boxplot

    Args:
        * boxplot: plot onto put some colours
        * zorder?
        * alpha: transparency setting
    
    """

#        for box in boxplot['boxes']:
#            # change outline color & fill color
#            box.set(color='darkgrey', linewidth=2, facecolor='lightgrey',
#                    zorder=zorder + 1, alpha=alpha)

    # change color and linewidth of the whiskers
    for whisker in boxplot['whiskers']:
        whisker.set(color='darkgrey', linewidth=2, linestyle='-',
                    zorder=zorder + 2, alpha=alpha)

    # change color and linewidth of the caps
    for cap in boxplot['caps']:
        cap.set(color='darkgrey', linewidth=2, linestyle='-',
                zorder=zorder + 3, alpha=alpha)

    # change color and linewidth of the medians
    for median in boxplot['medians']:
        median.set(color='darkgrey', linewidth=3, linestyle='-',
                   zorder=zorder + 4, alpha=alpha)

    # fliers <=> outliers
    plt.setp(boxplot['fliers'], color='white', marker='o', markersize=5.0,
             zorder=zorder + 5, alpha=alpha)

def update_params(default_params, user_params):
    """
    Set a unique set of parameters combining default parameters and parameters
    asked by the user

    Args:
        * default_params (dict): default parameters
        * user_params (dict): parameters set by the user.
    
    *NB: if a parameter exists in both dictionnaries, the parameter from
    user_params will remain.*

    Returns:
        user_params (dict): parameters
    """
    __params = default_params
    __params.update(user_params)
    return __params

class Plotter(object):
    """
    Creates different kinds of charts. Each kind of chart corresponds to a
    public method

    Args:
        * output (str): path that will contain a subdir 'fig' with all plot
          files 
    """
    def __init__(self, output, style='', css='sig'):
        sns.set(style="white")
        if style == 'confusion':
            sns.set(rc={"figure.figsize": (8, 8)})
        elif style == 'square':
            sns.set(rc={"figure.figsize": (6, 6)})
        elif style == 'vertical':
            sns.set(rc={"figure.figsize": (4, 6)})
        else:
            sns.set(rc={"figure.figsize": (8, 4)})
        if not os.path.exists(output):
            raise IOError('Output folder is missig (%s)', output)
        __subdir = os.path.join(output, 'fig')
        if not os.path.exists(__subdir):
            os.mkdir(__subdir)
            logger.info('Output fig subfolder (%s) has been created', __subdir)
        self.__output = output
        self.__plot = None
        self.__css = css
        logger.debug('Plotter class initialized')

    def dist(self, data, file='distribution.png', **kwargs):
        """
        Distribution histogram

        Args:
            * data (dataframe) : data to plot
            * file (str): path to the output file
        """
        __params = {'color':COLOR}
        __params = update_params(__params, kwargs)
        self.__plot = sns.distplot(data, **__params)
        return self.save(file)

    def barplot(self, data=None, y=None, x=None, file='barplot.png',
                title='', **kwargs):
        """
        Barplot

        Args:
            * data (dataframe) : data to plot
            * x (str) : name of the column used for absciss
            * y (str) : name of the column used for ordinate
            * file (str): path to the output file
        """
        __params = {'color':COLOR}
        __params = update_params(__params, kwargs)
        # Draw a count plot
        self.__plot = sns.barplot(y=y, x=x, data=data, **__params)
        return self.save(file, title=title)

    def __check(self, data):
        """
        Check if data can be plotted
        """
        if data.size > max(IND_THRES):
            logger.error('Too many data to plot. Giving up...')
            return False
        elif data.size > min(IND_THRES) * max(FEAT_THRES):
            logger.warning('Numerous data to plot. You should consider using \
                           "plot_sum" method')
        return True


    def boxplot(self, data, file='boxplot.png', title='', **kwargs):
        """
        Plots data as boxplot

        Args:
            * data (dataframe) : data to plot
            * file (str): path to the output file
            * title (str): title to add to the plot
        """
        __params = {'color':COLOR, 'notch':True, 'orient':'v'}
        __params = update_params(__params, kwargs)
        
        if self.__check(data):
            self.__plot = sns.boxplot(data=data, **__params)
            return self.save(file, title=title)

    def plot_sum(self, data, file='plot_summarized.png', title='',
                 features=None, **kwargs):
        """
        Plots data as vertical lines after summarized it
        """        
        # summarize data
        if hasattr(data, 'values'):
            data = data.values
        if data.shape[1] > max(FEAT_THRES):
            summary = np.mean(data, axis=0)
        else:
            summary = pd.DataFrame({'min': np.min(data, axis=0),
                                    'max': np.max(data, axis=0),})
            if data.shape[0] < max(IND_THRES):
                __q = (25, 50, 75)
                __df = pd.DataFrame(np.transpose(np.percentile(data,
                                                               q=__q, axis=0)),
                                    columns=['q%i' % i for i in __q])
                summary = summary.assign(**__df)
    
        fig = plt.figure(figsize=(8, 4))
        ax0 = fig.add_subplot(1, 1, 1)
        
        if features is not None:
            xlab = features
        else:
            xlab = range(1, data.shape[1] + 1)
        
        ax0.set_ylim(bottom=np.min(np.min(summary)),
                     top=np.max(np.max(summary)))
        
        if data.shape[1] > max(FEAT_THRES):
            ax0.plot(xlab, summary, ls='None', marker='D', color='k')
        else:
            __x = np.arange(summary.shape[0]) + 1
            ax0.vlines(x=__x, linewidth=1, color='0.5', 
                       ymin=summary['min'].values,
                       ymax=summary['max'].values)
            if 'q25' in summary.columns:
                ax0.vlines(x=__x, linewidth=5, color='0.7',
                           ymin=summary['q25'].values,
                           ymax=summary['q75'].values)
            if 'q50' in summary.columns and data.shape[0] < max(IND_THRES):
                line, = ax0.plot(xlab, summary['q50'], ls='None', marker='D',
                                 color='k')
        ax0.set_title(title)
        self.__plot = ax0
        
        return self.save(file, title=title)

    def factorplot(self, data, file='factorplot.png', title='', **kwargs):
        """
        Plots data as a factorplot

        Args:
            * data (dataframe) : data to plot
            * file (str): path to the output file
            * title (str): title to add to the plot
        """
        __params = {'color':COLOR, 'size':5, 'aspect':2, 'capsize':.1,
                    'linestyles':'--', 'kind':'point'}
        __params = update_params(__params, kwargs)

        if self.__check(data):
            self.__plot = sns.factorplot(data=data, **__params)
            return self.save(file, title=title)

    def regression(self, data, file='regression.png', title=''):
        """
        Plots result of a prediction using regression

        Args:
            * data (dataframe) : data to plot
            * file (str): path to the output file
            * title (str): chart's title
        """
        self.__plot = sns.lmplot('Mesures', 'Prediction', data=data)
        return self.save(file, title=title)

    def qqplot(self, data, file='qqplot.png', title='', **kwargs):
        """
        Plots residuals of a regression model

        Args:
            * data (matrix) : vector of residuals to plot
            * file (str): path to the output file
            * title (str): chart's title
        """
        __params = {'marker':'o', 'markerfacecolor':'b', 'markeredgecolor':'b',
                    'alpha':.6, 'zorder':10}
        __params = update_params(__params, kwargs)
        __pp = sm.ProbPlot(data, fit=True)
        self.__plot = __pp.qqplot(data, **__params)
        sm.qqline(self.__plot.axes[0], line='45', fmt='r-')
        plt.xlabel('Theoretical Quantiles')
        return self.save(file=file, title=title)
    
    def donut(self, data, labels, file='donut.png', title='', **kwargs):
        """
        Plots data as a donut plot (pie charts are not much appreciated in data
        vizualization...)

        Args:
            * data (dataframe) : data to plot
            * file (str): path to the output file
            * title (str): title to add to the plot
        """
        # Create a circle for the center of the plot
        __circle = plt.Circle( (0,0), 0.6, color='white')
        self.__plot = plt.pie(data, labels=labels,
                              colors=['darkgrey','lightgrey'],
                wedgeprops = { 'linewidth' : 5, 'edgecolor' : 'white' })
        p = plt.gcf()
        p.gca().add_artist(__circle)
        return self.save(file=file, title=title)

    def confusion(self, data=None, file='confusion.png', title='',
                  labels=None, text=''):
        """
        Plots a confusion matrix

        Args:
            * data (dataframe) : data to plot
            * file (str): path to the output file
            * title (str): chart's title
        """
        colmap = plt.cm.copper_r
        colmap.set_under('white')
        self.__plot = sns.heatmap(data, cmap=colmap, vmin=.5, square=True,
                                  annot=True, fmt=".0f")
        if text != '':
            self.__plot.figure.text(.5, .1, text, fontsize=10, ha='center')
        plt.ylabel('Truth')
        plt.xlabel('Prediction')
        # labels des axes
        if not labels is None:
            __pos = np.arange(len(labels))+.5
            plt.xticks(__pos, labels, size=8)
            plt.yticks(__pos[::-1], labels, size=8)

        return self.save(file=file, title=title)

    def save(self, file, title=''):
        """
        Save the plot into a file

        Args:
            * file (str): path to the output file
            * title (str): chart's title
            * css (str): css class to use
        """
        __msg = ""
        if file is None:
            logger.warning('Output path not defined.')
            return __msg
        if title != '':
            plt.title(str(title))
        logger.debug('Trying to save the plot')
        try:
            plt.savefig(os.path.join(self.__output, 'fig', file), format='png',
                        bbox_inches='tight')
        except IOError:
            logger.error("Missing folder : %s", self.__output)
        else:
            logger.info('Chart saved in %s', file)
            __msg = '\n\n![%s](fig/%s){: .%s}\n\n' % (title, file, self.__css)
        finally:
            plt.close()
        return __msg

    @property
    def fig(self):
        """
        Returns the figure used to display the chart
        """
        return self.__plot

    def edit_style(self, **kwargs):
        """
        Edits style of a figure
        """
        plt.setp(self.__plot.artists, **kwargs)

    def __del__(self):
        plt.close('all')
        self.__plot = None
        logger.debug('Plotter class destroyed')
