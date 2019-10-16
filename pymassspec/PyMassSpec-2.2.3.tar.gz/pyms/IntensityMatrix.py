"""
Class to model Intensity Matrix
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


import copy
import pathlib
from warnings import warn

import numpy
import deprecation

from pyms import __version__
from pyms.base import pymsBaseClass
from pyms.Mixins import TimeListMixin, MassListMixin, IntensityArrayMixin, GetIndexTimeMixin
from pyms.base import _list_types
from pyms.Utils.IO import save_data
from pyms.IonChromatogram import IonChromatogram
from pyms.Spectrum import MassSpectrum


class IntensityMatrix(pymsBaseClass, TimeListMixin, MassListMixin, IntensityArrayMixin, GetIndexTimeMixin):
	"""
	Intensity matrix of binned raw data

	:author: Andrew Isaac
	:author: Dominic Davis-Foster (type assertions and properties)
	"""
	
	def __init__(self, time_list, mass_list, intensity_array):
		"""
		Initialize the IntensityMatrix data

		:param time_list: Retention time values
		:type time_list: list

		:param mass_list: Binned mass values
		:type mass_list: list

		:param intensity_array: Binned intensity values per scan
		:type intensity_array: list of lists of numbers or numpy.ndarray

		:author: Andrew Isaac
		"""
		
		# sanity check
		if not isinstance(time_list, _list_types) or not isinstance(time_list[0], (int, float)):
			raise TypeError("'time_list' must be a list of numbers")
		
		if not isinstance(mass_list, _list_types) or not isinstance(mass_list[0], (int, float)):
			raise TypeError("'mass_list' must be a list of numbers")

		if not isinstance(intensity_array, numpy.ndarray):
			if not isinstance(intensity_array, _list_types) \
					or not isinstance(intensity_array[0], _list_types) \
					or not isinstance(intensity_array[0][0], (int, float)):
				raise TypeError("'intensity_array' must be a list, of a list, of numbers")
		
			intensity_array = numpy.array(intensity_array)
		
			if not len(time_list) == len(intensity_array):
				raise ValueError("'time_list' is not the same length as 'intensity_array'")
		
		if not len(mass_list) == len(intensity_array[0]):
			raise ValueError("'mass_list' is not the same size as 'intensity_array'")
		
		self._time_list = time_list
		self._mass_list = mass_list
		
		self._intensity_array = intensity_array
		
		self._min_rt = min(time_list)
		self._max_rt = max(time_list)
		
		self._min_mass = min(mass_list)
		self._max_mass = max(mass_list)
		
		# Try to include parallelism.
		try:
			from mpi4py import MPI
			comm = MPI.COMM_WORLD
			num_ranks = comm.Get_size()
			rank = comm.Get_rank()
			M, N = len(intensity_array), len(intensity_array[0])
			lrr = (rank * M / num_ranks, (rank + 1) * M / num_ranks)
			lcr = (rank * N / num_ranks, (rank + 1) * N / num_ranks)
			m, n = (lrr[1] - lrr[0], lcr[1] - lcr[0])
			self.comm = comm
			self.num_ranks = num_ranks
			self.rank = rank
			self.M = M
			self.N = N
			self.local_row_range = lrr
			self.local_col_range = lcr
			self.m = m
			self.n = n
		
		# If we can't import mpi4py then continue in serial.
		except ModuleNotFoundError:
			pass
	
	def __len__(self):
		return len(self.time_list)
	
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.time_list == other.time_list \
				   and self.mass_list == other.mass_list \
				   and numpy.array_equal(self.intensity_array, other.intensity_array)
		return NotImplemented
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details=f"Use '{__qualname__}.local_size' instead")
	def get_local_size(self):
		"""
		Gets the local size of intensity matrix.

		:return: Number of rows and cols
		:rtype: int

		:author: Luke Hodkinson
		"""
		
		return self.local_size
	
	@property
	def local_size(self):
		"""
		Gets the local size of intensity matrix.

		:return: Number of rows and cols
		:rtype: int

		:author: Luke Hodkinson
		"""
		
		# Check for parallel.
		if hasattr(self, 'comm'):
			return self.m, self.n
		
		# If serial call the regular routine.
		return self.size
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details=f"Use '{__qualname__}.size' instead")
	def get_size(self):
		"""
		Gets the size of intensity matrix

		:return: Number of rows and cols
		:rtype: int

		:author: Qiao Wang
		:author: Andrew Isaac
		:author: Luke Hodkinson
		:author: Vladimir Likic
		"""
		
		return self.size
	
	@property
	def size(self):
		"""
		Gets the size of intensity matrix

		:return: Number of rows and cols
		:rtype: int

		:author: Qiao Wang
		:author: Andrew Isaac
		:author: Luke Hodkinson
		:author: Vladimir Likic
		"""
		
		n_scan = len(self._intensity_array)
		n_mz = len(self._intensity_array[0])
		
		return n_scan, n_mz
	
	def iter_ms_indices(self):
		"""
		Iterates over local row indices

		:return: Current row index
		:rtype: int

		:author: Luke Hodkinson
		"""
		
		# Check for parallel.
		if hasattr(self, 'comm'):
			# At the moment we assume we break the matrix into contiguous
			# ranges. We've allowed for this to change by wrapping up the
			# iteration in this method.
			for i in range(self.local_row_range[0], self.local_row_range[1]):
				yield i
		
		else:
			# Iterate over global indices.
			n_scan = len(self._intensity_array)
			for i in range(0, n_scan):
				yield i
	
	def iter_ic_indices(self):
		"""
		Iterate over local column indices

		:return: Current column index
		:rtype: int

		:author: Luke Hodkinson
		"""
		
		# Check for parallel.
		if hasattr(self, 'comm'):
			# At the moment we assume we break the matrix into contiguous
			# ranges. We've allowed for this to change by wrapping up the
			# iteration in this method.
			for i in range(self.local_col_range[0], self.local_col_range[1]):
				yield i
		
		else:
			# Iterate over global indices.
			n_mz = len(self._intensity_array[0])
			for i in range(0, n_mz):
				yield i
	
	def set_ic_at_index(self, ix, ic):
		"""
		Sets the ion chromatogram specified by index to a new
			value

		:param ix: Index of an ion chromatogram in the intensity data
			matrix to be set
		:type ix: int
		:param ic: Ion chromatogram that will be copied at position 'ix'
			in the data matrix
		:type: IonChromatogram

		The length of the ion chromatogram must match the appropriate
		dimension of the intensity matrix.

		:author: Vladimir Likic
		"""
		
		if not isinstance(ix, int):
			raise TypeError("'ix' must be an an integer")
		
		if not isinstance(ic, IonChromatogram):
			raise TypeError("'ic' must be an IonChromaogram object")
		
		# this returns an numpy.array object
		ia = ic.intensity_array
		
		# check if the dimension is ok
		if len(ia) != len(self._intensity_array):
			raise ValueError("ion chromatogram incompatible with the intensity matrix")
		else:
			N = len(ia)
		
		# Convert 'ia' to a list. By convention, the attribute
		# _intensity_array of the class IntensityMatrix is a list
		# of lists. This makes pickling instances of IntensityMatrix
		# practically possible, since pickling numpy.array objects
		# produces ten times larger files compared to pickling python
		# lists.
		ial = ia.tolist()
		for i in range(N):
			self._intensity_array[i][ix] = ial[i]
	
	def get_ic_at_index(self, ix):
		
		"""
		Returns the ion chromatogram at the specified index

		:param ix: Index of an ion chromatogram in the intensity data
			matrix
		:type ix: int

		:return: Ion chromatogram at given index
		:rtype: IonChromatogram

		:author: Qiao Wang
		:author: Andrew Isaac
		:author: Vladimir Likic
		"""
		
		if not isinstance(ix, int):
			raise TypeError("'ix' must be an integer")
		
		ia = []
		for i in range(len(self._intensity_array)):
			ia.append(self._intensity_array[i][ix])
		
		ic_ia = numpy.array(ia)
		mass = self.get_mass_at_index(ix)
		rt = copy.deepcopy(self._time_list)
		
		return IonChromatogram(ic_ia, rt, mass)
	
	def get_ic_at_mass(self, mass=None):
		
		"""
		Returns the ion chromatogram for the specified mass.
			The nearest binned mass to mass is used.

			If no mass value is given, the function returns the total
			ion chromatogram.

		:param mass: Mass value of an ion chromatogram
		:type mass: int

		:return: Ion chromatogram for given mass
		:rtype: IonChromatogram

		:author: Andrew Isaac
		:author: Vladimir Likic
		"""
		
		if mass is None:
			return self.tic
		
		if mass < self._min_mass or mass > self._max_mass:
			print("min mass: ", self._min_mass, "max mass:", self._max_mass)
			raise IndexError("mass is out of range")
		
		ix = self.get_index_of_mass(mass)
		
		return self.get_ic_at_index(ix)
	
	def get_ms_at_index(self, ix):
		
		"""
		Returns a mass spectrum for a given scan index

		:param ix: The index of the scan
		:type ix: int

		:return: Mass spectrum
		:rtype: pyms.MassSpectrum.MassSpectrum

		:author: Andrew Isaac
		"""
		
		if not isinstance(ix, int):
			raise TypeError("'ix' must be an an integer")
		
		scan = self.get_scan_at_index(ix)
		
		return MassSpectrum(self.mass_list, scan)
	
	def get_scan_at_index(self, ix):
		
		"""
		Returns the spectral intensities for scan index

		:param ix: The index of the scan
		:type ix: int

		:return: Intensity values of scan spectra
		:rtype: list

		:author: Andrew Isaac
		"""
		
		if not isinstance(ix, int):
			raise TypeError("'ix' must be an an integer")
		
		if ix < 0 or ix >= len(self._intensity_array):
			raise IndexError("index out of range")
		
		return self._intensity_array[ix].tolist()
	
	def get_mass_at_index(self, ix):
		
		"""
		Returns binned mass at index

		:param ix: Index of binned mass
		:type ix: int

		:return: Binned mass
		:rtype: int

		:author: Andrew Isaac
		"""
		
		if not isinstance(ix, int):
			raise TypeError("'ix' must be an an integer")
		
		if ix < 0 or ix >= len(self._mass_list):
			raise IndexError("index out of range")
		
		return self._mass_list[ix]
	
	def get_index_of_mass(self, mass):
		"""
		Returns the index of mass in the list of masses

		The nearest binned mass to given mass is used.

		:param mass: Mass to lookup in list of masses
		:type mass: float

		:return: Index of mass closest to given mass
		:rtype: int

		:author: Andrew Isaac
		"""
		
		best = self._max_mass
		ix = 0
		for ii in range(len(self._mass_list)):
			tmp = abs(self._mass_list[ii] - mass)
			if tmp < best:
				best = tmp
				ix = ii
		return ix
	
	def crop_mass(self, mass_min, mass_max):
		
		"""
		Crops mass spectrum

		:param mass_min: Minimum mass value
		:type mass_min: int or float
		:param mass_max: Maximum mass value
		:type mass_max: int or float

		:return: none
		:rtype: NoneType

		:author: Andrew Isaac
		"""
		
		if not isinstance(mass_min, (int, float)) or not isinstance(mass_max, (int, float)):
			raise TypeError("'mass_min' and 'mass_max' must be numbers")
		if mass_min >= mass_max:
			raise ValueError("'mass_min' must be less than 'mass_max'")
		if mass_min < self._min_mass:
			raise ValueError(f"'mass_min' is less than the smallest mass: {self._min_mass:.3f}")
		if mass_max > self._max_mass:
			raise ValueError(f"'mass_max' is greater than the largest mass: {self._max_mass:.3f}")
		
		# pre build mass_list and list of indecies
		mass_list = self._mass_list
		new_mass_list = []
		ii_list = []
		for ii in range(len(mass_list)):
			mass = mass_list[ii]
			if mass_min <= mass <= mass_max:
				new_mass_list.append(mass)
				ii_list.append(ii)
		
		# update intensity matrix
		im = self._intensity_array.tolist()
		for spec_jj in range(len(im)):
			new_spec = []
			for ii in ii_list:
				new_spec.append(im[spec_jj][ii])
			im[spec_jj] = new_spec
		self._intensity_array = numpy.array(im)
		
		self._mass_list = new_mass_list
		self._min_mass = min(new_mass_list)
		self._max_mass = max(new_mass_list)
	
	def null_mass(self, mass):
		"""
		Ignore given (closest) mass in spectra

		:param mass: Mass value to remove
		:type mass: int or float

		:author: Andrew Isaac
		"""
		
		if not isinstance(mass, (int, float)):
			raise TypeError("'mass' must be numbers")
		if mass < self._min_mass or mass > self._max_mass:
			raise IndexError(f"'mass' not in mass range: {self._min_mass:.3f} to {self._max_mass:.3f}")
		
		ii = self.get_index_of_mass(mass)
		
		im = self._intensity_array
		for spec_jj in range(len(im)):
			im[spec_jj][ii] = 0
	
	def reduce_mass_spectra(self, N=5):
		"""
		Reduces mass spectra by retaining top N
			intensities, discarding all other intensities.

		:param N: The number of top intensities to keep
		:type N: int

		:author: Vladimir Likic
		"""
		
		if not isinstance(N, (int, float)):
			raise TypeError("'N' must be a number")
		
		# loop over all mass spectral scans
		for ii in range(len(self._intensity_array)):
			
			# get the next mass spectrum as list of intensities
			intensity_list = self._intensity_array[ii]
			n = len(intensity_list)
			
			# get the indices of top N intensities
			top_indices = list(range(n))
			top_indices.sort(key=lambda i: intensity_list[i], reverse=True)
			top_indices = top_indices[:N]
			
			# initiate new mass spectrum, and retain only top N intensities
			intensity_list_new = []
			
			for jj in range(n):
				intensity_list_new.append(0.0)
				if jj in top_indices:
					intensity_list_new[jj] = intensity_list[jj]
			
			self._intensity_array[ii] = intensity_list_new
	
	def export_ascii(self, root_name, format='dat'):
		"""
		Exports the intensity matrix, retention time vector, and
			m/z vector to the ascii format

			By default, export_ascii("NAME") will create NAME.im.dat, NAME.rt.dat,
			and NAME.mz.dat where these are the intensity matrix, retention
			time vector, and m/z vector in tab delimited format. If format='csv',
			the files will be in the CSV format, named NAME.im.csv, NAME.rt.csv,
			and NAME.mz.csv.

		:param root_name: Root name for the output files
		:type root_name: str or pathlib.Path
		:param format:
		:type format: str


		:return: none
		:rtype: NoneType

		:author: Milica Ng
		:author: Andrew Isaac
		:author: Vladimir Likic
		:author: Dominic Davis-Foster (pathlib support)
		"""
		
		if not isinstance(root_name, (str, pathlib.Path)):
			raise TypeError("'root_name' must be a string or a pathlib.Path object")
		
		if not isinstance(root_name, pathlib.Path):
			root_name = pathlib.Path(root_name)
		
		if not root_name.parent.is_dir():
			root_name.parent.mkdir(parents=True)
		
		if format == 'dat':
			separator = " "
		elif format == 'csv':
			separator = ","
		else:
			raise ValueError(f"Unknown format '{format}'. Only 'dat' and 'csv' supported")
		
		# export 2D matrix of intensities
		vals = self._intensity_array
		save_data(f"{root_name}.im.{format}", vals, sep=separator)
		
		# export 1D vector of m/z's, corresponding to rows of
		# the intensity matrix
		mass_list = self._mass_list
		save_data(f"{root_name}.mz.{format}", mass_list, sep=separator)
		
		# export 1D vector of retention times, corresponding to
		# columns of the intensity matrix
		time_list = self._time_list
		save_data(f"{root_name}.rt.{format}", time_list, sep=separator)
	
	def export_leco_csv(self, file_name):
		"""
		Exports data in LECO CSV format

		:param file_name: The name of the file
		:type file_name: str or pathlib.Path

		:author: Andrew Isaac
		:author: Vladimir Likic
		:author: Dominic Davis-Foster (pathlib support)
		"""
		
		if not isinstance(file_name, (str, pathlib.Path)):
			raise TypeError("'file_name' must be a string or a pathlib.Path object")
		
		if not isinstance(file_name, pathlib.Path):
			file_name = pathlib.Path(file_name)
		
		if not file_name.parent.is_dir():
			file_name.parent.mkdir(parents=True)
		
		mass_list = self._mass_list
		time_list = self._time_list
		vals = self._intensity_array
		
		fp = file_name.open("w")
		
		# Format is text header with:
		# "Scan","Time",...
		# and the rest is "TIC" or m/z as text, i.e. "50","51"...
		# The following lines are:
		# scan_number,time,value,value,...
		# scan_number is an int, rest seem to be fixed format floats.
		# The format is 0.000000e+000
		
		# write header
		fp.write("\"Scan\",\"Time\"")
		for ii in mass_list:
			if isinstance(ii, (int, float)):
				fp.write(f",\"{int(ii):d}\"")
			else:
				raise TypeError("mass list datum not a number")
		fp.write("\r\n")  # windows CR/LF
		
		# write lines
		for ii in range(len(time_list)):
			fp.write(f"{ii},{time_list[ii]:#.6e}")
			for jj in range(len(vals[ii])):
				if isinstance(vals[ii][jj], (int, float)):
					fp.write(f",{vals[ii][jj]:#.6e}")
				else:
					raise TypeError("datum not a number")
			fp.write("\r\n")
		
		fp.close()
	
	
def import_leco_csv(file_name):
	"""
	Imports data in LECO CSV format

	:param file_name: Path of the file to read
	:type file_name: str or pathlib.Path

	:return: Data as an IntensityMatrix
	:rtype: pyms.IntensityMatrix.IntensityMatrix

	:author: Andrew Isaac
	:author: Dominic Davis-Foster (pathlib support)
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	if not isinstance(file_name, pathlib.Path):
		file_name = pathlib.Path(file_name)
	
	lines_list = file_name.open('r')
	data = []
	time_list = []
	mass_list = []
	
	# Format is text header with:
	# "Scan","Time",...
	# and the rest is "TIC" or m/z as text, i.e. "50","51"...
	# The following lines are:
	# scan_number,time,value,value,...
	# scan_number is an int, rest seem to be fixed format floats.
	# The format is 0.000000e+000
	
	num_mass = 0
	FIRST = True
	HEADER = True
	data_col = -1
	time_col = -1
	# get each line
	for line in lines_list:
		cols = -1
		data_row = []
		if len(line.strip()) > 0:
			data_list = line.strip().split(',')
			# get each value in line
			for item in data_list:
				item = item.strip()
				item = item.strip('\'"')  # remove quotes (in header)
				
				# Get header
				if HEADER:
					cols += 1
					if len(item) > 0:
						if item.lower().find("time") > -1:
							time_col = cols
						try:
							value = float(item)
							# find 1st col with number as header
							if FIRST and value > 1:  # assume >1 mass
								data_col = cols
								# assume time col is previous col
								if time_col < 0:
									time_col = cols - 1
								FIRST = False
							mass_list.append(value)
							num_mass += 1
						except ValueError:
							pass
				# Get rest
				else:
					cols += 1
					if len(item) > 0:
						try:
							value = float(item)
							if cols == time_col:
								time_list.append(value)
							elif cols >= data_col:
								data_row.append(value)
						except ValueError:
							pass
			
			# check row length
			if not HEADER:
				if len(data_row) == num_mass:
					data.append(data_row)
				else:
					warn("ignoring row")
			
			HEADER = False
	
	# check col lengths
	if len(time_list) != len(data):
		warn("number of data rows and time list length differ")
	
	return IntensityMatrix(time_list, mass_list, data)


