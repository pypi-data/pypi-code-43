#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.6"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "beta"

##################################################################################
#
#	pyCheckGTFfile.py
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

##### This tool looks for duplicate gene names in GTF files and replaces these with the gene_id or transcript_name.

from pyCRAC.Classes.NGSFormatReaders import *
from pyCRAC.Methods import getfilename
from collections import defaultdict
from optparse import *

gtfdict = defaultdict(set)

def processGTFFile(infile,outfile,status):
	#store the gene_id-gene_name combinations in a dictionary and keeps track how many gene_ids there are per gene_name
	count = 0
	allowedfeatures = ["exon","CDS","5UTR","3UTR","start_codon","stop_codon"]
	gtf = NGSFileReader(infile)
	rejected = open("%s_incompatible.gtf" % getfilename(infile),"w")
	while gtf.readGTFLine():
		if gtf.feature in allowedfeatures:
			if not gtf.gene_name:
				gtf.gene_name = gtf.gene_id
			elif not gtf.gene_id:
				rejected.write(gtf.line)
				continue
			gtfdict[gtf.gene_name].add((gtf.chromosome,gtf.gene_id,gtf.gene_name))
	gtf = NGSFileReader(infile)
	outfile.write("##gff-version 2\n")
	while gtf.readGTFLine():
		if gtf.feature in allowedfeatures:
			if not gtf.gene_name:
				gtf.gene_name = gtf.gene_id
			if len(gtfdict[gtf.gene_name]) > 1:	   # if there is more than one gene_id for a gene_name, make sure the gene_name is changed
				if not gtf.gene_name:
					gtf.gene_name = gtf.gene_id					 
				if (gtf.chromosome,gtf.gene_id,gtf.gene_name) in gtfdict[gtf.gene_name]:
					position = sorted(gtfdict[gtf.gene_name]).index((gtf.chromosome,gtf.gene_id,gtf.gene_name))+1
					if gtf.gene_id == gtf.gene_name:
						gtf.line = gtf.line.replace("gene_id \"%s\"" % gtf.gene_id,"gene_id \"%s#%s\"" % (gtf.gene_id,position))
					gtf.line = gtf.line.replace("gene_name \"%s\"" % gtf.gene_name,"gene_name \"%s#%s\"" % (gtf.gene_name,position))
			outfile.write("%s" % gtf.line)
		else:
			rejected.write(gtf.line)
	outfile.close()
	rejected.close()

def main():
	parser = OptionParser(usage="usage: %prog [options] --gtf filename -o outputfile.gtf", version="%s" % __version__)
	parser.add_option("--gtf",dest="gtf_file",metavar="gtf input file",help="type the path to the gtf file that you want to use.",default=None)
	parser.add_option("-o","--output",dest="output_file",metavar="FILE",help="Optional. Specify the name of the output file. Default is standard output. Make sure it has the .gtf extension!",default=None)
	parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="To print status messages to a log file",default=False)
	(options, args) = parser.parse_args()
	if len(sys.argv) < 1:
		parser.error("usage: %prog [options] --gtf filein -o fileout. Use -h or --help for options")
	if not options.gtf_file:
		parser.error("\nYou forgot to input the path to your GTF input file\n")
	if not options.output_file:
		parser.error("\nYou forgot to include a name for your output file\n")
	gtf = options.gtf_file
	outfile = open(options.output_file,"w")
	status = sys.stderr	 
	if options.verbose:
		status = open("pyCheckGTFfile_log.txt","w")
		
	processGTFFile(gtf,outfile,status)
		
if __name__ == "__main__":
	main()