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

import os
import copy
import types
import pickle

import pytest
from tests.constants import *

import numpy

from pyms.IntensityMatrix import IntensityMatrix, build_intensity_matrix, build_intensity_matrix_i, import_leco_csv
from pyms.Spectrum import MassSpectrum
from pyms.IonChromatogram import IonChromatogram

def test_IntensityMatrix(im):
	assert isinstance(im, IntensityMatrix)
	
	IntensityMatrix(im.time_list, im.mass_list, im.intensity_array)
	
	for type in [test_string, test_int, test_float, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			IntensityMatrix(type, im.mass_list, im.intensity_array)
	for type in [test_string, test_int, test_float, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			IntensityMatrix(im.time_list, type, im.intensity_array)
	for type in [test_string, test_int, test_float, test_dict]:
		with pytest.raises(TypeError):
			IntensityMatrix(im.time_list, im.mass_list, type)
	with pytest.raises(ValueError):
		IntensityMatrix(im.time_list, im.mass_list, [test_list_ints])
	with pytest.raises(ValueError):
		IntensityMatrix(im.time_list, test_list_ints, im.intensity_array)


def test_len(im):
	assert len(im) == 2103


def test_equality(im):
	assert im == IntensityMatrix(im.time_list, im.mass_list, im.intensity_array)
	assert im != test_string
	assert im != test_int
	assert im != test_float
	assert im != test_tuple
	assert im != test_list_ints
	assert im != test_list_strs


def test_get_local_size(im):
	with pytest.warns(DeprecationWarning):
		im.get_local_size()


def test_local_size(im):
	assert isinstance(im.local_size, tuple)
	assert isinstance(im.local_size[0], int)
	assert im.local_size[0] == 2103


def test_get_size(im):
	with pytest.warns(DeprecationWarning):
		im.get_size()


def test_size(im):
	# size of intensity matrix (#scans, #bins)
	assert isinstance(im.size, tuple)
	assert isinstance(im.size[0], int)
	assert im.size == (2103, 450)

def test_iter_ms_indices(im):
	iter_ms = im.iter_ms_indices()
	assert isinstance(iter_ms, types.GeneratorType)
	for index, scan in enumerate(iter_ms):
		assert scan == index
	

def test_iter_ic_indices(im):
	iter_ic = im.iter_ic_indices()
	assert isinstance(iter_ic, types.GeneratorType)
	for index, intensity in enumerate(iter_ic):
		assert intensity == index


def test_set_ic_at_index(im):
	im = copy.deepcopy(im)
	
	im.set_ic_at_index(123, im.get_ic_at_index(0))
	assert im.get_ic_at_index(123).time_list == im.get_ic_at_index(0).time_list
	assert all(numpy.equal(im.get_ic_at_index(123).intensity_array, im.get_ic_at_index(0).intensity_array))
	
	for type in [test_dict, test_list_strs, test_list_ints, test_string, test_float]:
		with pytest.raises(TypeError):
			im.set_ic_at_index(type, im.get_ic_at_index(0))
		with pytest.raises(TypeError):
			im.set_ic_at_index(123, type)
	
	
def test_get_ic_at_index(im):
	ic = im.get_ic_at_index(123)
	
	# TODO: Check values for IC
	
	for type in [test_dict, test_list_strs, test_list_ints, test_string, test_float]:
		with pytest.raises(TypeError):
			im.get_ic_at_index(type)
	with pytest.raises(IndexError):
		im.get_ic_at_index(test_int)


def test_get_ic_at_mass(im):
	# TODO: im.get_ic_at_mass() # Broken
	ic = im.get_ic_at_mass(123)
	
	assert isinstance(ic, IonChromatogram)
	assert not ic.is_tic()
	assert len(ic) == 2103
	assert isinstance(ic.intensity_array, numpy.ndarray)
	assert ic.get_time_at_index(test_int) == 1304.15599823
	assert ic.time_list[0] == 1.05200003833
	assert ic.mass == 123.2516
	assert ic.time_step == 1.0560000035830972
	assert ic.get_index_at_time(12) == 10
	
	for val in [test_int, 0, test_float]:
		with pytest.raises(IndexError):
			im.get_ic_at_mass(val)
	for type in [test_dict, test_list_strs, test_list_ints, test_string]:
		with pytest.raises(TypeError):
			im.get_ic_at_mass(type)


def test_get_ms_at_index(im):
	ms = im.get_ms_at_index(123)
	assert isinstance(ms, MassSpectrum)
	
	assert isinstance(ms.mass_list, list)
	assert ms.mass_list[123] == 173.2516
	assert isinstance(ms.mass_spec, list)
	
	scan = im.get_scan_at_index(123)
	assert ms.mass_spec[123] == 0.0
	assert ms.mass_spec[123] == scan[123]
	assert ms.mass_spec[20] == 0.0
	assert ms.mass_spec[20] == scan[20]
	
	for type in [test_dict, test_list_strs, test_list_ints, test_string]:
		with pytest.raises(TypeError):
			im.get_ms_at_index(type)


def test_get_scan_at_index(im):
	scan = im.get_scan_at_index(test_int)
	
	assert isinstance(scan, list)
	
	assert scan[123] == 0.0
	assert scan[20] == 2314.0
	
	for type in [test_dict, test_list_strs, test_list_ints, test_string, test_float]:
		with pytest.raises(TypeError):
			im.get_scan_at_index(type)
	with pytest.raises(IndexError):
		im.get_scan_at_index(-1)
	with pytest.raises(IndexError):
		im.get_scan_at_index(1000000)


def test_mass_index(im):
	"""
	get_mass_at_index
	get_index_of_mass
	"""
	
	# the index of the nearest mass to 73.3m/z
	index = im.get_index_of_mass(73.3)
	assert isinstance(index, int)
	assert index == 23
	
	# the nearest mass to 73.3m/z
	assert isinstance(im.get_mass_at_index(index), float)
	assert im.get_mass_at_index(index) == 73.2516
	
	for type in [test_string, test_list_strs, test_list_ints, test_dict]:
		with pytest.raises(TypeError):
			im.get_index_of_mass(type)
		
	for type in [test_float, test_string, test_list_strs, test_list_ints, test_dict]:
		with pytest.raises(TypeError):
			im.get_mass_at_index(type)
	
	with pytest.raises(IndexError):
		im.get_mass_at_index(-1)
	with pytest.raises(IndexError):
		im.get_mass_at_index(1000000)


def test_crop_mass(im):
	im = copy.deepcopy(im)
	
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			im.crop_mass(type, 200)
	
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			im.crop_mass(100, type)
	
	with pytest.raises(ValueError):
		im.crop_mass(200, 100)
	
	im.crop_mass(100, 200)
	
	with pytest.raises(ValueError):
		im.crop_mass(50, 200)
	with pytest.raises(ValueError):
		im.crop_mass(150, 500)
	
	im.crop_mass(101.5, 149.5)

	
def test_null_mass(im):
	im = copy.deepcopy(im)
	
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			im.null_mass(type)
	
	with pytest.raises(IndexError):
		im.null_mass(500)
	with pytest.raises(IndexError):
		im.null_mass(10)
	
	im.null_mass(120)
	
	# TODO: Check that the nulling worked
	print(sum(im.get_ic_at_mass(120).intensity_array))

	
def test_reduce_mass_spectra(im):
	im = copy.deepcopy(im)
	# TODO:
	
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			im.reduce_mass_spectra(type)

	
def test_export_ascii(im, outputdir):
	"""
	Export the entire IntensityMatrix as CSV. This will create
	data.im.csv, data.mz.csv, and data.rt.csv where
	these are the intensity matrix, retention time
	vector, and m/z vector in the CSV format
	"""
	
	im.export_ascii(outputdir/"im_ascii")
	im.export_ascii(outputdir/"im_csv", format="csv")
	
	# TODO check exported files
	
	for type in [test_dict, test_list_ints, test_list_strs, test_int, test_float]:
		with pytest.raises(TypeError):
			im.export_ascii(type)
		with pytest.raises(ValueError):
			im.export_ascii(test_string, type)

	
def test_export_leco_csv(im, outputdir):
	"""
	Export the entire IntensityMatrix as LECO CSV. This is
	useful for import into AnalyzerPro
	"""
	
	im.export_leco_csv(outputdir/"im_leco.csv")
	
	for type in [test_dict, test_list_ints, test_list_strs, test_int, test_float]:
		with pytest.raises(TypeError):
			im.export_leco_csv(type)

	
def test_import_leco_csv(im, outputdir):
	imported_im = import_leco_csv(outputdir/"im_leco.csv")
	assert isinstance(imported_im, IntensityMatrix)
	for imported, original in zip(imported_im.time_list, im.time_list):
		assert f"{imported:.3f}" == f"{original:.3f}"
	for imported, original in zip(imported_im.mass_list, im.mass_list):
		assert f"{imported:.0f}" == f"{original:.0f}"
	for imported1, original1 in zip(imported_im.intensity_array, im.intensity_array):
		for imported2, original2 in zip(imported1, original1):
			assert f"{imported2:.6e}" == f"{original2:.6e}"
	
	
	# Check size to original
	print("Output dimensions:", im.size, " Input dimensions:", imported_im.size)
	
	for type in [test_dict, test_list_ints, test_list_strs, test_int, test_float]:
		with pytest.raises(TypeError):
			import_leco_csv(type)
		

def test_IntensityMatrix_custom(data):
	# IntensityMatrix
	# must build intensity matrix before accessing any intensity matrix methods.
	
	# bin interval of 0.5, eg. for double charge ions
	# intensity matrix, bin interval = 0.5, boundary +/- 0.25
	im = build_intensity_matrix(data, 0.5, 0.25, 0.25)
	assert isinstance(im, IntensityMatrix)
	
	# size of intensity matrix (#scans, #bins)
	assert isinstance(im.size, tuple)
	assert im.size == (2103, 900)
	
	# start mass
	assert isinstance(im.min_mass, float)
	assert im.min_mass == 50.2516
	
	# end mass
	assert isinstance(im.max_mass, float)
	assert im.max_mass == 499.7516
	
	# the index of the nearest mass to 73.3m/z
	index = im.get_index_of_mass(73.3)
	assert isinstance(index, int)
	assert index == 46
	
	# the nearest mass to 73.3m/z
	assert isinstance(im.get_mass_at_index(index), float)
	assert im.get_mass_at_index(index) == 73.2516
	
	# get the list of masses (bin centers), and print the first ten
	masses = im.mass_list
	assert isinstance(masses, list)
	assert masses[0] == 50.2516


def test_build_intensity_matrix(data):
	# todo
	
	for type in [test_dict, test_list_ints, test_list_strs, test_string, test_int, test_float]:
		with pytest.raises(TypeError):
			build_intensity_matrix(type)
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			build_intensity_matrix(data, bin_interval=type)
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			build_intensity_matrix(data, bin_left=type)
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			build_intensity_matrix(data, bin_right=type)
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			build_intensity_matrix(data, min_mass=type)
	with pytest.raises(ValueError):
		build_intensity_matrix(data, bin_interval=0)


def test_build_intensity_matrix_i(data, im_i):
	assert isinstance(im_i, IntensityMatrix)
	
	# size of intensity matrix (#scans, #bins)
	assert isinstance(im_i.size, tuple)
	assert im_i.size == (2103, 450)
	
	# start mass
	assert isinstance(im_i.min_mass, int)
	assert im_i.min_mass == 50
	
	# end mass
	assert isinstance(im_i.max_mass, int)
	assert im_i.max_mass == 499
	
	# the index of the nearest mass to 73.3m/z
	index = im_i.get_index_of_mass(73.3)
	assert isinstance(index, int)
	assert index == 23
	
	# the nearest mass to 73.3m/z
	assert isinstance(im_i.get_mass_at_index(index), int)
	assert im_i.get_mass_at_index(index) == 73
	
	# get the list of masses (bin centers), and print the first ten
	masses = im_i.mass_list
	assert isinstance(masses, list)
	assert masses[0] == 50
	
	for type in [test_dict, test_list_ints, test_list_strs, test_string, test_int, test_float]:
		with pytest.raises(TypeError):
			build_intensity_matrix_i(type)
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			build_intensity_matrix_i(data, bin_left=type)
	for type in [test_dict, test_list_ints, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			build_intensity_matrix_i(data, bin_right=type)


# Inherited Methods from pymsBaseClass

def test_dump(im_i, outputdir):
	im_i.dump(outputdir / "im_i_dump.dat")
	
	# Errors
	for type in [test_list_strs, test_dict, test_list_ints, test_tuple, test_int, test_float]:
		with pytest.raises(TypeError):
			im_i.dump(type)
	
	# Read and check values
	assert (outputdir / "im_i_dump.dat").exists()
	loaded_im_i = pickle.load((outputdir / "im_i_dump.dat").open("rb"))
	assert loaded_im_i == im_i
	assert len(loaded_im_i) == len(im_i)


# Inherited Methods from TimeListMixin

def test_time_list(im):
	time = im.time_list
	assert isinstance(time, list)
	# number of retention times
	assert len(time) == 2103
	# retention time of 1st scan:
	assert isinstance(time[0], float)
	assert time[0] == 1.05200003833


def test_get_time_list(im):
	with pytest.warns(DeprecationWarning):
		im.get_time_list()


# Inherited Methods from MassListMixin

def test_get_mass_list(im):
	with pytest.warns(DeprecationWarning):
		im.get_mass_list()


def test_mass_list(im):
	# get the list of masses (bin centers), and print the first ten
	assert isinstance(im.mass_list, list)
	assert isinstance(im.mass_list[0], float)
	assert im.mass_list[0] == 50.2516


# Inherited Methods from MaxMinMassMixin

def test_get_min_mass(im):
	with pytest.warns(DeprecationWarning):
		im.get_min_mass()


def test_min_mass(im):
	# start mass
	assert isinstance(im.min_mass, float)
	assert im.min_mass == 50.2516


def test_get_max_mass(im):
	with pytest.warns(DeprecationWarning):
		im.get_max_mass()


def test_max_mass(im):
	# end mass
	assert isinstance(im.max_mass, float)
	assert im.max_mass == 499.2516


# Inherited Methods from IntensityArrayMixin

def test_intensity_array(im):
	assert isinstance(im.intensity_array, numpy.ndarray)
	assert isinstance(im.intensity_array[0], numpy.ndarray)
	assert isinstance(im.intensity_array[0][0], float)
	assert im.intensity_array[0][0] == 0.0
	assert im.intensity_array[2][3] == 1216.0
	print(im.intensity_array)
	

def test_intensity_matrix(im):
	assert isinstance(im.intensity_matrix, numpy.ndarray)
	assert isinstance(im.intensity_matrix[0], numpy.ndarray)
	assert isinstance(im.intensity_matrix[0][0], float)
	assert im.intensity_matrix[0][0] == 0.0
	assert im.intensity_matrix[2][3] == 1216.0
	assert im.intensity_matrix[0][0] == im.intensity_array[0][0]
	assert numpy.equal(im.intensity_matrix.all(), im.intensity_array.all())


def test_get_intensity_array(im):
	with pytest.warns(DeprecationWarning):
		im.get_intensity_array()


def test_intensity_array_list(im):
	assert isinstance(im.intensity_array_list, list)
	assert isinstance(im.intensity_array_list[0], list)
	assert isinstance(im.intensity_array_list[0][0], float)
	assert im.intensity_array_list[0][0] == 0.0
	assert im.intensity_array_list[2][3] == 1216.0
	assert im.intensity_array[0][0] == im.intensity_array_list[0][0]
	assert im.intensity_array_list == im.intensity_array.tolist()
	

def test_get_matrix_list(im):
	with pytest.warns(DeprecationWarning):
		im.get_matrix_list()


def test_matrix_list(im):
	assert isinstance(im.matrix_list, numpy.ndarray)


# Inherited methods from GetIndexTimeMixin

def test_get_index_at_time(im):
	assert im.get_index_at_time(test_int) == 1168
	assert im.get_index_at_time(test_float) == 11
	
	for type in [test_string, test_list_ints, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			im.get_index_at_time(type)
	
	with pytest.raises(IndexError):
		im.get_index_at_time(-1)
	with pytest.raises(IndexError):
		im.get_index_at_time(1000000)


def test_get_time_at_index(im):
	assert im.get_time_at_index(test_int) == 1304.15599823
	
	for type in [test_string, test_list_ints, test_list_strs, test_dict, test_float]:
		with pytest.raises(TypeError):
			im.get_time_at_index(type)
	
	with pytest.raises(IndexError):
		im.get_time_at_index(-1)
	with pytest.raises(IndexError):
		im.get_time_at_index(1000000)


# TODO; Saving data
"""
# save the intensity matrix values to a file
mat = im.get_matrix_list()
print("saving intensity matrix intensity values...")
save_data("output/im.dat", mat)

"""