def build_intensity_matrix(data, bin_interval=1, bin_left=0.5, bin_right=0.5, min_mass=None):
	"""
	Sets the full intensity matrix with flexible bins

	:param data: Raw GCMS data
	:type data: pyms.GCMS.Class.GCMS_data
	:param bin_interval: interval between bin centres (default 1)
	:type bin_interval: int or float
	:param bin_left: left bin boundary offset (default 0.5)
	:type bin_left: float
	:param bin_right: right bin boundary offset (default 0.5)
	:type bin_right: float
	:param min_mass: Minimum mass to bin (default minimum mass from data)
	:type min_mass: bool
	
	:return: Binned IntensityMatrix object
	:rtype: pyms.IntensityMatrix.IntensityMatrix

	:author: Qiao Wang
	:author: Andrew Isaac
	:author: Vladimir Likic
	"""
	
	from pyms.GCMS.Class import GCMS_data
	
	if not isinstance(data, GCMS_data):
		raise TypeError("'data' must be a GCMS_data object")
	if bin_interval <= 0:
		raise ValueError("The bin interval must be larger than zero.")
	if not isinstance(bin_left, (int, float)):
		raise TypeError("'bin_left' must be a number.")
	if not isinstance(bin_right, (int, float)):
		raise TypeError("'bin_right' must be a number.")
	
	if not min_mass:
		min_mass = data.min_mass
	max_mass = data.max_mass
	
	return __fill_bins(data, min_mass, max_mass, bin_interval, bin_left, bin_right)


