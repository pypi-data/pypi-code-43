#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyFastqSplitter.py
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

""" 
Splits a fastq or fasta file by looking for the character that separates the two DNA sequences. Useful when you collapsed your data

"""

import sys
import six
import gzip
import argparse
from ruffus.cmdline import MESSAGE

def getfilename(filepath):
	""" Returns the file name without path and extension"""
	if isinstance(filepath,file) or not filepath:
			return "standard_input"
	else:
			return filepath.split("/")[-1].split(".")[0]
			
def headersplitter(string,filetype="fastq"):
	""" splits the header on the @ character"""
	if filetype is "fastq":
		Fld = string.split("@")[1:]
		assert len(Fld) == 2, "Can not split the %s header correctly! %s @ characters in the header\n" % (string, len(Fld))
		header_f = "@%s" % Fld[0]
		header_r = "@%s" % Fld[1]
		return header_f,header_r
	elif filetype is "fasta":
		Fld = string.split(">")[1:]
		if len(Fld) is 2:
			header_f = ">%s" % Fld[0]
			header_r = ">%s" % Fld[1]
		elif len(Fld) is 1:
			header_f = ">%s/1" % Fld[0]
			header_r = ">%s/2" % Fld[0]
		return header_f,header_r
	else:
		raise TypeError("I do not recognize the file type %s. Please use 'fasta' or 'fastq'\n")
					
def splitFastqFile(inputfile,outputfiles,filetype="fasta",character="|",compressed=False):
	""" Splits fastq files by looking for a specific character that splits the two DNA sequences.
	If this character is not present then it will simply split the DNA sequence in half, provided the length is an even number"""
	
	### processing the input files ###

	supportedfiletypes = ["fastq","fastq.gz"]
	
	if not inputfile:										# if the input comes from the standard input
		input = sys.stdin
	elif inputfile and filetype == supportedfiletypes[0]:	# if the input file is not compressed
		input = open(inputfile,"r")
	elif inputfile and filetype == supportedfiletypes[1]:	# if the input file was compressed using gunzip
		input = gzip.open(inputfile,"rb")
	else:
		raise RuntimeError("\n\nUnrecognizable file type %s\n" % filetype)
	
	### preparing the output files ###		  
	
	if len(outputfiles) == 2:
		forward,reverse = outputfiles
		if compressed:
			output_f = gzip.open("%s" % forward, "wb")
			output_r = gzip.open("%s" % reverse, "wb")
		else:
			output_f = open("%s" % forward, "w")
			output_r = open("%s" % reverse, "w")
	else:
		if len(outputfiles) == 1: 	## Only one file name provided. To maintain compatibility with existing pipelines.
			file_name = outputfiles[0]
			forward = "%s_1" % (file_name)
			reverse = "%s_2" % (file_name)
		elif not outputfiles: 			## No file name provided
			file_name = getfilename(inputfile)
			forward = "%s_1" % (file_name)
			reverse = "%s_2" % (file_name,)
		elif not inputfile and not outputfiles:
			forward = "standard_output_1"
			reverse = "standard_output_2"
		else:
			sys.stderr.write("cannot determine what the output files should be called!\n")

		if compressed:
			outtype	 = "fastq.gz"
			output_f = gzip.open("%s.%s" % (forward,outtype), "wb")
			output_r = gzip.open("%s.%s" % (reverse,outtype), "wb")
		else:
			outtype	 = "fastq"
			output_f = open("%s.%s" % (forward,outtype), "w")
			output_r = open("%s.%s" % (reverse,outtype), "w")

	files	= list()
	files.extend([input,output_f,output_r])			# this list keeps track of all the files/streams
	
	### iterating over the input files and merging the records ###		   
	
	while True:
		try:
			line_f = str()
			line_r = str()
			name	 = str(six.next(input).strip())
			sequence = str(six.next(input).strip())
			six.next(input)
			quality	 = str(six.next(input).strip())

			header_f,header_r = headersplitter(name,filetype="fastq")				 
			if character:
				seq_f,seq_r	  = sequence.split(character)
				qual_f,qual_r = quality[:len(seq_f)],quality[len(seq_f):]
			else:
				seqlen = len(sequence)
				if seqlen%2!=0:
					raise RuntimeError("\n\nThe sequence can not be split because the length is an uneven number\n")
				else:
					halfseqlength = len(sequence)/2
					seq_f,seq_r	  = sequence[:halfseqlength],sequence[halfseqlength:]
					qual_f,qual_r = quality[:halfseqlength],quality[halfseqlength:]

			line_f = '%s\n%s\n+\n%s\n' % (header_f,seq_f,qual_f)
			line_r = '%s\n%s\n+\n%s\n' % (header_r,seq_r,qual_r)

			if compressed:
				line_f = line_f.encode()
				line_r = line_r.encode()

			output_f.write(line_f)
			output_r.write(line_r)
				
		except StopIteration:
			break
	for i in files:
		i.close()	

