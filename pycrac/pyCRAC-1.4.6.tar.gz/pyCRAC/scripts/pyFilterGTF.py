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
#	pyFilterGTF.py
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
from pyCRAC.Parsers import GTF2
from pyCRAC.Classes.NGSFormatWriters import *
from pyCRAC.Parsers.ParseAlignments import ParseCountersOutput

def filterGenes(genes,gtf,strand,orientation="sense",singlefeats=False):
	""" filters genes on whether they are sense or anti-sense to a feature """
	filteredgenes = list()
	for gene in genes:
		if gene in gtf.genes:
			if orientation == "sense":
				if gtf.strand(gene) == strand:
					filteredgenes.append(gene)
			else:
				if gtf.strand(gene) != strand:
					filteredgenes.append(gene)
			if singlefeats and len(filteredgenes) > 1:
				filteredgenes = list()
	return filteredgenes

def main():
	parser = OptionParser(usage="usage: %prog [options] -f filename", version="%s" % __version__)
	files = OptionGroup(parser, "File input options")
	files.add_option("-f", "--input_file", dest="filename",help="provide the path to your gtf data file. Default is standard input.", metavar="FILE",default=None)
	files.add_option("-o", "--output_file", dest="output_file",help=" Use this flag to provide an output file name. Default is standard output. ", default=None)
	files.add_option("--gtf",dest="annotation_file",metavar="annotation_file.gtf",help="type the path to the gtf annotation file that you want to use",default=None)
	filtering = OptionGroup(parser, "GTF filtering options")
	filtering.add_option("--singlefeats",dest="singlefeats",action="store_true",help="to remove intervals that were mapped to multiple gene names, sense or anti-sense. Default = False",default=False)
	filtering.add_option("-a","--annotation",dest="annotation",help="select which annotation (i.e. protein_coding, ncRNA, sRNA, rRNA, tRNA, snoRNA) you would like to focus your search on. Default = None.", metavar="protein_coding",default=None)
	filtering.add_option("--anti_sense",dest="anti_sense",action="store_true",help="by default pyFilterGTF.py only reports intervals that overlap 'sense' with features. Use this flag if you only want to plot intervals that map anti-sense.",default=False)
	parser.add_option_group(files)
	parser.add_option_group(filtering)
	(options, args) = parser.parse_args()
	
	### setting the orientation
	orientation = "sense"
	if options.anti_sense:
		orientation = "anti_sense"
	###

	### By default, input and output are expected from the standard input or standard output.
	infile = sys.stdin
	outfile = sys.stdout
	###
	
	### Making GTF2 parser object and parsing GTF annotation file ###
	gtf = GTF2.Parse_GTF()
	gtf.read_GTF(options.annotation_file,source=options.annotation,transcripts=False)
	###
	
	### Object for processing the GTF data files
	if options.filename:
		infile = open(options.filename,"r")
	datain = ParseCountersOutput(infile)
	###
	
	### Object for writing the GTF output filename
	if options.output_file:
		outfile = open(options.output_file,"w")
	dataout = NGSFileWriter(outfile)
	###
	
	while datain.readLineByLine(numpy=False,mutsseqpos=False,collectmutations=False):
		genes = filterGenes(datain.genes,gtf,datain.strand,orientation=orientation,singlefeats=options.singlefeats)
		if genes:
			dataout.writeGTF(datain.chromosome,datain.source,datain.type,datain.read_start,datain.read_end,datain.score,datain.strand,gene_name=",".join(genes),gene_id=",".join([gtf.gene2orf(i) for i in genes]),comments=datain.comments)		
	
if __name__ == "__main__":
	main()