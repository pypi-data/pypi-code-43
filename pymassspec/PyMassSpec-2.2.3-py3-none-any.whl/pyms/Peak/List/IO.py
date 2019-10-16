"""
Functions related to storing and loading a list of Peak objects
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


import pickle
import pathlib

from pyms.Peak.Class import Peak
from pyms.base import _list_types
from pyms.Peak.List.Function import is_peak_list
from pyms.Utils.IO import prepare_filepath


def store_peaks(peak_list, file_name):
    """
    Store the list of peak objects

    :param peak_list: A list of peak objects
    :type peak_list: list of class:`pyms.Peaks.Class.Peak`
    :param file_name: File name to store peak list
    :type file_name: str or pathlib.Path

    :author: Andrew Isaac
    :author: Dominic Davis-Foster (type assertions and pathlib support)
    """
    
    if not is_peak_list(peak_list):
        raise TypeError("'peak_list' must be a list of Peak objects")

    if not isinstance(file_name, (str, pathlib.Path)):
        raise TypeError("'file_name' must be a string or a pathlib.Path object")

    file_name = prepare_filepath(file_name)

    fp = file_name.open('wb')
    pickle.dump(peak_list, fp, 1)
    fp.close()


def load_peaks(file_name):
    """
    Loads the peak_list stored with 'store_peaks'

    :param file_name: File name of peak list
    :type file_name: str or pathlib.Path

    :return: The list of Peak objects
    :rtype: list of class:`pyms.Peak.Class.Peak`

    :author: Andrew Isaac
    :author: Dominic Davis-Foster (pathlib support)
    """

    if not isinstance(file_name, (str, pathlib.Path)):
        raise TypeError("'file_name' must be a string or a pathlib.Path object")

    if not isinstance(file_name, pathlib.Path):
        file_name = pathlib.Path(file_name)

    fp = file_name.open('rb')
    peak_list = pickle.load(fp)
    fp.close()

    if not isinstance(peak_list, _list_types):
        raise IOError("The selected file is not a List")
    if not len(peak_list) > 0 or not isinstance(peak_list[0], Peak):
        raise IOError("The selected file is not a list of Peak objects")

    return peak_list
