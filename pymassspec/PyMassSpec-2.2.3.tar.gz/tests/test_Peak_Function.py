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

from pyms.Peak.Function import *


def test_peak_sum_area(peak, im_i):
	
	area_sum, area_dict = peak_sum_area(im_i, peak, single_ion=True, max_bound=5)
	assert isinstance(area_sum, float)
	assert isinstance(area_dict, dict)
	assert area_sum == 10025814.0
	assert area_dict[51] == 3299.0
	assert isinstance(area_dict[51], float)
	
	area_sum = peak_sum_area(im_i, peak, single_ion=False, max_bound=5)
	assert area_sum == 10025814.0
	
	# Errors
	for type in [test_int, test_float, test_string, test_dict, test_list_strs, test_list_ints, test_tuple]:
		with pytest.raises(TypeError):
			peak_sum_area(type, peak)
	for type in [test_int, test_float, test_string, test_dict, test_list_strs, test_list_ints, test_tuple]:
		with pytest.raises(TypeError):
			peak_sum_area(im_i, type)
	for type in [test_float, test_string, test_dict, test_list_strs, test_list_ints, test_tuple]:
		with pytest.raises(TypeError):
			peak_sum_area(im_i, peak, max_bound=type)
	

def test_peak_pt_bounds(peak, im_i):
	bounds = peak_pt_bounds(im_i, peak)
	assert isinstance(bounds, tuple)
	assert len(bounds) == 2
	assert bounds == (3,3)
	assert isinstance(bounds[0], int)
	
	for type in [test_string, test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			peak_pt_bounds(type, peak)
	for type in [test_string, test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			peak_pt_bounds(im_i, type)


def test_peak_top_ion_areas(peak, im_i):
	areas = peak_top_ion_areas(im_i, peak, 5)
	assert isinstance(areas, dict)
	
	assert len(areas) == 5
	
	assert areas[100] == 4534.0
	assert isinstance(areas[100], float)
	
	for type in [test_string, test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			peak_top_ion_areas(type, peak)
	for type in [test_string, test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			peak_top_ion_areas(im_i, type)
	for type in [test_string,  test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			peak_top_ion_areas(im_i, peak, n_top_ions=type)
	for type in [test_string, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			peak_top_ion_areas(im_i, peak, max_bound=type)


def test_top_ions_v1(peak):
	with pytest.warns(DeprecationWarning):
		top_ions_v1(peak, 10)


def test_top_ions_v2(peak):
	with pytest.warns(DeprecationWarning):
		top_ions_v2(peak, 10)

def test_ion_area():
	ion_area_val = ion_area(list(range(100)), 20)
	assert isinstance(ion_area_val, tuple)
	assert len(ion_area_val) == 5
	assert ion_area_val[0] == 231
	assert ion_area_val[1] == 19
	assert ion_area_val[2] == 1
	assert ion_area_val[3] is False
	assert ion_area_val[4] is True
	
	for type in [test_string, test_float, test_int, test_dict, test_list_strs]:
		with pytest.raises(TypeError):
			ion_area(type, 20)
	for type in [test_string, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			ion_area(list(range(100)), type)
	for type in [test_string, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			ion_area(list(range(100)), 20, max_bound=type)
	for type in [test_string, test_int, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			ion_area(list(range(100)), 20, tol=type)


def test_half_area():
	half_area_value = half_area(list(range(100)), 20)
	assert isinstance(half_area_value, tuple)
	assert len(half_area_value) == 3
	assert half_area_value[0] == 1
	assert half_area_value[1] == 1
	assert half_area_value[2] is True
	
	for type in [test_string, test_float, test_int, test_dict, test_list_strs]:
		with pytest.raises(TypeError):
			half_area(type)
	for type in [test_string, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			half_area(list(range(100)), max_bound=type)
	for type in [test_string, test_int, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			half_area(list(range(100)), tol=type)


def test_median_bounds(im_i, peak):
	median_bounds_value = median_bounds(im_i, peak)
	assert isinstance(median_bounds_value, tuple)
	assert isinstance(median_bounds(im_i, peak, False), tuple)
	assert len(median_bounds_value) == 2
	assert median_bounds_value == (1 ,1)
	assert median_bounds_value[0] == 1
	assert median_bounds_value[1] == 1
	
	for type in [test_string, test_float, test_int, test_dict, test_list_strs, test_list_ints]:
		with pytest.raises(TypeError):
			median_bounds(type, peak)
	for type in [test_string, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			median_bounds(im_i, type)
	for type in [test_string, test_int, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			median_bounds(im_i, peak, type)



"""def test_abundant_ions(filtered_peak_list, im_i):
	
	print("Number of filtered peaks: ", len(filtered_peak_list))
	
	# find and set areas
	print("Top 5 most abundant ions for each peak ")
	
	for peak in filtered_peak_list:
		rt = peak.rt
		# Only test interesting sub-set from 29.5 to 32.5 minutes
		if rt >= 29.5 * 60.0 and rt <= 32.5 * 60.0:
			# determine and set ion areas, use default num of ions =5
			areas_dict = peak_top_ion_areas(im_i, peak)
			peak.set_ion_areas(areas_dict)
			
			area_dict = peak.ion_areas
			# print the top 5 ions for each peak
			print(area_dict.keys())
"""



