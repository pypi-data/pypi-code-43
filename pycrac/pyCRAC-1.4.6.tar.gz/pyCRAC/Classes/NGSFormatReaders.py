#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.3"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyCRAC NGSFormatReaders.py
#
#
#	Copyright (c) Sander Granneman 2019
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
import six

def splitter(line):
	""" This function splits the line at double quotes and returns the second object in the array"""
	line = line.replace('\"',"")
	return line.split()[1]
	

class NGSFileReader():
	""" Converts transposed numpy arrays in to various NGS output formats """
	def __init__(self,infile):
		self.file_types = ["gtf","gff","bed","bedgraph","sgr"]
		self.file_type	= str()
		if not hasattr(infile,'read'):		    # if the infile is simply a file name
			self.file = open(infile,"r")
		elif hasattr(infile,'__iter__'):   
			self.file = infile			    # if it is a file object, standard input or a generator
		else:
			raise TypeError("\nCould not determine the file type\n")
		self.chromosome = str()
		self.strand		= str()
		self.start		= int()
		self.end		= int()
		self.source		= "exon"
		self.name		= str()
		self.feature	= "interval"
		self.attributes = str()
		self.comments	= str()
		self.coverage	= int()
		self.frame		= int()
		self.comments	= list()
		self.gene_name	= str()
		self.gene_id	= str()
		self.line		= str()
		self.transcript_name = str()
		self.transcript_id	 = str()
	
	def fileComments(self):
		return "".join(self.comments)

	def resetVariables(self):
		""" resets all the class variables. Important before reading a new line """
		self.chromosome = str()
		self.strand		= str()
		self.start		= int()
		self.end		= int()
		self.source		= "exon"
		self.name		= str()
		self.feature	= "interval"
		self.attributes = str()
		self.comments	= str()
		self.coverage	= int()
		self.frame		= int()
		self.comments	= list()
		self.gene_name	= str()
		self.gene_id	= str()
		self.line		= str()
		self.transcript_name = str()
		self.transcript_id	 = str()
		
	def __retrieveAndSplitLine(self):
		""" splits any line that is tab-delimited into columns """
		self.resetVariables()
		while True:
			try:
				self.line = six.next(self.file)
			except StopIteration:
				self.file.close()
				return False
			if self.line.startswith("track"):
				self.comments.append(self.line)
				continue
			if self.line.startswith("#"):
				self.comments.append(self.line)
				continue
			else:
				return self.line.strip().split("\t")
					
	def readBedgraphLine(self):
		""" processes a line from a bedgraph file. Start positions are converted to 0-based coordinates! """
		Fld = self.__retrieveAndSplitLine()
		try:
			if Fld:
				self.chromosome = Fld[0]
				self.start		= int(Fld[1])-1
				self.end		= int(Fld[2])
				self.coverage	= Fld[4]
				return True
			else:
				return False
		except IndexError:
			sys.stderr.write("IndexError. Are you sure you selected the correct file format?\n")
			return False
					
	def readBedLine(self):
		""" processes a line from a bed file (first six columns only)"""
		Fld = self.__retrieveAndSplitLine()
		try:
			if Fld:
				self.chromosome = Fld[0]
				self.start		= int(Fld[1])
				self.end		= int(Fld[2])
				self.name		= Fld[3]
				self.score		= Fld[4]
				self.strand		= Fld[5]
				return True
			else:
				return False
		except IndexError:
			sys.stderr.write("IndexError. Are you sure you selected the correct file format?\n")
			return False
			
	def readSgrLine(self):
		""" processes a line from an sgr file. Start positions are converted to 0-based coordinates! """
		Fld = self.__retrieveAndSplitLine()
		try:
			if Fld:
				self.chromosome = Fld[0]
				self.start		= int(Fld[1])-1
				try:
					self.coverage = int(Fld[2])
				except ValueError:
					self.coverage = float(Fld[2])
				return True
			else:
				return False
		except IndexError:
			sys.stderr.write("IndexError. Are you sure you selected the correct file format?\n")
			return False

	def readGTFLine(self):	
		""" processes a line from a GTF file. Start positions are converted to 0-based coordinates! """
		Fld = self.__retrieveAndSplitLine()
		try:
			if Fld:
				self.chromosome = Fld[0]
				self.source		= Fld[1]
				self.feature	= Fld[2]
				self.start		= int(Fld[3])-1
				self.end		= int(Fld[4])
				self.score		= Fld[5]
				self.strand		= Fld[6]
				self.frame		= Fld[7]
				if len(Fld) > 8:
					self.attributes = Fld[8].strip()
					self.__processAttributes(format="gtf")
				return True
			else:
				return False
		except IndexError:
			sys.stderr.write("IndexError. Are you sure you selected the correct file format?\n")
			return False
					
	def readGFFLine(self):
		""" processes a line from a GFF3 file. Start positions are converted to 0-based coordinates! """
		Fld = self.__retrieveAndSplitLine()
		try:
			if Fld:
				self.chromosome = Fld[0]
				self.source		= Fld[1]
				self.feature	= Fld[2]
				self.start		= int(Fld[3])-1
				self.end		= int(Fld[4])
				self.score		= Fld[5]
				self.strand		= Fld[6]
				self.frame		= Fld[7]
				if len(Fld) > 8:
					self.attributes = Fld[8]
					self.__processAttributes(format="gff")
					self.comments	= self.attributes.split("#")[-1]
				return True
			else:
				return False
		except IndexError:
			sys.stderr.write("Warning! IndexError. Are you sure you selected the correct file format?\n")
	
	def __processAttributes(self,format="gtf"):
		"""takes the attributes from column 9 in the GTF or GFF file and extracts gene_name,transcript_name, etc information"""
		info			= self.attributes.split(";")
		gene_id			= str()
		transcript_id	= str()
		gene_name		= str()
		transcript_name = str()
		if format == "gtf":
			for i in info:
				i = i.strip()
				if i.startswith('gene_id'):						# gtf file format
					self.gene_id = splitter(i)		
				elif i.startswith('transcript_id'):
					self.transcript_id = splitter(i)
				elif i.startswith('gene_name'):
					self.gene_name = splitter(i)
				elif i.startswith('transcript_name'):
					self.transcript_name = splitter(i)
				
		elif format == "gff":
			for i in info:
				if i.startswith('Name='):						# gff file format
					self.gene_name = i.split("=")[1]
					self.transcript_name = self.gene_name
				elif i.startswith('ID='):
					self.gene_id = i.split("=")[1]
					self.transcript_id = self.gene_id
