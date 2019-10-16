#############################################################################
#                                                                           #
#    PyMassSpec software for processing of mass-spectrometry data           #
#    Copyright (C) 2019 Dominic Davis-Foster                                #
#                                                                           #
#    This program is free software; you can redistribute it and/or modify   #
#    it under the terms of the GNU General Public License version 2 as      #
#    published by the Free Software Foundation.                             #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public License      #
#    along with this program; if not, write to the Free Software            #
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.              #
#                                                                           #
#############################################################################

import pytest
from tests.constants import *

from pyms.Spectrum import Scan


def test_Scan(scan):
	
	assert isinstance(scan, Scan)
	
	assert isinstance(scan.mass_list, list)
	assert isinstance(scan.intensity_list, list)
	
	# Errors
	for type in [test_string, test_int, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			Scan(type, scan.intensity_list)
	
	for type in [test_string, test_int, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			Scan(scan.mass_list, type)
	
	with pytest.raises(ValueError):
		Scan(scan.mass_list, test_list_ints)


def test_len(scan):
	assert len(scan) == 101


def test_equality(im, scan):
	assert scan != im.get_scan_at_index(1234)
	assert scan == Scan(scan.mass_list, scan.intensity_list)
	assert scan != test_list_ints
	assert scan != test_list_strs
	assert scan != test_tuple
	assert scan != test_string
	assert scan != test_int
	assert scan != test_float


def test_intensity_list(scan):
	assert scan.intensity_list[5] == 1381.0
	assert scan.intensity_list[50] == 673.0
	assert scan.intensity_list[100] == 1728.0
	
def test_mass_list(scan):
	assert scan.mass_list[5] == 60.9465
	assert scan.mass_list[50] == 138.8299
	assert scan.mass_list[100] == 477.6667
	

