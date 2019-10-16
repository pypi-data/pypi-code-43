"""
Classes to model a Mass Spectrum and Scans
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


import deprecation
from pyms import __version__

from pyms.base import pymsCopyBase, _list_types
from pyms.Mixins import MassListMixin


class pymsSpectrumBase(pymsCopyBase, MassListMixin):
	"""
	Base class for mass spectrum or scan

	:param mass_list: mass values
	:type mass_list: list
	:param intensity_list: intensity values
	:type intensity_list: list

	:author: Andrew Isaac
	:author: Qiao Wang
	:author: Vladimir Likic
	:author: Dominic Davis-Foster (type assertions and properties)
	"""
	
	def __init__(self, mass_list, intensity_list):
		"""
		Initialise the class

		:author: Andrew Isaac
		:author: Qiao Wang
		:author: Vladimir Likic
		"""
		
		if not isinstance(mass_list, _list_types) or \
				not isinstance(mass_list[0], (int, float)):
			raise TypeError("'mass_list' must be a list of numbers")
		if not isinstance(intensity_list, _list_types) or \
				not isinstance(intensity_list[0], (int, float)):
			raise TypeError("'intensity_list' must be a list of numbers")
		if not len(mass_list) == len(intensity_list):
			raise ValueError("'mass_list' is not the same size as 'intensity_list'")
		
		self._mass_list = mass_list
		self._intensity_list = intensity_list
		self._min_mass = min(mass_list)
		self._max_mass = max(mass_list)
	
	def __len__(self):
		"""
		Returns the length of the object

		:return: Length of object
		:rtype: int

		:author: Andrew Isaac
		:author: Qiao Wang
		:author: Vladimir Likic
		"""
		
		return len(self._mass_list)
	
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self._intensity_list == other.intensity_list \
				   and self._mass_list == other.mass_list
		return NotImplemented
	
	def __copy__(self):
		return self.__class__(self._mass_list[:], self._intensity_list[:])
	
	@property
	def intensity_list(self):
		"""
		Returns a copy of the intensity list

		:return: the intensities
		:rtype: list

		:author: Qiao Wang
		:author: Andrew Isaac
		:author: Vladimir Likic
		"""
		
		return self._intensity_list[:]
	
	@property
	def mass_spec(self):
		"""
		Returns the intensity list

		:return: the intensities
		:rtype: list

		:author: Qiao Wang
		:author: Andrew Isaac
		:author: Vladimir Likic
		"""
		
		return self._intensity_list


class MassSpectrum(pymsSpectrumBase):
	"""
	Models a binned mass spectrum

	:param mass_list: mass values
	:type mass_list: list
	:param intensity_list: intensity values
	:type intensity_list: list

	:author: Andrew Isaac
	:author: Qiao Wang
	:author: Vladimir Likic
	:author: Dominic Davis-Foster (type assertions and properties)
	"""
	
	@pymsSpectrumBase.intensity_list.setter
	def intensity_list(self, value):
		"""
		Set the intensity values for the spectrum
		
		:param value: list of intensity value for each mass in `mass_list`
		:type value: list
		"""
		
		if not isinstance(value, _list_types) or not isinstance(value[0], (int, float)):
			raise TypeError("'intensity_list' must be a list of numbers")
		
#		if not len(self.mass_list) == len(value):
#			raise ValueError("'mass_list' and 'intensity_list' are not the same size")
		
		self._intensity_list = value
		
	@pymsSpectrumBase.mass_spec.setter
	def mass_spec(self, value):
		"""
		Set the intensity values for the spectrum

		:param value: list of intensity value for each mass in `mass_list`
		:type value: list
		"""
		
		if not isinstance(value, _list_types) or not isinstance(value[0], (int, float)):
			raise TypeError("'intensity_list' must be a list of numbers")
		
#		if not len(self.mass_list) == len(value):
#			raise ValueError("'mass_list' and 'intensity_list' are not the same size")
		
		self._intensity_list = value
		
	@MassListMixin.mass_list.setter
	def mass_list(self, value):
		"""
		Set the mass values for the spectrum

		:param value: list of mass values for the spectrum
		:type value: list
		"""
		
		if not isinstance(value, _list_types) or not isinstance(value[0], (int, float)):
			raise TypeError("'mass_list' must be a list of numbers")
		
#		if not len(self.mass_list) == len(value):
#			raise ValueError("'mass_list' and 'intensity_list' are not the same size")
		
		self._mass_list = value


class Scan(pymsSpectrumBase):
	"""
	Generic object for a single Scan's raw data

	:param mass_list: mass values
	:type mass_list: list
	:param intensity_list: intensity values
	:type intensity_list: list

	:author: Andrew Isaac
	:author: Qiao Wang
	:author: Vladimir Likic
	:author: Dominic Davis-Foster (type assertions and properties)
	"""
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Scan.intensity_list' instead")
	def get_intensity_list(self):
		"""
		Returns the intensities for the current scan

		:return: the intensities
		:rtype: list

		:author: Qiao Wang
		:author: Andrew Isaac
		:author: Vladimir Likic
		"""
		
		return self.intensity_list
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Scan.min_mass' instead")
	def get_min_mass(self):
		"""
		Returns the minimum m/z value in the scan

		:return: Minimum m/z
		:rtype: Float

		:author: Andrew Isaac
		"""
		
		return self.min_mass
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Scan.max_mass' instead")
	def get_max_mass(self):
		"""
		Returns the maximum m/z value in the scan

		:return: Maximum m/z
		:rtype: Float

		:author: Andrew Isaac
		"""
		
		return self.max_mass


