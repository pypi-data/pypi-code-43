"""
Functions for I/O of data in JCAMP-DX format
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


import pathlib

from pyms.GCMS.Class import GCMS_data
from pyms.Spectrum import Scan
from pyms.base import pymsError


def JCAMP_reader(file_name):
	"""
	Generic reader for JCAMP DX files

	:param file_name: Path of the file to read
	:type file_name: str or pathlib.Path
	
	:return: GC-MS data object
	:rtype: class:`pyms.GCMS.Class.GCMS_data`

	:author: Qiao Wang
	:author: Andrew Isaac
	:author: Vladimir Likic
	:author: Dominic Davis-Foster (pathlib support)
	"""
	
	if not isinstance(file_name, (str, pathlib.Path)):
		raise TypeError("'file_name' must be a string or a pathlib.Path object")
	
	if not isinstance(file_name, pathlib.Path):
		file_name = pathlib.Path(file_name)
	
	print(f" -> Reading JCAMP file '{file_name}'")
	lines_list = file_name.open('r')
	data = []
	page_idx = 0
	xydata_idx = 0
	time_list = []
	scan_list = []
	
	for line in lines_list:
		if not len(line.strip()) == 0:
			prefix = line.find('#')
			# key word or information
			if prefix == 0:
				fields = line.split('=')
				if fields[0].find("##PAGE") >= 0:
					time = float(fields[2].strip())  # rt for the scan to be submitted
					time_list.append(time)
					page_idx = page_idx + 1
				elif fields[0].find("##DATA TABLE") >= 0:
					xydata_idx = xydata_idx + 1
			# data
			elif prefix == -1:
				if page_idx > 1 or xydata_idx > 1:
					if len(data) % 2 == 1:
						raise ValueError("data not in pair !")
					# TODO: what does this mean?
					mass = []
					intensity = []
					for i in range(len(data) // 2):
						mass.append(data[i * 2])
						intensity.append(data[i * 2 + 1])
					if not len(mass) == len(intensity):
						raise ValueError("len(mass) is not equal to len(intensity)")
					scan_list.append(Scan(mass, intensity))
					data = []
					data_sub = line.strip().split(',')
					for item in data_sub:
						if not len(item.strip()) == 0:
							data.append(float(item.strip()))
					if page_idx > 1:
						page_idx = 1
					if xydata_idx > 1:
						xydata_idx = 1
				else:
					data_sub = line.strip().split(',')
					for item in data_sub:
						if not len(item.strip()) == 0:
							data.append(float(item.strip()))
	
	if len(data) % 2 == 1:
		raise pymsError("data not in pair !")
	# get last scan
	mass = []
	intensity = []
	for i in range(len(data) // 2):
		mass.append(data[i * 2])
		intensity.append(data[i * 2 + 1])
	
	if not len(mass) == len(intensity):
		raise ValueError("len(mass) is not equal to len(intensity)")
	scan_list.append(Scan(mass, intensity))
	
	# sanity check
	if not len(time_list) == len(scan_list):
		raise ValueError("number of time points does not equal the number of scans")
	
	data = GCMS_data(time_list, scan_list)
	
	return data


def JCAMP_OpenChrom_reader(file_name):
	"""
	reader for JCAMP DX files produced by OpenChrom,
	produces GC-MS data object

	:author: David Kainer
	"""
	
	if not isinstance(file_name, str):
		raise TypeError("'file_name' must be a string")
	
	print(" -> Reading JCAMP file '%s'" % (file_name))
	lines_list = open(file_name, 'r')
	data = []
	page_idx = 0
	xydata_idx = 0
	time_list = []
	scan_list = []
	
	for line in lines_list:
		if not len(line.strip()) == 0:
			prefix = line.find('#')
			# key word or information
			if prefix == 0:
				fields = line.split('=')
				# print(" -> fields found: ", fields)
				if fields[0].find("##RETENTION_TIME") >= 0:
					time = float(fields[1].strip())  # rt for the scan to be submitted
					#    print(" -> RT: ", str(time))
					time_list.append(time)
					page_idx = page_idx + 1
				elif fields[0].find("##XYDATA") >= 0:
					xydata_idx = xydata_idx + 1
			# data
			elif prefix == -1:
				if page_idx > 1 or xydata_idx > 1:
					if len(data) % 2 == 1:
						raise pymsError("data not in pair !")
					mass = []
					intensity = []
					for i in range(len(data) // 2):
						mass.append(data[i * 2])
						intensity.append(data[i * 2 + 1])
					if not len(mass) == len(intensity):
						raise ValueError("len(mass) is not equal to len(intensity)")
					scan_list.append(Scan(mass, intensity))
					data = []
					data_sub = line.strip().split(',')
					for item in data_sub:
						if not len(item.strip()) == 0:
							data.append(float(item.strip()))
					if page_idx > 1:
						page_idx = 1
					if xydata_idx > 1:
						xydata_idx = 1
				else:
					data_sub = line.strip().split(',')
					for item in data_sub:
						if not len(item.strip()) == 0:
							data.append(float(item.strip()))
	
	if len(data) % 2 == 1:
		raise pymsError("data not in pair !")
	# get last scan
	mass = []
	intensity = []
	for i in range(len(data) // 2):
		mass.append(data[i * 2])
		intensity.append(data[i * 2 + 1])
	
	if not len(mass) == len(intensity):
		raise ValueError("len(mass) is not equal to len(intensity)")
	scan_list.append(Scan(mass, intensity))
	
	# sanity check
	if not len(time_list) == len(scan_list):
		raise ValueError("number of time points does not equal the number of scans")
	
	data = GCMS_data(time_list, scan_list)
	
	return data