def splitFastaFile(inputfile,outputfiles,filetype="fasta",character="|",compressed=False):
	""" Splits fastq files by looking for a specific character that splits the two DNA sequences.
	If this character is not present then it will simply split the DNA sequence in half, provided the length is an even number"""
	
	### processing the input files ###

	supportedfiletypes = ["fasta","fasta.gz"]
	
	if not inputfile:										# if the input comes from the standard input
		input = sys.stdin
	elif inputfile and filetype == supportedfiletypes[0]:	# if the input file is not compressed
		input = open(inputfile,"r")
	elif inputfile and filetype == supportedfiletypes[1]:	# if the input file was compressed using gunzip
		input = gzip.open(inputfile,"rb")
	else:
		raise RuntimeError("\n\nUnrecognizable file type %s\n" % filetype)
	
	### preparing the output files ###		  
	
	if len(outputfiles) == 2:
		forward,reverse = outputfiles
		if compressed:
			output_f = gzip.open("%s" % forward, "wb")
			output_r = gzip.open("%s" % reverse, "wb")
		else:
			output_f = open("%s" % forward, "w")
			output_r = open("%s" % reverse, "w")
	else:
		if len(outputfiles) == 1: 	## Only one file name provided. To maintain compatibility with existing pipelines.
			file_name = outputfiles[0]
			forward = "%s_1" % (file_name)
			reverse = "%s_2" % (file_name)
		elif not outputfiles: 			## No file name provided
			file_name = getfilename(inputfile)
			forward = "%s_1" % (file_name)
			reverse = "%s_2" % (file_name,)
		elif not inputfile and not outputfiles:
			forward = "standard_output_1"
			reverse = "standard_output_2"
		else:
			sys.stderr.write("cannot determine what the output files should be called!\n")

		if compressed:
			outtype	 = "fasta.gz"
			output_f = gzip.open("%s.%s" % (forward,outtype), "wb")
			output_r = gzip.open("%s.%s" % (reverse,outtype), "wb")
		else:
			outtype	 = "fasta"
			output_f = open("%s.%s" % (forward,outtype), "w")
			output_r = open("%s.%s" % (reverse,outtype), "w")

	files	= list()
	files.extend([input,output_f,output_r])			# this list keeps track of all the files/streams
	
	### iterating over the input files and merging the records ###		   
	
	while True:
		try:
			line_f = str()
			line_r = str()
			name	 = str(six.next(input).strip())
			sequence = str(six.next(input).strip())

			header_f,header_r = headersplitter(name,filetype="fasta")
			if character:
				seq_f,seq_r	  = sequence.split(character)
			else:
				seqlen = len(sequence)
				if seqlen%2!=0:
					raise RuntimeError("\n\nThe sequence can not be split becuase the length is an uneven number\n")
				else:
					halfseqlength = len(sequence)/2
					seq_f,seq_r	  = sequence[:halfseqlength],sequence[halfseqlength:]

			line_f = '%s\n%s\n' % (header_f,seq_f)
			line_r = '%s\n%s\n' % (header_r,seq_r)

			if compressed:	# if the output file is compressed:
				line_f = line_f.encode()
				line_r = line_r.encode()

			output_f.write(line_f)
			output_r.write(line_r)

		except StopIteration:
			break

	for i in files:
		i.close()				
def main():
	parser = argparse.ArgumentParser(usage="usage: %prog [options] -f file")
	parser.add_argument("-f", "--filename",metavar="fastq_file",dest="filename",help=" To provide the names of two raw data files separated by a single space. Default = standard input",default=None)
	parser.add_argument("-o", "--outfiles",nargs="*",metavar="prefix or forward.fasta,reverse.fasta",dest="outfiles",help="provide either a prefix for the output file names or the full names of the forward and reverse output files.",default=None)
	parser.add_argument("--file_type", dest="filetype",choices=["fasta","fasta.gz","fastq","fastq.gz"],help="type of file, uncompressed or compressed (fastq.gz, gzip/gunzip compressed) fastq. Default is fastq",metavar="FASTQ",default="fastq")
	parser.add_argument("-c", "--character",metavar="|",dest="character",help="If the joined sequences were separated by a specific character then the program can divide the sequences by looking for that character",default=None)
	parser.add_argument("--gz","--gzip", dest="gzip",action="store_true",help="use this option to compress all output file using gunzip or gzip (compression level 9). Note that this slows down the program significantly", default=False)
	args = parser.parse_args()

	supportedfiletypes = ["fasta","fasta.gz","fastq","fastq.gz"]
	if args.filetype in supportedfiletypes[:2]:
		splitFastaFile(args.filename,args.outfiles,args.filetype,args.character,compressed=args.gzip)
	else:
		splitFastqFile(args.filename,args.outfiles,args.filetype,args.character,compressed=args.gzip)
			
if __name__ == "__main__":
	main()