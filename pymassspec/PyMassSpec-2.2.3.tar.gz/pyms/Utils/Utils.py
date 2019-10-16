"""
General utility functions
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


def is_positive_int(arg):

    """
    Determines if the argument is an integer greater than zero

    :param arg: A string to be evaluate as a postive integer
    :type arg: types.StringType

    :return: A boolean indicator True or False
    :rtype:  bool

    :author: Milica Ng
    """

    if not isinstance(arg, int):
        return False
    elif not (arg > 0):
        return False
    else:
        return True


def is_list_of_dec_nums(arg):

    """
    Determines if the argument is a list of decimal numbers

    :param arg: A string to be evaluate as a list of decimal numbers
    :type arg: types.StringType

    :return: A boolean indicator True or False
    :rtype:  bool

    :author: Milica Ng
    """

    if not(isinstance(arg, list)):
        return False
    elif not arg:
        return False
    else:
        for q in arg:
            if not(isinstance(q, list)):
                return False
    return True

