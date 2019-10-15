#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.7"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "beta"

##################################################################################
#
#	pyNormalizeIntervalLengths.py
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

import os
import sys
from optparse import *
from pyCRAC.Methods import processChromFile
	
def normalizeIntervalLength(start,end,chromosomelength,length=20):
	""" extends or trims the interval coordinates to a set length. Default = 20 bp. """
	newstart = int()
	newend	 = int()
	if start - length < 0: start = 1							# to make sure that the start is always a positive number 
	if end + length > chromosomelength: end = chromosomelength	# to make sure that interval doesn't go beyond the chromosome boundaries.
	actlength  = end - start
	difference = length - actlength
	if difference == 0:
		return start,end
	else:
		newstart = round(float(start) - float(difference)/2.0)
		if newstart < 0: newstart = 1
		newend	= round(float(end) + float(difference)/2.0)
		if newend > chromosomelength: newend = chromosomelength
		return int(newstart),int(newend)		# convert back to integers
	
def extendIntervalLength(start,end,chromosomelength,length=20):
	""" extends or the interval coordinates to a minimum length. Default = 20 bp. """
	if start - length < 0: start = 1							# to make sure that the start is always a positive number 
	if end + length > chromosomelength: end = chromosomelength	# to make sure that interval doesn't go beyond the chromosome boundaries.
	newstart = int()
	newend	 = int()
	actlength  = end - start
	difference = length - actlength
	if difference > 0:
		newstart = round(float(start) - float(difference)/2.0)
		if newstart < 0: newstart = 1
		newend = round(float(end) + float(difference)/2.0)
		return int(newstart),int(newend)		# convert back to integers
	else:
		return start,end

	return int(newstart),int(newend)			# convert back to integers
	
def addToInterval(start,end,chromosomelength,length=20):
	""" extends each interval to with a specific length. """
	start -= length
	end += length
	if start <= 0: start = 1
	if end > chromosomelength: end = chromosomelength
	return start,end
	
def addToLeft(start,end,strand,chromosomelength,length=20):
	""" adds a specific length to the 5'end of a gene """
	if strand == "+":
		start -= length
		if start <= 0: start = 1
	else:
		end += length
		if end > chromosomelength: end = chromosomelength
	return start,end
	
def addToRight(start,end,strand,chromosomelength,length=20):
	""" adds a specific length to the 5'end of a gene """
	if strand == "-":
		start -= length
		if start <= 0: start = 1
	else:
		end += length
		if end > chromosomelength: end = chromosomelength
	return start,end
		
def main():
	parser = OptionParser(usage="usage: %prog [options] -f intervaldata -c chromfile -o output_file.gtf",version="%s" % __version__)
	parser.add_option("-f", "--intervaldata", dest="intervaldata",help="Name of the bed/gff/gtf file containing the read/cDNA coordinates", metavar="mygtffile",default=None)	 
	parser.add_option("--file_type",dest="file_type",choices=["bed","gtf","gff"],help="this tool supports bed6, gtf and gff input files. Please select from 'bed','gtf' or 'gff'. Default=gtf",default="gtf")	
	parser.add_option("-o", "--outfile",dest="outfile",help="Optional. Provide the name of the output file. Default is 'selected_intervals.gtf'",metavar="outfile.gtf",default=None) 
	parser.add_option("-c", "--chromfile",dest="chromfile",help="Location of the chromosome info file. This file should have two columns: first column is the names of the chromosomes, second column is length of the chromosomes. Default is yeast",metavar="yeast.txt",default=None)
	parser.add_option("-v", "--verbose",action="store_true",help="to print status messages to a log file",default=False)
	parser.add_option("--fixed",type="int",dest="length",help="to set a fixed length for each interval in the gtf file.",metavar=20,default=0)
	parser.add_option("--min",dest="min",type="int",help="to set a minimal length for an interval. If an interval is shorter than the set minimal length it will be extended. Default = OFF.",metavar=20,default=0)
	parser.add_option("--addboth",type="int",dest="add",help="to extend the coordinates on both sides with a fixed number.",metavar=20,default=0)
	parser.add_option("--addleft",type="int",dest="left",help="to extend 5' end with a fixed number",metavar=20,default=0)
	parser.add_option("--addright",type="int",dest="right",help="to extend 3' end with a fixed number",metavar=20,default=0)
	(options, args) = parser.parse_args()
	outfile = sys.stdout
	if options.outfile:
		outfile = open(options.outfile,"w")
	chromlengthfile = open(options.chromfile,"r").readlines()
	chromdict = processChromFile(chromlengthfile)
	data  = open(options.intervaldata,"r").readlines()
	for line in data:
		if line.startswith("#"):
			outfile.write(line)
			continue
		Fld = line.strip().split("\t")
		chromosome = Fld[0]
		try:
			if options.file_type == "bed":
				strand = Fld[5]
				if options.length:
					Fld[1],Fld[2] = normalizeIntervalLength(int(Fld[1]),int(Fld[2]),chromdict[chromosome],options.length)
				elif options.min:
					Fld[1],Fld[2] = extendIntervalLength(int(Fld[1]),int(Fld[2]),chromdict[chromosome],options.min)
				elif options.add:
					Fld[1],Fld[2] = addToInterval(int(Fld[1]),int(Fld[2]),chromdict[chromosome],options.add)
				elif options.left:
					Fld[1],Fld[2] = addToLeft(int(Fld[1]),int(Fld[2]),chromdict[chromosome],options.left)
				elif options.right:
					Fld[1],Fld[2] = addToRight(int(Fld[1]),int(Fld[2]),chromdict[chromosome],options.right)
			else:
				strand = Fld[6]
				if options.length:
					Fld[3],Fld[4] = normalizeIntervalLength(int(Fld[3]),int(Fld[4]),chromdict[chromosome],options.length)
				elif options.min:
					Fld[3],Fld[4] = extendIntervalLength(int(Fld[3]),int(Fld[4]),chromdict[chromosome],options.min)
				elif options.add:
					Fld[3],Fld[4] = addToInterval(int(Fld[3]),int(Fld[4]),chromdict[chromosome],options.add)
				elif options.left:
					Fld[3],Fld[4] = addToLeft(int(Fld[3]),int(Fld[4]),chromdict[chromosome],options.left)
				elif options.right:
					Fld[3],Fld[4] = addToRight(int(Fld[3]),int(Fld[4]),chromdict[chromosome],options.right)
		except:
			sys.stderr.write("Could not process line %s\nPlease check the input file.\n" % line)
			continue
				
		outfile.write("%s\n" % "\t".join([str(i) for i in Fld]))					
	
if __name__ == "__main__":
	main()