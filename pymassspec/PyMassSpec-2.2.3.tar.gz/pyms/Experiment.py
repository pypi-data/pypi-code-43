"""
Models a GC-MS experiment represented by a list of signal peaks
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


import os
import copy
import pickle
import pathlib

import deprecation

from pyms import __version__
from pyms.base import pymsBaseClass
from pyms.Peak.List.Function import is_peak_list, sele_peaks_by_rt
from pyms.Utils.IO import prepare_filepath


class Experiment(pymsBaseClass):
	"""
	Models an experiment object

	:param expr_code: Unique identifier for the experiment
	:type expr_code: str
	:param peak_list: A list of peak objects
	:type peak_list: list of class:`pyms.Peak.Peak`

	:author: Vladimir Likic
	:author: Andrew Isaac
	:author: Dominic Davis-Foster (type assertions, properties and pathlib support)
	"""
	
	def __init__(self, expr_code, peak_list):
		"""
		Models an experiment
		"""
		
		if not isinstance(expr_code, str):
			raise TypeError("'expr_code' must be a string")
		if not is_peak_list(peak_list):
			raise TypeError("'peak_list' must be a list of Peak objects")
		
		self.__expr_code = expr_code
		self.__peak_list = peak_list
	
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.peak_list == other.peak_list \
				   and self.expr_code == other.expr_code
		
		return NotImplemented
	
	def __len__(self):
		return len(self.peak_list)
	
	def __copy__(self):
		return Experiment(copy.copy(self.__expr_code), copy.copy(self.peak_list))
	
	def __deepcopy__(self, memodict={}):
		return self.__copy__()
	
	@property
	def expr_code(self):
		"""
		Returns the expr_code of the experiment

		:return: The expr_code of the experiment
		:rtype: str
		"""
		
		return self.__expr_code

	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Experiment.expr_code' instead")
	def get_expr_code(self):
		"""
		Returns the expr_code of the experiment
		
		.. deprecated:: 2.1.2
			Use :attr:`pyms.Experiment.Experiment.expr_code` instead.

		:return: The expr_code of the experiment
		:rtype: str
		"""
		return self.expr_code
		
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Experiment.peak_list' instead")
	def get_peak_list(self):
		"""
		Returns the peak list

		.. deprecated:: 2.1.2
			Use :attr:`pyms.Experiment.Experiment.peak_list` instead.

		:return: A list of peak objects
		:rtype: list
		"""
		
		return self.peak_list
	
	@property
	def peak_list(self):
		"""
		Returns the peak list

		:return: A list of peak objects
		:rtype: list
		"""
		
		return self.__peak_list
	
	def sele_rt_range(self, rt_range):
		"""
		Discards all peaks which have the retention time outside the specified range

		:param rt_range: Min, max retention time given as a list [rt_min,rt_max]
		:type rt_range: list
		"""
		
		if not isinstance(rt_range, list):
			raise TypeError("'rt_range' must be a list")
		
		peaks_sele = sele_peaks_by_rt(self.__peak_list, rt_range)
		self.__peak_list = peaks_sele
	
	@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
							current_version=__version__,
							details="Use 'Experiment.dump' instead")
	def store(self, file_name):
		"""
		stores an experiment to a file
	
		.. deprecated:: 2.1.2
			Use :attr:`pyms.Experiment.Experiment.dump` instead.
	
		:param file_name: The name of the file
		:type file_name: str or pathlib.Path
	
		:author: Vladimir Likic
		:author: Andrew Isaac
		:author: Dominic Davis-Foster (pathlib support)
		"""
		
		if not isinstance(file_name, (str, pathlib.Path)):
			raise TypeError("'file_name' must be a string or a pathlib.Path object")
		
		file_name = prepare_filepath(file_name)
		
		fp = file_name.open('wb')
		pickle.dump(self, fp, 1)
		fp.close()


def read_expr_list(file_name):
	"""
	Reads the set of experiment files and returns a list of class:`pyms.Experiment.Experiment` objects

	:param file_name: The name of the file which lists experiment dump file names, one file per line
	:type file_name: str or pathlib.Path

	:return: A list of Experiment instances
	:rtype: list of class:`pyms.Experiment.Experiment`

	:author: Vladimir Likic
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	if not isinstance(file_name, pathlib.Path):
		file_name = pathlib.Path(file_name)

	fp = file_name.open()
	
	exprfiles = fp.readlines()
	fp.close()
	
	exprl = []
	
	for exprfile in exprfiles:
		
		exprfile = exprfile.strip()
		expr = load_expr(exprfile)
		
		exprl.append(expr)
	
	return exprl


def load_expr(file_name):
	"""
	Loads an experiment saved with 'store_expr'

	:param file_name: Experiment file name
	:type file_name: str or pathlib.Path
	
	:return: The loaded experiment
	:rtype: class:`pyms.Experiment.Experiment`

	:author: Vladimir Likic
	:author: Andrew Isaac
	:author: Dominic Davis-Foster (type assertions and pathlib support)
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	if not isinstance(file_name, pathlib.Path):
		file_name = pathlib.Path(file_name)
	
	fp = file_name.open('rb')
	expr = pickle.load(fp)
	fp.close()
	
	if not isinstance(expr, Experiment):
		raise IOError("The loaded file is not an experiment file")
	
	return expr


@deprecation.deprecated(deprecated_in="2.1.2", removed_in="2.2.0",
						current_version=__version__,
						details="Use 'Experiment.store()' instead")
def store_expr(file_name, expr):
	"""
	Stores an experiment to a file

	.. deprecated:: 2.1.2
		Use :meth:`pyms.Experiment.Experiment.store` instead.

	:param file_name: The name of the file
	:type file_name: str
	:param expr: An experiment object
	:type expr: class:`pyms.Experiment.Experiment`

	:author: Vladimir Likic
	:author: Andrew Isaac
	:author: Dominic Davis-Foster (type assertions)
	"""
	
	if not isinstance(expr, Experiment):
		raise TypeError("'expr' must be an Experiment object")
	
	if not isinstance(file_name, str):
		raise TypeError("'file_name' must be a string")
	
	if not os.path.exists(os.path.dirname(file_name)):
		os.makedirs(os.path.dirname(file_name))
	
	fp = open(file_name,'wb')
	pickle.dump(expr, fp, 1)
	fp.close()
