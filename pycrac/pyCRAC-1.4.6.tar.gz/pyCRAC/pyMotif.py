#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.1.0"
__credits__		= ["Sander Granneman","Grzegorz Kudla"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyMotif.py
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
from optparse import *
from pyCRAC.Classes.Motifs import *
from pyCRAC.Parsers import GTF2

def main():
	"""This program can only be used with an alignment file that has been generated using the genome as reference sequence!"""
	parser = OptionParser(usage="usage: %prog [options] -f filename --gtf=yeast.gtf --tab=yeast.tab", version="%s" % __version__)
	files = OptionGroup(parser, "File input options")
	files.add_option("-f", "--input_file", dest="filename",help="Provide the path to an interval gtf file. By default it expects data from the standard input.", metavar="intervals.gtf",default=None)
	files.add_option("-o", "--output_file", dest="output_file",help="Use this flag to override the standard file names. Do NOT add an extension.", default=None)
	files.add_option("--file_type",dest="file_type",choices=['bed','gff','gtf'], help=SUPPRESS_HELP,default='gtf')
	files.add_option("--gtf",dest="annotation_file",metavar="annotation_file.gtf",help="type the path to the gtf annotation file that you want to use",default=None)
	files.add_option("--tab",dest="tab_file",metavar="tab_file.tab",help="type the path to the tab file that contains the genomic reference sequence",default=None) 
	specific = OptionGroup(parser, "pyMotif specific options")
	specific.add_option("--k_min", dest="k_length_min",type="int",metavar="4",help="this option allows you to set the shortest k-mer length. Default = 4.",default=4)
	specific.add_option("--k_max", dest="k_length_max",type="int",metavar="6",help="this option allows you to set the longest k-mer length. Default = 8.",default=8)
	specific.add_option("-n","--numberofkmers",dest="motif_number",type="int",metavar=100,help="choose the maximum number of enriched k-mer sequences you want to have reported in output files. Default = 1000",default=100000)
	common = OptionGroup(parser, "pyCRAC common options")	
	common.add_option("-a","--annotation",dest="annotation",help="select which annotation (i.e. protein_coding, ncRNA, sRNA, rRNA,snoRNA,snRNA, depending on the source of your GTF file) you would like to focus your search on. Default = all annotations",metavar="protein_coding",default=None) 
	common.add_option("-r","--range",dest="range",type="int",metavar="100",help="allows you to add regions flanking the genomic feature. If you set '-r 50' or '--range=50', then the program will add 50 nucleotides to each feature on each side regardless of whether the GTF file has genes with annotated UTRs.",default=False)
	common.add_option("-v","--verbose",dest="verbose",action="store_true",help="prints all the status messages to a file rather than the standard output",default=False)
	common.add_option("--overlap",dest="overlap",help="sets the number of nucleotides a motif has to overlap with a genomic feature before it is considered a hit. Default =  1 nucleotide",type="int",metavar="1",default=1)
	common.add_option("--zip", dest="zip",metavar="FILE", help="use this option to compress all the output files in a single zip file", default=None)
	parser.add_option_group(files)
	parser.add_option_group(specific)
	parser.add_option_group(common)
	# the --out option is used by Galaxy to override default output file names. Four file names need to be included. First file will contain Z-scores, second the random motifs, third the motifs found in the data and fourth file will contain motifs found in genes.'
	# recommended file names: 'Z_scores.txt','random_k-mer_hit_list.txt','data_k-mer_hit_list.txt','top_k-mers_in_features.gtf'
	(options, args) = parser.parse_args()
	status = sys.stdout
	if options.verbose:
		status = open("pyMotif_log.txt","w")
	if not options.filename:
		options.filename = sys.stdin
	if len(sys.argv) < 1:
		parser.error("no input files detected, use -h or --help for instructions on how to use the program\n")
	if not options.annotation_file:
		parser.error("you forgot to input the GTF annotation file\n")
	if not options.tab_file:
		parser.error("you forgot to input the .tab file\n")
	
	### Making GTF2 parser object and parsing GTF annotation file ###
	status.write("processing gtf annotation and genomic sequence files...\n")
	gtf = GTF2.Parse_GTF()
	gtf.read_GTF(options.annotation_file,ranges=options.range,source=options.annotation,transcripts=False)
	gtf.read_TAB(options.tab_file)
	###

	### creating a FindMotifs object
	motifs = FindMotifs()
	### setting lengths of the k-mers to be extracted and set the annotation
	motifs.setKmerLength(k_min=options.k_length_min, k_max=options.k_length_max)
	motifs.annotation = options.annotation
	
	### processing the read data and finding motifs:
	status.write("finding motifs...\n")
	motifs.findMotifs(gtf,options.filename,min_overlap=options.overlap)
	###
	
	status.write("calculating k-mer Z-scores...\n")
	motifs.calcMotifZscores()

	motifs.printMotifZscores(output_file=options.output_file,max_motifs=options.motif_number)
	status.write("printing k-mers hits...\n")
	motifs.printRandKmers(output_file=options.output_file,max_motifs=options.motif_number)
	status.write("printing randomly extracted k-mer hits...\n")
	motifs.printExperimentalKmers(output_file=options.output_file,max_motifs=options.motif_number)
	status.write("printing k-mer gtf file...\n")
	motifs.printMotifGTFfile(output_file=options.output_file,max_motifs=options.motif_number)
	status.write("DONE!...\n")	

	if options.zip:					
		import zipfile
		status.write("compressing files...\n")
		file = zipfile.ZipFile(options.zip,mode="w",compression=zipfile.ZIP_DEFLATED)
		for files in motifs.file_list:
			file.write(files)
		file.close()	
		for files in motifs.file_list:
			try:
				os.remove(files)
			except OSError:
				pass   

if __name__ == "__main__":
	main()