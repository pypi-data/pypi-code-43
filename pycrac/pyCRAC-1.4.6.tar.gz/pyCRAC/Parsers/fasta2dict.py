#!/usr/bin/python

__author__ = "Sander Granneman"
__copyright__ = "Copyright 2018"
__version__ = "0.0.4"
__credits__ = ["Sander Granneman"]
__maintainer__ = "Sander Granneman"
__email__ = "sgrannem@staffmail.ed.ac.uk"
__status__ = "Production"

##################################################################################
#
#	fasta2dict.py
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

import io
from collections import defaultdict

try:
    file_types = (file, io.IOBase)
except NameError:
    file_types = (io.IOBase,)

class Fasta2Dict():
	"""this class can be used to store the information in a fasta sequence file into a dictionary.
	The dictionary keys are the gene or chromosome names, whereas the "values" is a single string of sequence"""
	def __init__(self,fasta_file,ids=[]):
		self.__sequence = defaultdict(str)
		count = 0
		id = str()
		if type(fasta_file) == file_types:
		    fasta = fasta_file
		else:
		    fasta = open(fasta_file,"r")
		splitfasta = fasta.read().split('>')	 # This bit of code was inspired by the TAMO Fasta.py module
		for i in splitfasta[1:]:
			lines	 = i.split('\n')
			id		 = lines[0]
			sequence = ''.join(lines[1:])
			count	+= 1
			if not ids:
				self.__sequence[id] = sequence
			else:
				if id in ids: self.__sequence[id] = sequence
						
	def numberOfSeqs(self):
		return len(self.__sequence)
		
	def chromosomeLengths(self):
		for chr in sorted(self.__sequence):
			return "%s\t%s" % (chr,len(self.__sequence[chr]))
		
	def __getitem__(self,chromosome):
		return self.__sequence[chromosome]

	def __iter__(self):
		return iter(self.__sequence)

	def __setitem__(self,chromosome,sequence):
		self.__sequence[chromosome] = sequence

	def __call__(self):
		for key in self.__sequence:
			return "%s\t%s" % (key,self.__sequence[key])
