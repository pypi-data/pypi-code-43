#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.4"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyGetGTFSources.py
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
import time
from collections import defaultdict
from optparse import *

def getGTFSourceList(file_object):
	"""Looks at the second column in the GTF file and stores the information in a set list,
	hence, only unique annotations/features are stored. These will be printed to the standard output"""
	sourcelist = set()
	count	   = defaultdict(int)
	for line in file_object:
		if line[0] is not "#":
			try:
				Fld = line.strip("\n").split("\t")
				sourcelist.add(Fld[1])
				count[Fld[1]] += 1
			except IndexError:
				sys.stderr.write("IndexError at line:\n%s" % (line))
		else:
			continue
	sortedsourcelist = list()
	sortedsourcelist.extend(sourcelist)
	return sortedsourcelist,count

def main():
	parser = OptionParser(usage="usage: %prog [options] --gtf=myfavgtf --count", version="%s" % __version__)
	parser.add_option("--gtf",dest="gtf_file",metavar="Yourfavoritegtf.gtf",help="type the path to the gtf file that you want to use. By default it expects data from the standard input",default=None)
	parser.add_option("-o","--outfile",dest="outfile",help="type the name and path of the file you want to write the output to. Default is standard output",default=None)		
	parser.add_option("--count",dest="count",action="store_true",help="with this flag you the program will count the occurence for each source/annotation in the gtf file",default=False)
	(options, args) = parser.parse_args()
	data = sys.stdin
	out	 = sys.stdout
	if options.outfile:
		out = open(options.outfile,"w")
	if options.gtf_file:
		data = open(options.gtf_file,"r")
	sources,counts = getGTFSourceList(data)
	out.write("# %s\n# %s\n# source list generated from: %s\n" % (' '.join(sys.argv),time.ctime(),options.gtf_file))
	if options.count:
		for i in sources:
			out.write("%s\t%s\n" % (i,counts[i]))	
	else:
		for i in sources:
			out.write("%s\n" % (i))
			
if __name__ == "__main__":
	main()