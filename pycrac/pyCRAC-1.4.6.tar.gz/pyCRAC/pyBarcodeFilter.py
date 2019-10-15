#!/usr/bin/python

__authors__		= ["Sander Granneman"]
__copyright__	= "Copyright 2019"
__version__		= "3.1"
__credits__		= ["Sander Granneman","Grzegorz Kudla"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyBarcodeFilter.py
#
#
#	Copyright (c) Sander Granneman and Grzegorz Kudla 2019
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
import time
from optparse import *
from pyCRAC.Classes.Barcodes import *
					
def main():
	parser = OptionParser(usage="usage: %prog [options] -f filename -b barcode_list", version="%s" % __version__)
	parser.add_option("-f", "--input_file", dest="filename",help="name of the FASTQ or FASTA input file", metavar="FILE")
	parser.add_option("-r", "--reverse_input_file", dest="filename_reverse",help="name of the paired (or reverse) FASTQ or FASTA input file", metavar="FILE")
	parser.add_option("--file_type", dest="filetype",help="type of file, uncompressed (fasta or fastq) or compressed (fasta.gz or fastq.gz, gzip/gunzip compressed). Default is fastq", metavar="FASTQ",default="fastq")
	parser.add_option("-b", "--barcode_list", dest="barcode_list",help="name of tab-delimited file containing barcodes and barcode names", metavar="FILE",default=None)
	parser.add_option("-k", "--keep_barcode", dest= "keep_barcode", action="store_true", help="in case you do not want to remove the in read barcode from the sequences. Useful when uploading data to repositories.",default=False)
	parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="prints all the status messages to a file rather than the standard output.",default=False)
	parser.add_option("--search",choices=["forward","reverse"],help="use this flag if barcode sequences need to be removed from the forward or the reverse reads. The tool assumes. Default=forward", default="forward")
	parser.add_option("-m", "--mismatches", dest="mismatches",help="to set the number of allowed mismatches in a barcode. Only one mismatch is allowed. Default = 0", type="int",metavar="1",default=0)
	parser.add_option("-i", "--index", dest="index",help="use this option if you want to split the data using the Illumina indexing barcode information",action="store_true",default=False)
	parser.add_option("--gz","--gzip", dest="gzip", action="store_true",help="use this option to compress all the output files using gunzip or gzip (compression level 9). Note that this can significantly slow down the program", default=False)
	(options, args) = parser.parse_args()
	data = None
	if len(sys.argv) < 4:
		parser.error("At least two file arguments are required. Use -h option for usage\n")
	if not options.barcode_list:
		parser.error("You forgot to enter the name of the file containing the barcodes. Use the -b flag for this purpose\n")
	if not options.filename:
		parser.error("You forgot to enter the name of the (forward) raw data file. Use the -f flag for this purpose\n")
	if options.index:
		data = IndexingBarcodeSplitter(options.filetype,options.filename,options.filename_reverse,options.barcode_list,allowedmismatches=options.mismatches,gzip=options.gzip)
		if options.filename_reverse:
			if re.search("fastq",options.filetype):
				data.processPairedFastqFileIndexes()
			elif re.search("fasta",options.filetype):
				data.processPairedEndFastAFileIndexes()
			else:
				parser.error("\nDid not recognize the %s file type\n" % options.filetype)
		else:
			if re.search("fastq",options.filetype):
				data.processFastqFileIndexes()
			elif re.search("fasta",options.filetype):
				data.processFastAFileIndexes()
			else:
				parser.error("\nDid not recognize the %s file type\n" % options.filetype)

	else:
		data = BarcodeSplitter(options.filetype,options.filename,options.filename_reverse,options.barcode_list,allowedmismatches=options.mismatches,gzip=options.gzip,keepbarcode=options.keep_barcode,search=options.search)
		if options.filename_reverse:
			if re.search("fastq",options.filetype):
				data.processPairedEndFastQFiles()
			elif re.search("fasta",options.filetype):
				data.processPairedEndFastAFiles()
			else:
				parser.error("\nDid not recognize the %s file type\n" % options.filetype)
		else:
			if re.search("fastq",options.filetype):
				data.processFastQFile()
			elif re.search("fasta",options.filetype):
				data.processFastAFile()
			else:
				parser.error("\nDid not recognize the %s file type\n" % options.filetype)

	data.printRandBarcodeStats()
	data.printBarcodeStats()

if __name__ == "__main__":
	main()