def build_intensity_matrix_i(data, bin_left=0.3, bin_right=0.7):
	"""
	Sets the full intensity matrix with integer bins

	:param data: Raw GCMS data
	:type data: pyms.GCMS.Class.GCMS_data

	:param bin_left: left bin boundary offset (default 0.3)
	:type bin_left: float

	:param bin_right: right bin boundary offset (default 0.7)
	:type bin_right: float

	:return: Binned IntensityMatrix object
	:rtype: pyms.IntensityMatrix.IntensityMatrix

	:author: Qiao Wang
	:author: Andrew Isaac
	:author: Vladimir Likic
	"""
	
	from pyms.GCMS.Class import GCMS_data
	
	if not isinstance(data, GCMS_data):
		raise TypeError("'data' must be a GCMS_data object")
	if not isinstance(bin_left, (int, float)):
		raise TypeError("'bin_left' must be a number.")
	if not isinstance(bin_right, (int, float)):
		raise TypeError("'bin_right' must be a number.")
	
	min_mass = data.min_mass
	max_mass = data.max_mass
	
	# Calculate integer min mass based on right boundary
	bin_right = abs(bin_right)
	min_mass = int(min_mass + 1 - bin_right)
	
	return __fill_bins(data, min_mass, max_mass, 1, bin_left, bin_right)


