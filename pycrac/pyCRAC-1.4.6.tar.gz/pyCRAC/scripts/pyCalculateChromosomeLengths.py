#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "production"

##################################################################################
#
#	pyCalculateChromosomeLengths.py
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
from optparse import *
from pyCRAC.Classes.Exceptions import FileTypeError

def main():
	""" this program converts fasta files to the tabular output """
	parser = OptionParser(usage="usage: %prog -f filename.fasta", version="%s" % __version__)
	parser.add_option("-f", "--input_file",dest="input_file",metavar="chromosomes.fasta",help="provide the name and path of your fasta or tab genomic sequence file. Default is standard input.",default=None)
	parser.add_option("--file_type",choices=["fasta","tab"],metavar="fasta",help="provide the file type (fasta or tab). Default is fasta",default="fasta")
	parser.add_option("-o","--output_file",dest="output_file",metavar="FILE",help="to provide an output file name. Default is standard output",default=None)
	parser.add_option("--trim",dest="trim",action="store_true",help="to trim the header of the chromosome name. This shortens the name to make it the same as in the GTF file. Please double check the output to make sure this went correctly!")
	(options, args) = parser.parse_args()
	input  = sys.stdin
	output = sys.stdout
	if options.input_file:
		input  = open(options.input_file,"r")
	if options.output_file:
		output = open(options.output_file,"w")
	chromosome = str()
	sequence   = str()
	if options.file_type == "fasta":
		for line in input:
			if line.startswith(">") and sequence:		# if a new id has been found and sequence exists, print to file
				output.write("%s\t%s\n" % (chromosome,len(sequence)))
				if options.trim:
					chromosome = line[1:].strip().split()[0]  # only retain the first part!
				else:
					chromosome = line[1:].strip()
				sequence = str()
			elif line.startswith(">"):					# if only a new id has been found, store the id
				if options.trim:
					chromosome = line[1:].strip().split()[0]  # only retain the first part!
				else:
					chromosome = line[1:].strip()
			else:
				sequence += line.strip()				# else, concatenate the sequence strings
		output.write("%s\t%s\n" % (chromosome,len(sequence)))
	elif options.file_type == "tab":
		for line in input:
			chromosome,sequence = line.strip().split()
			output.write("%s\t%s\n" % (chromosome,len(sequence)))
		
	else:
		raise FileTypeError("\nI do not recognize the %s format. Please choose from 'fasta' or 'tab'\n")
	output.close()
		
if __name__ == "__main__":
	main()