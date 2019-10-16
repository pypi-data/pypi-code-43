"""
Provides mathematical functions
"""

################################################################################
#                                                                              #
#    PyMassSpec software for processing of mass-spectrometry data              #
#    Copyright (C) 2005-2012 Vladimir Likic                                    #
#    Copyright (C) 2019 Dominic Davis-Foster                                   #
#                                                                              #
#    This program is free software; you can redistribute it and/or modify      #
#    it under the terms of the GNU General Public License version 2 as         #
#    published by the Free Software Foundation.                                #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU General Public License for more details.                              #
#                                                                              #
#    You should have received a copy of the GNU General Public License         #
#    along with this program; if not, write to the Free Software               #
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.                 #
#                                                                              #
################################################################################


import math
from statistics import median
from statistics import stdev as std

import numpy

from pyms.base import _list_types


def vector_by_step(vstart, vstop, vstep):
    """
    generates a list by using start, stop, and step values

    :param vstart: Initial value
    :type vstart: A number
    :param vstop: Max value
    :type vstop: A number
    :param vstep: Step
    :type vstep: A number
   
    :return: A list generated
    :rtype: list

    :author: Vladimir Likic
    """

    if not isinstance(vstart, (int, float)) or not isinstance(vstop, (int, float)) or not isinstance(vstep, (int, float)):
        raise TypeError("parameters 'start', 'stop', and 'step' must be numbers")

    v = []

    p = vstart 
    while p < vstop:
        v.append(p)
        p = p + vstep

    return v


def MAD(v):
    """
    median absolute deviation

    :param v: A list or array
    :type v: list, tuple, or numpy.core.ndarray

    :return: median absolute deviation
    :rtype: float

    :author: Vladimir Likic
    """

    if not isinstance(v, _list_types):
        raise TypeError("'v' must be a list or array")

    m = median(v)
    m_list = []

    for xi in v:
        d = math.fabs(xi - m)
        m_list.append(d)

    mad = median(m_list)/0.6745

    return mad


def rmsd(list1, list2):

    """
    Calculates RMSD for the 2 lists

    :param list1: First data set
    :type list1: list, tuple, or numpy.core.ndarray
    :param list2: Second data set
    :type list2: list, tuple, or numpy.core.ndarray
    :return: RMSD value
    :rtype: float

    :author: Qiao Wang
    :author: Andrew Isaac
    :author: Vladimir Likic
    """

    if not isinstance(list1, _list_types):
        raise TypeError("'list1' must be a list or array")

    if not isinstance(list2, _list_types):
        raise TypeError("'list2' must be a list or array")

    sum = 0.0
    for i in range(len(list1)):
        sum = sum + (list1[i] - list2[i]) ** 2
    rmsd = math.sqrt(sum / len(list1))
    return rmsd


# added by DK. courtesy of
# http://stackoverflow.com/questions/22354094/pythonic-way-of-detecting-outliers-in-one-dimensional-observation-data
def mad_based_outlier(data, thresh=3.5):
    """
    
    :param data:
    :param thresh:
    :return:
    """
    
    data = numpy.array(data)
    if len(data.shape) == 1:
        data = data[:, None]
    median = numpy.nanmedian(data)
    diff = numpy.nansum((data - median) ** 2, dtype=float, axis=-1)
    diff = numpy.sqrt(diff)
    med_abs_deviation = numpy.nanmedian(diff)
    
    modified_z_score = 0.6745 * diff / med_abs_deviation
    
    return modified_z_score > thresh


# added by DK. courtesy of
# http://stackoverflow.com/questions/22354094/pythonic-way-of-detecting-outliers-in-one-dimensional-observation-data
def percentile_based_outlier(data, threshold=95):
    """
    
    :param data:
    :param threshold:
    :return:
    """
    
    data = numpy.array(data)
    diff = (100 - threshold) / 2.0
    # nanpercentile only works in numpy 1.9 and up
    # minval, maxval = numpy.nanpercentile(data, [diff, 100 - diff])
    data = numpy.array(data)
    minval, maxval = numpy.percentile(numpy.compress(numpy.isnan(data) == False, data), (diff, 100 - diff))
    return (data < minval) | (data > maxval)


# added by DK. courtesy of
# http://stackoverflow.com/questions/11686720/is-there-a-numpy-builtin-to-reject-outliers-from-a-list
def median_outliers(data, m=2.5):
    """
    
    :param data:
    :param m:
    :return:
    """
    
    data = numpy.array(data)
    d = numpy.abs(data - numpy.nanmedian(data))
    mdev = numpy.nanmedian(d)
    s = d / mdev if mdev else 0.
    return (s > m)