def __fill_bins(data, min_mass, max_mass, bin_interval, bin_left, bin_right):
	"""
	Fills the intensity values for all bins

	:param data: Raw GCMS data
	:type data: class:`pyms.GCMS.Class.GCMS_data`
	:param min_mass: minimum mass value
	:type min_mass: int or float
	:param max_mass: maximum mass value
	:type max_mass: int or float
	:param bin_interval: interval between bin centres
	:type bin_interval: int or float
	:param bin_left: left bin boundary offset
	:type bin_left: float
	:param bin_right: right bin boundary offset
	:type bin_right: float

	:return: Binned IntensityMatrix object
	:rtype: class:`pyms.IntensityMatrix.IntensityMatrix`

	:author: Qiao Wang
	:author: Andrew Isaac
	:author: Moshe Olshansky
	:author: Vladimir Likic
	"""

	if not (abs(bin_left+bin_right-bin_interval) < 1.0e-6*bin_interval):
		raise ValueError("there should be no gaps or overlap.")

	bin_left = abs(bin_left)
	bin_right = abs(bin_right)

	# To convert to int range, ensure bounds are < 1
	bl = bin_left - int(bin_left)

	# Number of bins
	num_bins = int(float(max_mass+bl-min_mass)/bin_interval)+1

	# initialise masses to bin centres
	mass_list = [i * bin_interval + min_mass for i in range(num_bins)]

	# Modified binning loops. I've replaced the deepcopy getting routines with
	# the alias properties. This way we can avoid performing the copies when
	# it is clear that we do not intend on modifying the contents of the arrays
	# here.
	#           - Luke Hodkinson, 18/05/2010

	# fill the bins
	intensity_matrix = []
	for scan in data.scan_list: # use the alias, not the copy (Luke)
		intensity_list = [0.0] * num_bins
		masses = scan.mass_list # use the alias, not the copy (Luke)
		intensities = scan.intensity_list # use the alias, not the copy (Luke)
		for ii in range(len(masses)):
			mm = int((masses[ii] + bl - min_mass)/bin_interval)
			intensity_list[mm] += intensities[ii]
		intensity_matrix.append(intensity_list)

	return IntensityMatrix(data.time_list, mass_list, intensity_matrix)


