# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015-2019  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Utilities

Helper functions and utilities for evaluation of data

and other stuff.

"""
from __future__ import division

import re
import numpy as np
import scipy.linalg as la

from . import formel
from .dataarray import dataArray as dA

try:
    import pymatgen
    cifreaderfound=True
except ImportError:
    cifreaderfound=False
    pass

# variable to allow printout for debugging as if debug:print 'message'
debug=False

# Control Sequence Introducer  =  "\x1B[" for print coloured text
# 30–37  Set text color  30 + x = Black    Red     Green   Yellow[11]  Blue    Magenta     Cyan    White
# 40–47  Set background color    40 + x,
CSIr="\x1B[31m"      # red
CSIrb="\x1B[31;40m"  # red black background
CSIy="\x1B[33m"      # yellow
CSIyb="\x1B[33;40m"  # yellow black background
CSIg="\x1B[32m"      # green
CSIgb="\x1B[32;40m"  # green black background
CSIe="\x1B[0m"  # sets to default

