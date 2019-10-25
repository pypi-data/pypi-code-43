# -*- coding: utf-8 -*-
"""
**Confusion matrix**

A confusion matrix, also known as an error matrix, is a specific table layout
that allows visualization of the performance of an algorithm, typically a
supervised learning one (see 'classification' class).

Each column of the matrix represents the instances in a predicted class while
each row represents the instances in an actual class. The name stems from the
fact that it makes it easy to see if the system is confusing two classes.

Example:
    >>> import numpy as np
    >>> # creates 2 vectors representing labels
    >>> y_true = np.random.randint(0, 15, 100)
    >>> y_pred = np.random.randint(0, 15, 100)
    >>> cm = Confusion(y_true, y_pred)
    >>> cm.calcul_matrice()
    >>> cm.calcul_kappa()
    >>> print(cm)
"""
from __future__ import division, print_function

import os

import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, cohen_kappa_score
from maplearn.datahandler.plotter import Plotter

from maplearn import logger


class Confusion(object):
    """
    Computes confusion matrix based on 2 vectors of labels:

    1. labels of known samples
    2. predicted labels

    Args:
        * y_sample (vector): vector with known labels
        * y_predit (vector): vector with predicted labels
        * fTxt (str): path to the text file to write confusion matrix into
        * fPlot (str): id. with chart

    Attributes:
        * y_sample (vector): true labels (ground data)
        * y_predit (vector): corresponding predicted labels
        * cm (matrix): confusion matrix filled with integer values
        * kappa (float): kappa index
        * score (float): precision score

    TODO:
        * y_sample and y_predit should be renamed y_true and y_pred
    """
    def __init__(self, y_sample, y_predit, fTxt=None, fPlot=None):
        self.y_sample = y_sample
        self.y_predit = y_predit
        self.__files = {'txt': fTxt, 'plot': fPlot}
        self.__labels = np.union1d(y_sample, y_predit)
        # Resultats
        self.cm = None
        self.__kappa = None
        self.score = None

    def calcul_matrice(self):
        """
        Computes a confusion matrix and display the result

        Returns:
            * matrix (integer): confusion matrix
            * float: kappa index
        """
        self.__kappa = None
        # Compute confusion matrix
        self.cm = confusion_matrix(self.y_sample, self.y_predit,
                                   labels=self.__labels)
        try:
            if self.__labels.shape[0] == 2:
                self.score = precision_score(self.y_sample, self.y_predit,
                                             labels=self.__labels,
                                             pos_label=self.__labels[0],
                                             average='weighted')
            else:
                self.score = precision_score(self.y_sample, self.y_predit,
                                             labels=self.__labels,
                                             average='weighted')
        except:
            self.score = precision_score(self.y_sample, self.y_predit,
                                         average='weighted')
        return(self.cm, self.kappa)  # renvoie la matrice de confusion

    @property
    def kappa(self):
        """
        Computes kappa index based on 2 vectors

        Returns:
            * float: kappa index
        """
        if self.__kappa is None:
            self.__kappa = cohen_kappa_score(self.y_sample, self.y_predit)

        return self.__kappa

    def export(self, fTxt=None, fPlot=None, title=None):
        """
        Saves confusion matrix in:

        * a text file
        * a graphic file

        Args:
            * fTxt (str): path to the output text file
            * fPlot (str): path to the output graphic file
            * title (str): title of the chart
        """
        __msg = ""
        if fTxt is not None:
            self.__files['txt'] = fTxt
        if fPlot is not None:
            self.__files['plot'] = fPlot

        # save confusion matrix in a plot
        if self.__files['plot'] is not None:
            __plt = Plotter(os.path.dirname(self.__files['plot']),
                            style='confusion')
            if title is None:
                title = 'Confusion Matrix on %i samples' \
                        % self.y_sample.shape[0]
            data = self.cm.astype('float')
            data[data==0] = np.nan
            labels = [str(int(i)) for i in list(self.__labels)]
            text = 'Accuracy: %.3f | Kappa: %.3f' % (self.score, self.kappa)
            __msg += __plt.confusion(data=data,
                            file=os.path.basename(self.__files['plot']),
                            title=title, text=text,
                            labels = labels)
            __plt = None
        else:
            logger.warning('Unable to save graphic: no output file defined')

        # save confusion matrix as a text file
        if self.__files['txt'] is not None:
            # sauvegarde matrice de confusion (obligatoirement en premier)
            np.savetxt(self.__files['txt'], self.cm.astype(int), comments='',
                       header=np.array2string(self.__labels), fmt='%i')
        else:
            logger.warning('Unable to save: no output text file defined')
        return __msg

    def __str__(self):
        str_msg=""
        if self.__files['plot'] is not None:
            str_msg += '![cm](%s){: .cm}\n' % os.path.basename(self.__files['plot'])
        return str_msg


def confusion_cl(cm, labels, os1, os2):
    """
    Computes confusion between 2 given classes (expressed in percentage) based
    on a confusion matrix

    Args:
        * cm (matrix): confusion matrix
        * labels (array): vector of labels
        * os1 and os2 (int): codes of th classes

    Returns:
        * float: confusion percentage between 2 classes
    """
    # indices correspondantes aux 2 classes
    if os1 in labels and os2 in labels:
        id1 = long(np.where(labels == os1)[0])
        id2 = long(np.where(labels == os2)[0])
    else:
        return None
    # matrice de confusion sur les 2 classes
    cm_cl = np.matrix([[cm[id1, id1], cm[id1, id2]],
                       [cm[id2, id1], cm[id2, id2]]])

    # conf_cl=(cm_cl[0,1]+cm_cl[1,0])/np.sum(cm_cl)*100
    return (cm_cl[0, 1] + cm_cl[1, 0]) / np.sum(cm_cl) * 100
