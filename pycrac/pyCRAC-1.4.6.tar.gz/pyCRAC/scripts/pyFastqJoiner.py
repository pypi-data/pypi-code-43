#!/usr/bin/python

__author__		= 'Sander Granneman'
__copyright__	= 'Copyright 2019'
__version__		= '0.0.6'
__credits__		= ['Sander Granneman']
__maintainer__	= 'Sander Granneman'
__email__		= 'sgrannem@ed.ac.uk'
__status__		= 'Production'

##################################################################################
#
#	pyFastqJoiner.py
#
#
#	Copyright (c) Sander Granneman 2019
#	
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the 'Software'), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#	
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#	
#	THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#	THE SOFTWARE.
#
##################################################################################

"""
Joins two fastq files into one. Useful when you need to flatten or collaps paired end data

"""

import sys
import six
import gzip
from optparse import *
from pyCRAC.Methods import reverse_complement

def mergeFastqFiles(forward,reverse,filetype,merged=None,character=None,compressed=False,reversecomplement=False):
	''' merges the sequence and quality values of the two fastq files and returns a new fastq file. 
	This tool does NOT check whether the header names are the same, it simply merges them.
	When setting reverse_complement=True, the reverse reads will be reverse complemented before merging.'''
	
	### processing the input files ###

	fastq_f = None
	fastq_r = None

	supportedfiletypes = ['fastq','fastq.gz']
	
	if filetype == supportedfiletypes[0]:	   # if the input files are not compressed
		fastq_f	 = open(forward,'r')
		fastq_r	 = open(reverse,'r')
	elif filetype == supportedfiletypes[1]:	   # if the input files were compressed using gunzip
		fastq_f	 = gzip.open(forward,'rb')
		fastq_r	 = gzip.open(reverse,'rb')
	else:
		raise RuntimeError('\n\nUnrecognizable file type %s\n' % filetype)
	
	### preparing the output file. It is also possible to pipe the output to another script by not naming the output file ###
	
	if merged and not compressed:
		output	= open(merged,'w')
	elif merged and compressed:										   
		output	= gzip.open('%s.gz' % merged,'wb')
	else:
		output	= sys.stdout
	
	### iterating over the input files and merging the records ###		   
	
	files = list()
	files.extend([fastq_f,fastq_r,output])
	while True:
		try:
			line = str()
			name_f, name_r = str(six.next(fastq_f).strip()), str(six.next(fastq_r).strip())
			seq_f, seq_r   = str(six.next(fastq_f).strip()), str(six.next(fastq_r).strip())
			six.next(fastq_f)
			six.next(fastq_r)
			qual_f, qual_r = str(six.next(fastq_f).strip()), str(six.next(fastq_r).strip())

			if reversecomplement:
				seq_r  = reverse_complement(seq_r)	# reverse-complement the sequence string
				qual_r = qual_r[::-1]				# reversing the quality information				

			line = '%s%s\n%s%s%s\n+\n%s%s\n' % (name_f,name_r,seq_f,character,seq_r,qual_f,qual_r)

			if compressed:
				line = line.encode()
			output.write(line)

		except StopIteration:
			break
	for i in files:
		try:
			i.close()  
		except ValueError:
			pass   
		
def mergeFastaFiles(forward,reverse,filetype,merged=None,character=None,compressed=False,reversecomplement=False):
	''' merges the sequence and quality values of the two fasta files and returns a new fasta file. 
	NOTE!!!!This tool does NOT check whether the header names are the same, it simply merges them,'''
	
	### processing the input files ###

	fasta_f = None
	fasta_r = None
	supportedfiletypes = ['fasta','fasta.gz']
	
	if filetype == supportedfiletypes[0]:	   # if the input files are not compressed
		fasta_f	 = open(forward,'r')
		fasta_r	 = open(reverse,'r')
	elif filetype == supportedfiletypes[1]:	   # if the input files were compressed using gunzip
		fasta_f	 = gzip.open(forward,'rb')
		fasta_r	 = gzip.open(reverse,'rb')
	else:
		raise RuntimeError('\n\nUnrecognizable file type %s\n' % filetype)
	
	### preparing the output file. It is also possible to pipe the output to another script by not naming the output file ###		 
	
	if merged and not compressed:
		output	= open(merged,'w')
	elif merged and compressed:										   
		output	= gzip.open('%s.gz' % merged,'wb')
	else:
		output	= sys.stdout
	
	### iterating over the input files and merging the records ###		   
	
	files = list()
	files.extend([fasta_f,fasta_r,output])
	while True:
		try:
			line = str()
			name_f, name_r	= str(six.next(fasta_f).strip()),str(six.next(fasta_r).strip())
			seq_f,	seq_r	= str(six.next(fasta_f).strip()),str(six.next(fasta_r).strip())
			if reversecomplement:
				seq_r = reverse_complement(seq_r)	# reverse-complement the sequence string

			line = '%s%s\n%s%s%s\n' % (name_f,name_r,seq_f,character,seq_r)

			if compressed:
				line = line.encode()

			output.write(line)
				
		except StopIteration:
			break

	for i in files:
		try:
			i.close()  
		except ValueError:
			pass   
def main():
	parser = OptionParser(usage='usage: %prog [options] -f file1 file 2', version="%s" % __version__)
	parser.add_option('-f', '--filename',nargs=2,metavar='fastq_file1 fastq_file2',dest='filename',help='provide the names of two raw data files separated by a single space')
	parser.add_option('--file_type',choices=['fasta','fastq','fasta.gz','fastq.gz'],dest='filetype',help='type of file, uncompressed or compressed (fasta, fasta.gz, fastq.gz, (gzip/gunzip compressed)) fastq. Default is fastq', metavar='FASTQ',default='fastq')
	parser.add_option('--reversecomplement',dest='reversecomplement',action='store_true',help='to reverse-complement the reverse read before joining. Default is False',default=False)
	parser.add_option('-o', '--outfile',metavar='mergedfastq.fastq',dest='outfile',help='provide the name of the output file. By default it will be printed to the standard output',default=None)
	parser.add_option('-c', '--character',metavar="|",dest='character',help='This option adds the "|" character between the DNA sequences so that it is much easier to split the data again later on',default="")
	parser.add_option('--gz','--gzip', dest='gzip', action='store_true',help='use this option to compress all output file using gunzip or gzip (compression level 9). No need to add the .gz extension. Note that this slows down the program significantly', default=False)
	(options, args) = parser.parse_args()
	if not options.filename or len(options.filename) < 2:
		parser.error('you need to input two filenames!\nExample: -f file1.fastq file2.fastq\n')
	supportedfiletypes = ['fasta','fasta.gz','fastq','fastq.gz']
	if options.filetype in supportedfiletypes[:2]:
		mergeFastaFiles(options.filename[0],options.filename[1],options.filetype,merged=options.outfile,character=options.character,compressed=options.gzip,reversecomplement=options.reversecomplement)
	else:
		mergeFastqFiles(options.filename[0],options.filename[1],options.filetype,merged=options.outfile,character=options.character,compressed=options.gzip,reversecomplement=options.reversecomplement)
	
if __name__ == '__main__':
	main()