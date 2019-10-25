# -*- coding: utf-8 -*-
"""
**Labels**

This class handles labels associated to features in samples:

* counts how many samples for each class

"""
from __future__ import print_function
from __future__ import unicode_literals

from collections import Counter

import numpy as np

from maplearn.app.reporting import icon_msg, str_prop

from maplearn import logger


class Labels(object):
    """
    Samples labels used in PackData class

    Args:
        * Y (array): vector with samples' labels
        * codes (dict): dictionnary with labels code and associated description

    Attributes:
        * summary ()
        * dct_codes (dict): dictionnary with labels code and associated
          description

    Property:
        * Y (array): vector containing labels of samples (codes)
    """

    def __init__(self, Y, codes=None, output=None):
        self.__y = None
        self.summary = None
        self.dct_codes = codes
        self.Y = Y
        self.__output = output

    def count(self):
        """
        Summarizes labels of each class (how many samples for each class)
        """
        ukeys = np.unique(self.__y)
        bins = ukeys.searchsorted(self.__y)
        ukeys = [int(i) for i in list(ukeys)]
        l_nb = [int(i) for i in list(np.bincount(bins))]
        self.summary = dict(zip(ukeys, l_nb))

    def convert(self):
        """
        Conversion between codes
        """
        if self.dct_codes is None:
            logger.error('Unable to convert using new codes')
        else:
            self.__y = np.array([self.dct_codes[i] for i in self.__y])

    def libelle2code(self):
        """
        Converts labels' names into corresponding codes
        """
        if self.__y.dtype == 'S1':
            self.convert()
        else:
            logger.info("Y already contains numerical values")

    @property
    def Y(self):
        """
        Samples (as a vector)
        """
        return self.__y

    @Y.setter
    def Y(self, Y):
        """
        Sets samples after checking matching labels <-> names
        """
        if Y.ndim != 1:
            str_msg = "Y should be one dimension (got %i)" % Y.ndim
            logger.critical(str_msg)
            raise IndexError(str_msg)

        # gestion de la nomenclature en fonction des codes donnés en entrée
        # et des valeurs observées dans Y
        if self.dct_codes is not None:
            codes_y = list(np.unique(Y))
            tmp = [c for c in codes_y if c not in self.dct_codes.keys()]
            # creation de nouveaux codes si manquent dans nomenclature
            if len(tmp) > 0:
                logger.info('Following labels will be created:')
                for code in tmp:
                    self.dct_codes[code] = str(code)
                    logger.info('New label : %i (%s)', code,
                                self.dct_codes[code])

            if len(self.dct_codes) > len(codes_y):
                logger.warning('Label(s) without sample')
        else:
            self.dct_codes = dict(zip(np.unique(Y),
                                      [str(i) for i in np.unique(Y)]))

        # If several classes share the same code => to aggregate
        counts = Counter(self.dct_codes.values())
        duplic = [k for k in counts if counts[k] > 1]
        if len(duplic) > 0:
            logger.debug('%i label(s) to recode', len(duplic))
            for libelle in duplic:
                codes = [k for k in self.dct_codes
                         if self.dct_codes[k] == libelle]
                for code in codes[1:]:
                    Y[Y == code] = codes[0]
                    self.dct_codes.pop(code)

                print('\t* [%s] => %i (%s)' % (','.join([str(code) for code
                      in codes[1:]]), codes[0], self.dct_codes[codes[0]]))
            logger.info('%i code(s) recoded(s)', len(duplic))

        # Set Y and summarize number of samples per class
        self.__y = Y
        self.count()

    def __str__(self):
        __counts = np.unique(self.__y, return_counts=True)
        str_msg = "\n### Description des echantillons ###\n"
        if len(__counts[1]) < 1:
            str_msg += "**Aucun echantillon disponible**"
        else:
            str_msg += str_prop(__counts,
                                outdir=self.__output,
                                outfile='prop_labels.png')
            
            # Congalton empirical rule (at least 50 samples in each class)
            __cong = __counts[1][__counts[1]<50]
            if __cong.shape[0] > 0:
                str_msg += icon_msg("""(1) %i classe(s) avec moins de 50 echantillons
                                    (regle empirique de Congalton) : %s""" 
                                    % (__cong.shape[0],
                                       np.array2string(__cong, separator=';')),
                                       nature="warning")
        str_msg += '\n\n<div style="clear:both;">\n</div>\n'
        return str_msg