def __fill_bins_old(data, min_mass, max_mass, bin_interval, bin_left, bin_right):
	"""
	Fills the intensity values for all bins

	:param data: Raw GCMS data
	:type data: class:`pyms.GCMS.Class.GCMS_data`
	:param min_mass: minimum mass value
	:type min_mass: int or float
	:param max_mass: maximum mass value
	:type max_mass: int or float
	:param bin_interval: interval between bin centres
	:type bin_interval: int or float
	:param bin_left: left bin boundary offset
	:type bin_left: float
	:param bin_right: right bin boundary offset
	:type bin_right: float

	:return: Binned IntensityMatrix object
	:rtype: class:`pyms.IntensityMatrix.IntensityMatrix`

	:author: Qiao Wang
	:author: Andrew Isaac
	:author: Vladimir Likic
	"""
	
	bin_left = abs(bin_left)
	bin_right = abs(bin_right)

	# To convert to int range, ensure bounds are < 1
	bl = bin_left - int(bin_left)

	# Number of bins
	num_bins = int(float(max_mass+bl-min_mass)/bin_interval)+1

	# initialise masses to bin centres
	mass_list = [i * bin_interval + min_mass for i in range(num_bins)]

	# fill the bins
	intensity_matrix = []
	for scan in data.get_scan_list():
		intensity_list = [0.0] * num_bins
		masses = scan.get_mass_list()
		intensities = scan.get_intensity_list()
		for mm in range(num_bins):
			for ii in range(len(scan)):
				if mass_list[mm]-bin_left <= masses[ii] < mass_list[mm]+bin_right:
					intensity_list[mm] += intensities[ii]
		intensity_matrix.append(intensity_list)

	return IntensityMatrix(data.get_time_list(), mass_list, intensity_matrix)

