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
import copy

from pyms.TopHat import tophat
from pyms.BillerBiemann import *
from pyms.Noise.SavitzkyGolay import savitzky_golay
from pyms.Peak.Class import Peak
from pyms.Noise.Analysis import window_analyzer


def test_BillerBiemann(im_i):
	im_i = copy.deepcopy(im_i)
	# Intensity matrix size (scans, masses)
	n_scan, n_mz = im_i.size
	
	# noise filter and baseline correct
	for ii in range(n_mz):
		ic = im_i.get_ic_at_index(ii)
		ic_smooth = savitzky_golay(ic)
		ic_bc = tophat(ic_smooth, struct="1.5m")
		im_i.set_ic_at_index(ii, ic_bc)
	
	# Use Biller and Biemann technique to find apexing ions at a scan
	# default is maxima over three scans and not to combine with any neighbouring
	# scan.
	peak_list = BillerBiemann(im_i)
	assert isinstance(peak_list, list)
	assert isinstance(peak_list[0], Peak)
	assert len(peak_list) == 2101
	
	# Find apex oven 9 points and combine with neighbouring peak if two scans apex
	# next to each other.
	peak_list2 = BillerBiemann(im_i, points=9, scans=2)
	assert len(peak_list2) == 805
	
	assert len(peak_list2) <= len(peak_list)
	
	# Errors
	for type in [test_string, test_int, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			BillerBiemann(type)
	
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			BillerBiemann(im_i, points=type)
	
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			BillerBiemann(im_i, scans=type)


def test_rel_threshold(peak_list):
	rel_threshold(peak_list)
	rel_threshold(peak_list, 2.0)
	pl = rel_threshold(peak_list, 2)
	
	assert isinstance(pl, list)
	assert isinstance(pl[0], Peak)
	
	assert len(pl) == 805
	assert len(pl) <= len(peak_list)
	
	# Errors
	with pytest.raises(ValueError):
		rel_threshold(peak_list, percent=0)
	
	for type in [test_string, test_list_ints, test_list_strs, test_dict, test_int, test_tuple]:
		with pytest.raises(TypeError):
			rel_threshold(type)
	
	for type in [test_string, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			rel_threshold(peak_list, percent=type)
			

def test_num_ions_threshold(peak_list, tic):
	"""
	Filter the peak list, first by removing all intensities in a peak less
	than a given relative threshold, then by removing all peaks that have
	less than a given number of ions above a given value
	"""
	
	# trim by relative intensity
	pl = rel_threshold(peak_list, 2)
	
	# trim by threshold
	new_peak_list = num_ions_threshold(pl, 3, 10000)
	assert isinstance(new_peak_list, list)
	assert isinstance(new_peak_list[0], Peak)
	
	assert len(new_peak_list) == 215
	assert len(new_peak_list) <= len(peak_list)
	assert len(new_peak_list) <= len(pl)
	
	# With window_analyzer
	# estimate noise level from the TIC, used later to
	# discern true signal peaks
	noise_level = window_analyzer(tic)
	
	# trim by relative intensity
	apl = rel_threshold(peak_list, 1)
	
	# trim by number of ions above threshold
	peak_list = num_ions_threshold(apl, 3, noise_level)
	
	assert isinstance(peak_list, list)
	assert isinstance(peak_list[0], Peak)
	
	assert len(peak_list) in (87, 88)
	assert len(peak_list) <= len(peak_list)
	
	# Errors
	for type in [test_string, test_int, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			num_ions_threshold(type, 5, 100)
	
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			num_ions_threshold(peak_list, type, 100.0)
	
	for type in [test_string, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			num_ions_threshold(peak_list, 5, type)


def test_sum_maxima(im):
	new_tic = sum_maxima(im)
	assert isinstance(new_tic, IonChromatogram)
	assert new_tic.is_tic()
	
	# Errors
	for type in [test_string, test_int, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			sum_maxima(type)
	
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			sum_maxima(im, points=type)
	
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			sum_maxima(im, scans=type)


def test_get_maxima_indices():
	# TODO: main test
	
	# Errors
	
	for type in [test_string, test_int, test_float, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			get_maxima_indices(type)
	for type in [test_string, test_list_ints, test_float, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_indices(test_list_ints, points=type)


def test_get_maxima_list(tic):
	maxima_iist = get_maxima_list(tic)
	assert isinstance(maxima_iist, list)
	assert isinstance(maxima_iist[0], list)
	assert isinstance(maxima_iist[0][0], float)
	assert maxima_iist[0][0] == 2.10800014436
	
	# Errors
	
	for type in [test_string, test_int, test_float, test_list_strs, test_dict, test_list_ints, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_list(type)
	for type in [test_string, test_list_ints, test_float, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_list(tic, points=type)


def test_get_maxima_list_reduced(tic):
	maxima_iist = get_maxima_list_reduced(tic, 12.34)
	assert isinstance(maxima_iist, list)
	assert isinstance(maxima_iist[0], list)
	assert isinstance(maxima_iist[0][0], float)
	assert maxima_iist[0][0] == 10.5559998751
	
	# Errors
	for type in [test_string, test_int, test_float, test_list_strs, test_dict, test_list_ints, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_list_reduced(type, 0)
	for type in [test_string, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_list_reduced(tic, mp_rt=type)
	for type in [test_string, test_list_ints, test_float, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_list_reduced(tic, test_float, points=type)
	for type in [test_string, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_list_reduced(tic, test_float, window=type)


def test_get_maxima_matrix(peak_list, im, tic):
	maxima_matrix = get_maxima_matrix(im)
	assert isinstance(maxima_matrix, numpy.ndarray)
	# TODO: value check
	
	# Errors
	for type in [test_string, test_int, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_matrix(type)
	
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_matrix(im, points=type)
	
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			get_maxima_matrix(im, scans=type)
