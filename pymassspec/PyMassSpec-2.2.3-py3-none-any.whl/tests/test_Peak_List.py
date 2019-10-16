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
from pyms.Peak import Peak
from pyms.Spectrum import MassSpectrum
from pyms.Peak.Function import peak_sum_area
from pyms.Peak.List import *
from pyms.Peak.List.IO import *
from pyms.base import _list_types


def test_composite_peak(filtered_peak_list, im_i):
	print(".", end='')
	composite_peak_list = filtered_peak_list[10:20]
	print(".", end='')
	peak = composite_peak(composite_peak_list)
	print(".", end='')
	assert isinstance(peak, Peak)
	
	uid = peak.UID
	assert uid == '96-69-62-47.73'
	
	assert peak.get_third_highest_mz() == 57
	assert peak.bounds is None
	assert peak.get_int_of_ion(100) == 3.603215488138507
	assert peak.rt == 47.727200388899995
	assert peak.ic_mass is None
	assert peak.top_ions(10)[0] == 115
	
	#area = peak_sum_area(im_i, peak)
	#peak.area = area
	#assert peak.area == area

	assert isinstance(peak.mass_spectrum, MassSpectrum)
	assert isinstance(peak.mass_spectrum.mass_spec, _list_types)
	peak.null_mass(73)
	index_73 = peak.mass_spectrum.mass_list.index(73)
	assert peak.mass_spectrum.mass_spec[index_73] == 0

	peak.crop_mass(100, 200)
	assert peak.UID != uid

	# Errors
	for type in [test_dict, test_list_ints, test_list_strs, test_float, test_string, test_tuple, test_int]:
		with pytest.raises(TypeError):
			composite_peak(type)


def test_composite_peak_outliers(filtered_peak_list, im_i):
	composite_peak_list = filtered_peak_list[10:13]
	peak = composite_peak(composite_peak_list, ignore_outliers=True)
	assert isinstance(peak, Peak)
	
	uid = peak.UID
	assert uid == '88-86-92-39.07'
	
	assert peak.get_third_highest_mz() == 85
	assert peak.bounds is None
	assert peak.get_int_of_ion(100) == 7.1236965120460285
	assert peak.rt == 39.0680015087
	assert peak.ic_mass is None
	assert peak.top_ions(10)[0] == 161
	
	#area = peak_sum_area(im_i, peak)
	#peak.area = area
	#assert peak.area == area

	peak.null_mass(73)
	index_73 = peak.mass_spectrum.mass_list.index(73)
	assert peak.mass_spectrum.mass_spec[index_73] == 0

	peak.crop_mass(100, 200)
	assert peak.UID != uid


def test_fill_peaks(im_i, peak_list):
	filled_peak_list = fill_peaks(im_i, peak_list, 10.0)
	assert is_peak_list(filled_peak_list)
	
	# Errors
	for type in [test_dict, test_list_ints, test_list_strs, test_float, test_string, test_tuple, test_int]:
		with pytest.raises(TypeError):
			fill_peaks(im_i, type, 10.0)
	for type in [test_dict, test_list_ints, test_list_strs, test_string, test_tuple, test_int]:
		with pytest.raises(TypeError):
			fill_peaks(im_i, peak_list, type)


def test_is_peak_list(peak_list, ms, im_i, data):
	assert is_peak_list(peak_list)
	assert not is_peak_list(test_int)
	assert not is_peak_list(test_string)
	assert not is_peak_list(test_float)
	assert not is_peak_list(test_list_strs)
	assert not is_peak_list(test_list_ints)
	assert not is_peak_list(test_tuple)
	assert not is_peak_list(test_dict)
	assert not is_peak_list(ms)
	assert not is_peak_list(im_i)
	assert not is_peak_list(data)


def test_sele_peaks_by_rt(filtered_peak_list):
	selected_peaks = sele_peaks_by_rt(filtered_peak_list, ("12m", "13m"))
	assert is_peak_list(selected_peaks)
	assert len(selected_peaks) == 18
	peak = selected_peaks[0]
	assert isinstance(peak, Peak)
	
	uid = peak.UID
	assert uid == '68-54-26-722.30'
	
	assert peak.get_third_highest_mz() == 50
	assert peak.bounds == [0, 683, 0]
	assert peak.get_int_of_ion(100) == 0.0
	assert peak.rt == 722.299976349
	assert peak.ic_mass is None
	assert peak.top_ions(10)[0] == 133
	
	peak.null_mass(73)
	index_73 = peak.mass_spectrum.mass_list.index(73)
	assert peak.mass_spectrum.mass_spec[index_73] == 0
	
	peak.crop_mass(100, 200)
	assert peak.UID != uid
	
	with pytest.raises(TypeError):
		sele_peaks_by_rt(filtered_peak_list, [1.2, 3.4])
	with pytest.raises(ValueError):
		sele_peaks_by_rt(filtered_peak_list, ["50s", "10s"])
	
	# Errors
	for type in [test_dict, test_list_ints, test_list_strs, test_float, test_string, test_tuple, test_int]:
		with pytest.raises(TypeError):
			sele_peaks_by_rt(type, ("12m", "13m"))
	for type in [test_dict, test_float, test_string, test_int]:
		with pytest.raises(TypeError):
			sele_peaks_by_rt(filtered_peak_list, type)
	for type in [test_list_ints, test_list_strs, test_tuple]:
		with pytest.raises(ValueError):
			sele_peaks_by_rt(filtered_peak_list, type)


def test_store_peaks(filtered_peak_list, outputdir):
	store_peaks(filtered_peak_list, outputdir/"filtered_peak_list.dat")
	
	# Errors
	for type in [test_dict, test_list_ints, test_list_strs, test_float, test_tuple, test_int, test_string]:
		with pytest.raises(TypeError):
			store_peaks(type, outputdir/test_string)
	for type in [test_dict, test_list_ints, test_list_strs, test_float, test_tuple, test_int]:
		with pytest.raises(TypeError):
			store_peaks(filtered_peak_list, type)


def test_load_peaks(filtered_peak_list, datadir, outputdir):
	loaded_peak_list = load_peaks(outputdir/"filtered_peak_list.dat")

	assert loaded_peak_list == filtered_peak_list


	# Errors
	for type in [test_dict, test_list_ints, test_list_strs, test_float, test_tuple, test_int]:
		with pytest.raises(TypeError):
			load_peaks(type)
	with pytest.raises(FileNotFoundError):
		load_peaks(test_string)

	with pytest.raises(IOError):
		load_peaks(datadir/"not-an-experiment.expr")
	with pytest.raises(IOError):
		load_peaks(datadir/"test_list_ints.dat")
	with pytest.raises(IOError):
		load_peaks(datadir/"test_empty_list.dat")

