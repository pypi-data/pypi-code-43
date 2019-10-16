"""
Provides a class to model signal peak
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
from warnings import warn

import deprecation

from pyms import __version__
from pyms.base import pymsBaseClass
from pyms.IntensityMatrix import IntensityMatrix
from pyms.Spectrum import MassSpectrum
from pyms.base import _list_types


class Peak(pymsBaseClass):
	"""
	Models a signal peak

		A signal peak object
		A peak object is initialised with retention time and
		Either an ion mass, a mass spectrum or None

	:param rt: Retention time
	:type rt: int or float
	:param ms: A ion mass, or spectra of maximising ions
	:type ms: int or float or class`pyms.MassSpectrum.MassSpectrum`, optional
	:param minutes: Retention time units flag. If True, retention time
		is in minutes; if False retention time is in seconds
	:type minutes: bool, optional
	:param outlier: Whether the peak is an outlier
	:type outlier: bool, optional

	:author: Vladimir Likic
	:author: Andrew Isaac
	:author: Dominic Davis-Foster (type assertions and properties)
	:author: David Kainer (outlier flag)
	"""
	
	def __init__(self, rt=0.0, ms=None, minutes=False, outlier=False):
		"""
		Models a signal peak
		"""
		
		if not isinstance(rt, (int, float)):
			raise TypeError("'rt' must be a number")
		
		if ms and not isinstance(ms, MassSpectrum) and not isinstance(ms, (int, float)):
			raise TypeError("'ms' must be a number or a MassSpectrum object")
		
		if minutes:
			rt = rt*60.0
		
		# basic peak attributes
		self.is_outlier = outlier
		self.__rt = float(rt)
		self.__pt_bounds = None
		self.__area = None
		self.__ion_areas = {}
		
		# these two attributes are required for
		# setting the peak mass spectrum
		if isinstance(ms, MassSpectrum):
			# mass spectrum
			self.__mass_spectrum = ms
			self.__ic_mass = None
		else:
			# single ion chromatogram properties
			self.__mass_spectrum = None
			self.__ic_mass = ms
		
		self.make_UID()
	
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.UID == other.UID \
				   and self.bounds == other.bounds \
				   and self.rt == other.rt \
				   and self.mass_spectrum == other.mass_spectrum \
				   and self.area == other.area
		
		return NotImplemented
	
	"""def __copy__(self):
		#return pickle.loads(pickle.dumps(self))
		
		if self.__mass_spectrum is None:
			peak = Peak(rt=copy.copy(self.__rt),
						ms=copy.copy(self.__ic_mass),
						minutes=self.__minutes,
						outlier=self.is_outlier)
		else:
			peak = Peak(rt=copy.copy(self.__rt),
						ms=copy.copy(self.__mass_spectrum),
						minutes=self.__minutes,
						outlier=self.is_outlier)
		if self.__area is not None:
			peak.area = self.area
		if self.__pt_bounds is not None:
			peak.bounds = copy.copy(self.bounds)
		if self.__ic_mass is not None:
			peak.ic_mass = 0+self.ic_mass
		
		return peak
		
	def __deepcopy__(self, memodict={}):
		return self.__copy__()"""
	
	@property
	def area(self):
		"""
		Gets the area under the peak

		:return: The peak area
		:rtype: float

		:author: Andrew Isaac
		"""
		
		return self.__area
	
	@area.setter
	def area(self, value):
		"""
		Sets the area under the peak

		:param value: The peak area
		:type value: float

		:author: Andrew Isaac
		"""
		
		if not isinstance(value, (int, float)):
			raise TypeError("'Peak.area' must be a positive number")
		elif value <= 0:
			raise ValueError("'Peak.area' must be a positive number")
		
		self.__area = value
	
	@property
	def bounds(self):
		"""
		Gets peak boundaries in points

		:return: A list containing left, apex, and right
			peak boundaries in points, left and right are offsets
		:rtype: list

		:author: Andrew Isaac
		"""
		
		return self.__pt_bounds
	
	@bounds.setter
	def bounds(self, value):
		"""
		Sets peak boundaries in points

		:param value: A list containing left, apex, and right
			peak boundaries in points, left and right are offsets
		:type value: list
		"""
		
		if not isinstance(value, _list_types):
			raise TypeError("'Peak.bounds' must be a list")
		
		if len(value) != 3:
			raise ValueError("'Peak.bounds' must have exactly 3 elements")

		for index, item in enumerate(value):
			if not isinstance(item, int):
				raise TypeError(f"'Peak.bounds' element #{index} must be an integer")
		
		self.__pt_bounds = value
	
	def crop_mass(self, mass_min, mass_max):
		"""
		Crops mass spectrum

		:param mass_min: Minimum mass value
		:type mass_min: int or float
		:param mass_max: Maximum mass value
		:type mass_max: int or float

		:author: Andrew Isaac
		"""
		
		if not isinstance(mass_min, (float, int)) or not isinstance(mass_max, (float, int)):
			raise TypeError("'mass_min' and 'mass_max' must be numbers")
		if mass_min >= mass_max:
			raise ValueError("'mass_min' must be less than 'mass_max'")
		
		mass_list = self.__mass_spectrum.mass_list
		
		if mass_min < min(mass_list):
			raise ValueError("'mass_min' is less than the smallest mass: %d" % min(mass_list))
		if mass_max > max(mass_list):
			raise ValueError("'mass_max' is greater than the largest mass: %d" % max(mass_list))
		
		# pre build mass_list and list of indecies
		new_mass_list = []
		new_mass_spec = []
		mass_spec = self.__mass_spectrum.mass_spec
		for ii in range(len(mass_list)):
			mass = mass_list[ii]
			if mass_min <= mass <= mass_max:
				new_mass_list.append(mass)
				new_mass_spec.append(mass_spec[ii])
		
		self.__mass_spectrum.mass_list = new_mass_list
		self.__mass_spectrum.mass_spec = new_mass_spec
		
		if len(new_mass_list) == 0:
			raise ValueError("mass spectrum is now empty")
		elif len(new_mass_list) < 10:
			warn("peak mass spectrum contains < 10 points", Warning)
		
		# update UID
		self.make_UID()

	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.area' instead")
	def get_area(self):
		"""
		Gets the area under the peak

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.area` instead.

		:return: The peak area
		:rtype: float

		:author: Andrew Isaac
		"""
		
		return self.area
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.ic_mass' instead")
	def get_ic_mass(self):
		"""
		Gets the mass for a single ion chromatogram peak

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.ic_mass` instead.

		:return: The mass of the single ion chromatogram that the peak is from
		:rtype: float or int
		"""
		
		return self.ic_mass
	
	def get_int_of_ion(self, ion):
		"""
		returns the intensity of a given ion

		:param ion: The m/z value of the ion of interest
		:type ion: int

		:return: The intensity of the given ion in this peak
		:rtype: int
		"""
		
		try:
			index = self.__mass_spectrum.mass_list.index(ion)
			return self.__mass_spectrum.mass_spec[index]
		except (ValueError, IndexError):
			raise IndexError(f"'ion' out of range of mass spectrum (range {min(self.__mass_spectrum.mass_list)} to {max(self.__mass_spectrum.mass_list)})")
	
	def get_ion_area(self, ion):
		"""
		gets the area of a single ion chromatogram under the peak

		:param ion: The ion whose IC is to be returned
		:type ion: int

		:return: The area of the ion under this peak
		:rtype: float
		"""
		
		try:
			return self.__ion_areas[ion]
		except KeyError:
			return None
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.ion_areas' instead")
	def get_ion_areas(self):
		"""
		returns a copy of the ion areas dict

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.ion_areas` instead.

		:return: The dictionary of ion:ion area pairs
		:rtype: dict
		"""
		
		return self.ion_areas
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.mass_spectrum' instead")
	def get_mass_spectrum(self):
		"""
		Gets the mass spectrum at the apex of the peak

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.mass_spectrum` instead.

		:return: The mass spectrum at the apex of the peak
		:rtype: class:`pyms.MassSpectrum.MassSpectrum`
		"""
		
		return self.mass_spectrum
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.bounds' instead")
	def get_pt_bounds(self):
		"""
		Gets peak boundaries in points

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.bounds` instead.

		:return: A list containing left, apex, and right
			peak boundaries in points, left and right are offsets
		:rtype: list

		:author: Andrew Isaac
		"""
		
		return self.bounds
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.rt' instead")
	def get_rt(self):
		"""
		Return the retention time

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.rt` instead.

		:return: Retention time
		:rtype: float
		"""
		
		return self.rt
	
	def get_third_highest_mz(self):
		"""
		returns the mz value with the third highest intensity

		:return: the ion with the third highest intensity
		:rtype: int
		"""
		
		if self.__mass_spectrum is not None:
			mass_list = self.__mass_spectrum.mass_list
			mass_spec = self.__mass_spectrum.mass_spec
			# find top two masses
			best = 0
			best_ii = 0
			best2_ii = 0
			best3_ii = 0
			for ii in range(len(mass_spec)):
				if mass_spec[ii] > best:
					best = mass_spec[ii]
					best3_ii = best2_ii
					best2_ii = best_ii
					best_ii = ii
			
			return int(mass_list[best3_ii])
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.UID' instead")
	def get_UID(self):
		"""
		Return the unique peak ID (UID) based on:
			Int masses of top two intensities and their ratio (as
			Mass1-Mass2-Ratio*100); or the single mass as int.

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.UID` instead.

		:return: UID string
		:rtype: str

		:author: Andrew Isaac
		"""
		
		return self.UID
	
	@property
	def ic_mass(self):
		"""
		Gets the mass for a single ion chromatogram peak

		:return: The mass of the single ion chromatogram that the peak is from
		:rtype: float or int
		"""
		
		return self.__ic_mass
	
	@ic_mass.setter
	def ic_mass(self, value):
		"""
		Sets the mass for a single ion chromatogram peak
			Clears the mass spectrum

		:param value: The mass of the ion chromatogram that the peak is from
		:type value: float
		"""
		
		if not isinstance(value, (int, float)):
			raise TypeError("'Peak.ic_mass' must be a number")
		self.__ic_mass = value
		# clear mass spectrum
		self.__mass_spectrum = None
		self.make_UID()
	
	@property
	def ion_areas(self):
		"""
		Returns a copy of the ion areas dict

		:return: The dictionary of ion:ion area pairs
		:rtype: dict
		"""
		if len(self.__ion_areas) == 0:
			raise ValueError("no ion areas set")
		
		return copy.deepcopy(self.__ion_areas)
	
	@ion_areas.setter
	def ion_areas(self, value):
		"""
		Set the ion:ion area pair dictionary

		:param value: The dictionary of ion:ion_area pairs
		:type value: dict
		"""
		
		if not isinstance(value, dict) or not isinstance(list(value.keys())[0], int):
			raise TypeError("'Peak.ion_areas' must be a dictionary of ion:ion_area pairs")
		self.__ion_areas = value
	
	def make_UID(self):
		"""
		Create a unique peak ID (UID) based on:
			Int masses of top two intensities, their ratio and RT (as
			Mass1-Mass2-Ratio*100-RT); or the single mass as int and RT.

		:author: Andrew Isaac
		"""
		
		if self.__mass_spectrum is not None:
			mass_list = self.__mass_spectrum.mass_list
			mass_spec = self.__mass_spectrum.mass_spec
			# find top two masses
			best = 0
			best_ii = 0
			best2_ii = 0
			for ii in range(len(mass_spec)):
				if mass_spec[ii] > best:
					best = mass_spec[ii]
					best2_ii = best_ii
					best_ii = ii
			ratio = int(100*mass_spec[best2_ii]/best)
			self.__UID = f"{int(mass_list[best_ii]):d}-{int(mass_list[best2_ii]):d}-{ratio:d}-{self.__rt:.2f}"
		elif self.__ic_mass is not None:
			self.__UID = f"{int(self.__ic_mass):d}-{self.__rt:.2f}"
		else:
			self.__UID = f"{self.__rt:.2f}"
	
	@property
	def mass_spectrum(self):
		"""
		Gets the mass spectrum at the apex of the peak

		:return: The mass spectrum at the apex of the peak
		:rtype: class:`pyms.MassSpectrum.MassSpectrum`
		"""
		
		return copy.copy(self.__mass_spectrum)
	
	@mass_spectrum.setter
	def mass_spectrum(self, value):
		"""
		Sets the mass spectrum
			Clears the mass for a single ion chromatogram peak

		:param value: The mass spectrum at the apex of the peak
		:rtype: class:`pyms.MassSpectrum.MassSpectrum`
		"""
		
		if not isinstance(value, MassSpectrum):
			raise TypeError("'Peak.mass_spectrum' must be a MassSpectrum object")
		
		self.__mass_spectrum = value
		# clear ion mass
		self.__ic_mass = None
		self.make_UID()
	
	def null_mass(self, mass):
		"""
		Ignore given mass in spectra

		:param mass: Mass value to remove
		:type mass: int or float

		:author: Andrew Isaac
		"""
		
		if self.__mass_spectrum is None:
			raise NameError("mass spectrum not set for this peak")
		
		if not isinstance(mass, (int, float)):
			raise TypeError("'mass' must be a number")
		
		mass_list = self.__mass_spectrum.mass_list
		
		if mass < min(mass_list) or mass > max(mass_list):
			raise IndexError("'mass' not in mass range:", min(mass_list), "to", max(mass_list))
		
		best = max(mass_list)
		ix = 0
		for ii in range(len(mass_list)):
			tmp = abs(mass_list[ii] - mass)
			if tmp < best:
				best = tmp
				ix = ii
		
		self.__mass_spectrum.mass_spec[ix] = 0
		
		# update UID
		self.make_UID()
	
	@property
	def rt(self):
		"""
		Return the retention time

		:return: Retention time
		:rtype: float
		"""
		
		return self.__rt
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.area' instead")
	def set_area(self, area):
		"""
		Sets the area under the peak

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.area` instead.

		:param area: The peak area
		:type area: float

		:author: Andrew Isaac
		"""
		
		if not isinstance(area, (int, float)):
			raise TypeError("'area' must be a positive number")
		elif area <= 0:
			raise ValueError("'area' must be a positive number")
		
		self.__area = area
	
	def set_bounds(self, left, apex, right):
		"""
		Sets peak boundaries in points

		:param left: Left peak boundary, in points offset from apex
		:param apex: Apex of the peak, in points
		:param right: Right peak boundary, in points offset from apex
		"""
		
		self.bounds = (left, apex, right)
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.ic_mass' instead")
	def set_ic_mass(self, mz):
		"""
		Sets the mass for a single ion chromatogram peak
			Clears the mass spectrum

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.ic_mass` instead.

		:param mz: The mass of the ion chromatogram that the peak is from
		:type mz: float
		"""
		
		if not isinstance(mz, (float, int)):
			raise TypeError("'mz' must be a number")
		self.__ic_mass = mz
		# clear mass spectrum
		self.__mass_spectrum = None
		self.make_UID()
	
	def set_ion_area(self, ion, area):
		"""
		sets the area for a single ion

		:param ion: the ion whose area is being entered
		:type ion: int
		:param area: the area under the IC of ion
		:type area: int or float

		:author: Sean O'Callaghan
		"""

		if not isinstance(ion, int):
			raise TypeError("'ion' must be an integer")
		
		if not isinstance(area, (int, float)):
			raise TypeError("'area' must be a number")
		
		self.__ion_areas[ion] = area
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.ion_areas' instead")
	def set_ion_areas(self, ion_areas):
		"""
		set the ion:ion area pair dictionary

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.ion_areas` instead.

		:param ion_areas: The dictionary of ion:ion_area pairs
		:type ion_areas: dict
		"""
		
		self.ion_areas = ion_areas
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.mass_spectrum' instead")
	def set_mass_spectrum(self, ms):
		"""
		Sets the mass spectrum
			Clears the mass for a single ion chromatogram peak

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.mass_spectrum` instead.

		:param ms: The mass spectrum at the apex of the peak
		:type ms: class:`pyms.MassSpectrum.MassSpectrum`
		"""
		
		if not isinstance(ms, MassSpectrum):
			raise TypeError("'ms' must be a MassSpectrum object")
		
		self.__mass_spectrum = ms
		# clear ion mass
		self.__ic_mass = None
		self.make_UID()
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Peak.bounds' instead")
	def set_pt_bounds(self, pt_bounds):
		"""
		Sets peak boundaries in points

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Peak.Peak.bounds` instead.

		:param pt_bounds: A list containing left, apex, and right
			peak boundaries in points, left and right are offsets
		:type pt_bounds: list
		"""
		
		self.bounds = pt_bounds
	
	@property
	def UID(self):
		"""
		Return the unique peak ID (UID) based on:
			Int masses of top two intensities and their ratio (as
			Mass1-Mass2-Ratio*100); or the single mass as int.

		:return: UID string
		:rtype: str

		:author: Andrew Isaac
		"""
		
		return self.__UID
		
	## TODO: What is this?
	def find_mass_spectrum(self, data, from_bounds=False):
		
		"""
		Sets peak mass spectrum from the data
			Clears the single ion chromatogram mass

		:param data: An IntensityMatrix object
		:type data: class:`pyms.GCMS.IntensityMatrix`
		:param from_bounds: Indicator whether to use the attribute
			'pt_bounds' or to find the peak apex from the peak
			retention time
		:type from_bounds: bool
		"""
		
		if not isinstance(data, IntensityMatrix):
			raise TypeError("'data' must be an IntensityMatrix")
		
		if from_bounds:
			if self.__pt_bounds is None:
				raise NameError("pt_bounds not set for this peak")
			else:
				pt_apex = self.__pt_bounds[1]
		else:
			# get the index of peak apex from peak retention time
			pt_apex = data.get_index_at_time(self.__rt)
		
		# set the mass spectrum
		self.__mass_spectrum = data.get_ms_at_index(pt_apex)
		
		# clear single ion chromatogram mass
		self.__ic_mass = None
		self.make_UID()

	def top_ions(self, num_ions=5):
		"""
		Computes the highest #num_ions intensity ions
	
		:param num_ions: The number of ions to be recorded
		:type num_ions: int
	
		:return: A list of the #num_ions highest intensity ions, default 5
		:rtype: list, optional
	
		:author: Sean O'Callaghan
		:author: Dominic Davis-Foster (type assertions)
		"""
		
		if not isinstance(num_ions, int):
			raise TypeError("'n_top_ions' must be an integer")
	
		intensity_list = self.mass_spectrum.mass_spec
		mass_list = self.mass_spectrum.mass_list
	
		ic_tuple = zip(intensity_list, mass_list)
	
		sorted_ic = sorted(ic_tuple)
		top_ic = sorted_ic[-num_ions:]
	
		top_ions = []
	
		for entry in top_ic:
			top_ions.append(entry[1])
			
		return top_ions
