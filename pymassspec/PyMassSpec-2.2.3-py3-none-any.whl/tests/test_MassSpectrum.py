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


import copy

import pytest

from tests.constants import *

from pyms.Spectrum import MassSpectrum


def test_MassSpectrum(ms):
	assert isinstance(ms, MassSpectrum)
	
	assert isinstance(ms.mass_list, list)
	assert isinstance(ms.mass_spec, list)
	
	# Errors
	for type in [test_string, test_int, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			MassSpectrum(type, ms.mass_spec)
	
	for type in [test_string, test_int, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			MassSpectrum(ms.mass_list, type)
	
	with pytest.raises(ValueError):
		MassSpectrum(ms.mass_list, test_list_ints)


def test_len(ms):
	assert len(ms) == 450


def test_equality(im, ms):
	assert ms != im.get_ms_at_index(1234)
	assert ms == MassSpectrum(ms.mass_list, ms.mass_spec)
	assert ms != test_list_ints
	assert ms != test_list_strs
	assert ms != test_tuple
	assert ms != test_string
	assert ms != test_int
	assert ms != test_float


def test_mass_spec(ms):
	ms = copy.deepcopy(ms)
	assert ms.mass_spec[5] == 4192.0
	assert ms.mass_spec[50] == 3459.0
	assert ms.mass_spec[100] == 0.0
	
	ms.mass_spec[0] = 123
	assert ms.mass_spec[0] == 123
	
	assert ms.mass_spec == ms.intensity_list
	
	ms.mass_spec = list(range(len(ms.mass_spec)))
	assert ms.mass_spec == list(range(len(ms.mass_spec)))
	
	# Errors
	for type in [test_float, test_string, test_int, test_dict, test_list_strs]:
		with pytest.raises(TypeError):
			ms.mass_spec = type
		with pytest.raises(TypeError):
			ms.intensity_list = type
	
	#for type in [test_list_ints, test_tuple]:
	#	with pytest.raises(ValueError):
	#		ms.mass_spec = type
	#	with pytest.raises(ValueError):
	#		ms.intensity_list = type


def test_mass_list(ms):
	assert ms.mass_list[5] == 55
	assert ms.mass_list[50] == 100
	assert ms.mass_list[100] == 150
	
	ms.mass_list = list(range(len(ms.mass_list)))
	assert ms.mass_list == list(range(len(ms.mass_list)))
	
	# Errors
	for type in [test_float, test_string, test_int, test_dict, test_list_strs]:
		with pytest.raises(TypeError):
			ms.mass_list = type
	
	#for type in [test_list_ints, test_tuple]:
	#	with pytest.raises(ValueError):
	#		ms.mass_list = type


