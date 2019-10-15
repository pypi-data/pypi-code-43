#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.3"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyFasta2Tab.py
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
import os
from optparse import *
from pyCRAC.Methods import getfilename

def main():
	""" this program converts fasta files to the tabular output """
	parser = OptionParser(usage="usage: %prog -f filename.fasta", version="%s" % __version__)
	parser.add_option("-f", "--input_file",dest="fasta_file",metavar="fasta_file",help="provide the name and path of your fasta input file. Default is standard input.",default=None)
	parser.add_option("-o", "--output_file",dest="tab_file",metavar="tab_file",help="provide a name and path for your tab output file. Default is input with .tab extension",default=None),
	(options, args) = parser.parse_args()
	input = sys.stdin
	output_file = "%s.tab" % getfilename(input)
	output = None
	if options.fasta_file:
		input = open(options.fasta_file,"r")
		output_file = "%s.tab" % getfilename(options.fasta_file)
	if options.tab_file:
		output = open(options.tab_file,"w")
	else:
		output = open(output_file,"w")
	id = str()
	sequence = str()
	for line in input:
		if line.startswith(">") and sequence:		# if a new id has been found and sequence exists, print to file
			output.write("%s\t%s\n" % (id,sequence))
			id = line[1:].strip()
			sequence = str()
		elif line.startswith(">"):					# if only a new id has been found, store the id
			id = line[1:].strip()
		else:
			sequence += line.strip()				# else, concatenate the sequence strings
	output.write("%s\t%s\n" % (id,sequence))
		
if __name__ == "__main__":
	main()