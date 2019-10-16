"""
General I/O functions
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

import gzip
import pickle
import pathlib

import numpy

_list_types = (list, tuple, numpy.core.ndarray)


def prepare_filepath(file_name):
	"""
	Convert string filename into pathlib.Path object
		and create parent directories if required
		
	:param file_name: file_name to process
	:type file_name: str or pathlib.Path
	
	:return: file_name
	:rtype: pathlib.Path
	
	:author: Dominic Davis-Foster
	"""
	
	if not isinstance(file_name, pathlib.Path):
		file_name = pathlib.Path(file_name)
	
	if not file_name.parent.is_dir():
		file_name.parent.mkdir(parents=True)
	
	return file_name


def dump_object(obj, file_name):
	"""
	Dumps an object to a file through pickle.dump()

	:param obj: Object to be dumped
	:type obj: any
	:param file_name: Name of the file for the object dump
	:type file_name: str or pathlib.Path
	
	:author: Vladimir Likic
	:author: Dominic Davis-Foster (pathlib support)
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	file_name = prepare_filepath(file_name)
	
	with file_name.open('wb') as fp:
		pickle.dump(obj, fp)


def load_object(file_name):
	"""
	Loads an object previously dumped with dump_object()

	:param file_name: Name of the object dump file
	:type file_name: str or pathlib.Path

	:return: Object contained in the file 'file_name'
	:rtype: An instance of an arbitrary class
	
	:author: Vladimir Likic
	:author: Dominic Davis-Foster (pathlib support)
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	file_name = prepare_filepath(file_name)
	
	with file_name.open('wb') as fp:
		return pickle.load(fp)
	

def file_lines(file_name, strip=False):
	"""
	Returns lines from a file, as a list

	:param file_name: Name of a file
	:type file_name: str or pathlib.Path
	:param strip: If True, lines are pre-processed. Newline characters are
		removed, leading and trailing whitespaces are removed, and lines
		starting with '#' are discarded
	:type: bool, optional

	:return: A list of lines
	:rtype: list

	:author: Vladimir Likic
	:author: Dominic Davis-Foster (pathlib support)
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	if not isinstance(file_name, pathlib.Path):
		file_name = pathlib.Path(file_name)
	
	with file_name.open() as fp:
		lines = fp.readlines()
	
	if strip:
		# strip leading and trailing whitespaces
		lines_filtered = []
		for line in lines:
			line = line.strip()
			lines_filtered.append(line)
		
		# discard comments
		lines_to_discard = []
		for line in lines_filtered:
			# remove empty lines and comments
			if len(line) == 0 or line[0] == "#":
				lines_to_discard.append(line)
		for line in lines_to_discard:
			lines_filtered.remove(line)
		lines = lines_filtered
	
	return lines


def save_data(file_name, data, format_str="%.6f", prepend="", sep=" ", compressed=False):
	"""
	Saves a list of numbers or a list of lists of numbers
		to a file with specific formatting

	:param file_name: Name of a file
	:type file_name: str or pathlib.Path
	:param data: A list of numbers, or a list of lists
	:type: list
	:param format_str: A format string for individual entries
	:type: str
	:param prepend: A string, printed before each row
	:type: str
	:param sep: A string, printed after each number
	:type: str
	:param compressed: A boolean. If True, the output will be gzipped
	:type: bool

	:author: Vladimir Likic
	:author: Dominic Davis-Foster (pathlib support)
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	file_name = prepare_filepath(file_name)
	
	if not isinstance(data, _list_types):
		raise TypeError("'data' must be a list")
	
	if not isinstance(prepend, str):
		raise TypeError("'prepend' must be a string")
	
	if not isinstance(sep, str):
		raise TypeError("'sep' must be a string")
	
	with file_name.open("w") as fp:
		
		# decide whether data is a vector or matrix
		if isinstance(data[0], (int, float)):
			for item in data:
				if not isinstance(item, (int, float)):
					raise TypeError("not all elements of the list are numbers")
			data_is_matrix = 0
		else:
			for item in data:
				if not isinstance(item, _list_types):
					raise TypeError("not all elements of the list are lists")
			data_is_matrix = 1
		
		if data_is_matrix:
			for ii in range(len(data)):
				fp.write(prepend)
				for jj in range(len(data[ii])):
					if isinstance(data[ii][jj], (int, float)):
						fp.write(format_str % (data[ii][jj]))
						if jj<(len(data[ii]) - 1): fp.write(sep)
					else:
						raise TypeError("'datum' must be a number")
				fp.write("\n")
		else:
			for ii in range(len(data)):
				fp.write(prepend)
				fp.write(format_str % (data[ii]))
				fp.write("\n")
	
	if compressed:
		with file_name.open() as f_in:
			with gzip.open(str(file_name) + '.gz', 'wb') as f_out:
				f_out.writelines(f_in)
