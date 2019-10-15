#!/usr/bin/python

__author__ = "Sander Granneman"
__copyright__ = "Copyright 2018"
__version__ = "0.0.5"
__credits__ = ["Sander Granneman"]
__maintainer__ = "Sander Granneman"
__email__ = "sgrannem@staffmail.ed.ac.uk"
__status__ = "Production"

##################################################################################
#
#	tab2dict.py
#
#
#	Copyright (c) Sander Granneman 2018
#	
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the "Software"), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#	
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#	
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#	THE SOFTWARE.
#
##################################################################################

import sys
import time
from collections import defaultdict

class Tab2Dict():
	"""this class can be used to store the information in a fasta sequence file into a dictionary.
	The dictionary keys are the gene or chromosome names, whereas the "values" is a single string of sequence.
	When parsing a large genomic reference sequence file, you can choose to put only a handful of chromosomes into memory
	by using the id argument followed by a list of the chromosome names"""

	def __init__(self,tab_file,ids=[]):
		self.__sequence = defaultdict(str)
		id =  str()
		if hasattr(tab_file,'read'):
			tab = tab_file
		else:
			tab = open(tab_file,"r")
		for line in tab:
			Fld = line.strip("\n").split('\t')
			id	= Fld[0].split(" ")[0]
			if not ids:
				self.__sequence[id] = Fld[1]
			else:
				if id in ids: self.__sequence[id] = Fld[1]

	def __getitem__(self,chromosome):
		return self.__sequence[chromosome]

	def __iter__(self):
		return iter(self.__sequence)

	def __setitem__(self,chromosome,sequence):
		self.__sequence[chromosome] = sequence

	def __call__(self):
		for key in self.__sequence:
			sys.stdout.write("%s\t%s\n" % (key,self.__sequence[key]))
