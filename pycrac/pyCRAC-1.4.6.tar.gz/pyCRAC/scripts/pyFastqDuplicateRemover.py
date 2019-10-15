#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright "
__version__		= "0.0.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyFastqDuplicateRemover.py
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
import re
import six
from collections import defaultdict
from optparse import *

def getfilename(filepath):
	""" Returns the file name without path and extension"""
	return filepath.split("/")[-1].split(".")[0]

def trackDuplicates(file_input):
	""" keeps track of the cDNA duplicates using both random barcode sequences (if available)
	and the nucleotide sequence. Counts the number of duplicates. Returns a dictionary """
	randbarcode = None
	header		= str()
	tracker		= defaultdict(int)
	splitter	= "##"	# the character(s) that divide the header and random barcode sequence
	while True:
		try:
			name_f = six.next(file_input).strip()
			seq_f  = six.next(file_input).strip()
			if name_f.startswith("@"):	# for fastq files
				six.next(file_input)	# To make sure that the next round it starts at a header again in the next round
				six.next(file_input)	# The program doesn't care about the quality values				
				if re.search(splitter,name_f):	# If there is a random barcode sequence in the header of the forward sequence...
					randbarcode = re.split(splitter,name_f)[-1].split("@")[0]  # split again with @ in case these are joined header from paired end fastq data
			elif name_f.startswith(">"): # for fasta files
				if re.search(splitter,name_f):	# If there is a random barcode sequence in the header of the forward sequence...
					randbarcode = re.split(splitter,name_f)[-1].split(">")[0]  # split again with > in case these are joined header from paired end fasta data
			
			tracker[randbarcode,seq_f] += 1
					
		except StopIteration:
			break
	
	return tracker

def trackPairedEndDuplicates(forward,reverse):
	""" Tracks duplicates in Paired-End data. Returns a dictionary """
	randbarcode = None
	header		= str()
	tracker		= defaultdict(int)
	splitter	= "##"	# the character(s) that divide the header and random barcode sequence
	while True:
		try:
			name_f, name_r	= six.next(forward).strip(),six.next(reverse).strip()
			seq_f,	seq_r	= six.next(forward).strip(),six.next(reverse).strip()
			if name_f.startswith("@"):
				six.next(forward)		# To make sure that the next round it starts at a header again in the next round
				six.next(reverse)		# The program doesn't care about the quality values
				six.next(forward)
				six.next(reverse)
			if re.search(splitter,name_f):	# If there is a random barcode sequence in the header of the forward sequence...
				randbarcode = re.split(splitter,name_f)[-1]
			else:
				randbarcode = "##"
			tracker[randbarcode,seq_f,seq_r] += 1
			
		except StopIteration:
			break
	
	return tracker
	
def printFastaFile(tracker,output=None):
	""" prints the results in fasta format. Header includes random barcode sequence and number of duplicates """
	if output:
		file_output = open(output,"w")
	else:
		file_output = sys.stdout		# if it doesn't get
		
	for rank,key in enumerate(tracker,start=1):
		randbarcode,sequence = key
		if randbarcode:
			file_output.write(">%s_%s_%s\n%s\n" % (rank,randbarcode,tracker[randbarcode,sequence],sequence))
		else:
			file_output.write(">%s_%s\n%s\n" % (rank,tracker[randbarcode,sequence],sequence))

def printPairedEndFastaFile(tracker,output=None):
	""" prints the results in fasta format for Paired-End data. Header includes random barcode sequence and number of duplicates """
	file_name = str()
	if output:
		file_name = getfilename(output)
	else:
		file_name = "collapsed"
	output_f = open("%s_1.fasta" % (file_name), "w")
	output_r = open("%s_2.fasta" % (file_name), "w")
	for rank,key in enumerate(tracker,start=1):
		randbarcode,sequence_f,sequence_r = key
		if randbarcode:
			output_f.write(">%s_%s_%s/1\n%s\n" % (rank,randbarcode,tracker[randbarcode,sequence_f,sequence_r],sequence_f))
			output_r.write(">%s_%s_%s/2\n%s\n" % (rank,randbarcode,tracker[randbarcode,sequence_f,sequence_r],sequence_r))
		else:
			output_f.write(">%s_%s/1\n%s\n" % (rank,tracker[randbarcode,sequence_f,sequence_r],sequence_f))
			output_r.write(">%s_%s/2\n%s\n" % (rank,tracker[randbarcode,sequence_f,sequence_r],sequence_r))

def main():
	parser = OptionParser(usage="usage: %prog [options] -f forwardfile -r reversefile -o collapsed.fasta", version="%s" % __version__)
	files = OptionGroup(parser,"File input options")
	parser.add_option("-f", "--input_file", dest="infile_forward",help="name of the FASTQ or FASTA input file. Default is standard input", metavar="FILE",default=None)
	parser.add_option("-r", "--reverse_input_file", dest="infile_reverse",help="name of the paired (or reverse) FASTQ or FASTA input file", metavar="FILE",default=None)
	parser.add_option("-o", "--output_file", dest="outfile",help="Provide the path and name of the fasta output file. Default is standard output. For paired-end data just provide a file name without file extension (!)",metavar="FILE",default=None)
	(options, args) = parser.parse_args()
	infile_f  = sys.stdin
	outfile	  = None
	if options.outfile: 
		outfile = options.outfile
	if options.infile_forward and not options.infile_reverse: 
		infile_f = open(options.infile_forward,"r")
		datadict = trackDuplicates(infile_f)
		printFastaFile(datadict,outfile)
	elif options.infile_forward and options.infile_reverse: 
		infile_f = open(options.infile_forward,"r")
		infile_r = open(options.infile_reverse,"r")
		datadict = trackPairedEndDuplicates(infile_f,infile_r)
		printPairedEndFastaFile(datadict,outfile)
	else:
		datadict = trackDuplicates(infile_f)
		printFastaFile(datadict,outfile)

if __name__ == "__main__":
	main()
