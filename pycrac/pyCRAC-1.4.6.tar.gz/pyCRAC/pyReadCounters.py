#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.5.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyReadCounters.py
#
#
#	Copyright (c) Sander Granneman 2018
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
import os
from optparse import *
from pyCRAC.Classes.Counters import PyCounters
from pyCRAC.Parsers import GTF2

def main(): 
	parser = OptionParser(usage="usage: %prog [options] -f filename", version="%s" % __version__)
	files = OptionGroup(parser, "File input options")
	files.add_option("-f", "--input_file", dest="filename",help="provide the path to your novo, SAM/BAM or gtf data file. Default is standard input. Make sure to specify the file type of the file you want to have analyzed using the --file_type option!", metavar="FILE",default=None)
	files.add_option("-o", "--output_file", dest="output_file",help="Use this flag to override the standard file names. Do NOT add an extension.", default=None)
	files.add_option("--file_type",dest="file_type",choices=["novo","sam","gtf"],help="use this option to specify the file type (i.e. 'novo','sam' or 'gtf'). This will tell the program which parsers to use for processing the files. Default = 'novo'",default="novo")
	files.add_option("--gtf",dest="annotation_file",metavar="annotation_file.gtf",help="type the path to the gtf annotation file that you want to use",default=None)
	common = OptionGroup(parser, "Common pyCRAC options")
	common.add_option("-a","--annotation",dest="annotation",help="select which annotation (i.e. protein_coding, ncRNA, sRNA, rRNA, tRNA, snoRNA) you would like to focus your search on. Default = all.", metavar="protein_coding",default=None)
	common.add_option("-v","--verbose",dest="verbose",action="store_true",help="prints all the status messages to a file rather than the standard output",default=False)
	common.add_option("--ignorestrand",dest="nostrand",action="store_true",help="To ignore strand information and all reads overlapping with genomic features will be considered sense reads. Useful for analysing ChIP or RIP data",default=False)
	common.add_option("--overlap",dest="overlap",help="sets the number of nucleotides a read has to overlap with a gene before it is considered a hit. Default =  1 nucleotide",type="int",metavar="1",default="1")
	common.add_option("-r","--range",dest="range",type="int",metavar="100",help="allows you to add regions flanking the genomic feature. If you set '-r 50' or '--range=50', then the program will add 50 nucleotides to each feature on each side regardless of whether the GTF file has genes with annotated UTRs.",default=False)
	common.add_option("--rpkm",dest="rpkm",action="store_true",help="to include a column showing reads per kilobase per 1 million mapped reads for each gene. Default is False.",default=False)
	common.add_option("--nucdensities",dest="nucdensities",action="store_true",help="With this flag nucleotide densities are calculated (i.e. the total number of nucleotides overlapping with a feature). Default is False.",default=False)
	common.add_option("--properpairs",dest="properpairs",action="store_true",help="In case you have paired-end data, you can use this flag to analyze only properly paired reads. Default is False",default=False)
	common.add_option("--sense",dest="sense",action="store_true",help="this option instructs pyReadCounters to only consider reads overlapping sense with genomic features. Default is False",default=False)
	common.add_option("--anti_sense",dest="anti_sense",action="store_true",help="this option instructs pyReadCounters to only consider reads overlapping anti-sense with genomic features. Default is False",default=False)
	novo = OptionGroup(parser, "Options for SAM/BAM and Novo files")
	novo.add_option("--force_single_end",dest="force_single_end",action="store_true",help="To consider all reads unpaired, even if it is paired end data.Default is False.",default=False)
	novo.add_option("--hittable",dest="hittable",action="store_true",help="use this flag if you only want to print a hit table for your data",default=False)
	novo.add_option("--gtffile",dest="gtffile",action="store_true",help="use this flag if you only want to print the pyReadCounters gtf file for your data",default=False)
	novo.add_option("--stats",dest="stats",action="store_true",help="use this flag if you only want to print a the statistics showing the complexity of your data",default=False)
	novo.add_option("-s","--sequence",dest="sequence",metavar="intron",choices=["intron","genomic","CDS","exon","5UTR","3UTR"],help="with this option you can select whether you want to count reads overlapping coding or genomic sequence or intron, exon, CDS, 5UTR or 3UTR coordinates. Default = genomic.",default="genomic")
	novo.add_option("--mutations",dest="muts",metavar="delsonly",help="Use this option to only track mutations that are of interest. For CRAC data this is usually deletions (--mutations=delsonly). For PAR-CLIP data this is usually T-C mutations (--mutations=TC). Other options are: do not report any mutations: --mutations=nomuts. Only report specific base mutations, for example only in T's, C's and G's :--mutations=[TCG]. The brackets are essential. Other nucleotide combinations are also possible",default=None)
	novo.add_option("--align_quality", "--mapping_quality", dest="align_quality", metavar="100", type="int", help="with these options you can set the alignment quality (Novoalign) or mapping quality (SAM) threshold. Reads with qualities lower than the threshold will be ignored. Default = 0", default=None)
	novo.add_option("--align_score", dest="align_score", metavar="100", type="int", help="with this option you can set the alignment score threshold. Reads with alignment scores lower than the threshold will be ignored. Default = 0", default=None)
	novo.add_option("--unique",dest="unique",action="store_true",help="with this option reads with multiple alignment locations will be removed. Default = Off",default=False)	 
	novo.add_option("--blocks",dest="blocks",action="store_true",help="with this option reads with the same start and end coordinates on a chromosome will be counted as one cDNA. Default = Off",default=False)
	novo.add_option("-d","--distance",dest="distance",metavar="1000",type="int",help="this option allows you to set the maximum number of base-pairs allowed between two non-overlapping paired reads. Default = 1000",default=1000)
	novo.add_option("--discarded",dest="discarded",metavar="FILE", help="prints the lines from the alignments file that were discarded by the parsers. This file contains reads that were unmapped (NM), of poor quality (i.e. QC) or paired reads that were mapped to different chromosomal locations or were too far apart on the same chromosome. Useful for debugging purposes",default=None)
	novo.add_option("-l","--length",dest="length",metavar="100",type="int",help="to set read length threshold. Default = 1000",default=1000)
	novo.add_option("-m","--max",dest="max_reads",metavar="100000",type="int",help="maximum number of mapped reads that will be analyzed. Default = All",default=float("infinity"))
	novo.add_option("--zip", dest="zip", metavar="FILE", help="use this option to compress all the output files in a single zip file", default=None)
	parser.add_option_group(files)
	parser.add_option_group(common)
	parser.add_option_group(novo)
	(options, args) = parser.parse_args()
	status = sys.stdout
	sense  = True
	anti_sense = True
	annotation = None
	if options.verbose:
		status = open("pyReadCounters_log.txt","w")
	if not options.filename: 
		options.filename = sys.stdin
	if options.muts:
		mutslist = re.compile("\[([A-Za-z]+)\]")
		mutstype = mutslist.findall(options.muts)
		if mutstype: options.muts = [i for i in mutstype[0]]		
	if len(sys.argv) < 1:
		parser.error("usage: %prog -f filename --gtf=yourfavgtffile.gtf [options]. Use -h or --help for options\n")	 
	if options.sense and options.anti_sense:
		parser.error("cannot combine the flags --sense and --anti_sense in a command line\n")
	if options.properpairs and options.force_single_end:
		parser.error("cannot combine the flags --force_single_end and --properpairs in a command line\n")
	if options.sense:
		anti_sense = False
	if options.anti_sense:
		sense = False
	if options.annotation:
		annotation = options.annotation

	### setting which output files to print
	gtf_file   = True
	stats_file = True
	hittable   = True
	if options.hittable:
		gtf_file   = False
		stats_file = False
	if options.gtffile:
		hittable   = False
		stats_file = False
	if options.stats:
		hittable = False
		gtf_file = False
	###

	status.write("parsing GTF annotation file...\n")

	### Making GTF2 parser object and parsing GTF annotation file ###
	gtf = GTF2.Parse_GTF()
	gtf.read_GTF(options.annotation_file,ranges=options.range,transcripts=False,source=annotation)
	###
	
	### creating a PyCounters object
	data = PyCounters(options.filename,gtf,file_type=options.file_type,ignorestrand=options.nostrand,debug=options.discarded)
	###
	
	file_types = ["sam","novo","gtf"]
	if options.file_type in file_types[:2]:			# if the file type is a novo or sam file.
		status.write("processing %s file...\n" % options.file_type)
		data = PyCounters(options.filename,gtf,file_type=options.file_type,ignorestrand=options.nostrand,debug=options.discarded)
		status.write("cataloguing read mapping positions...\n")
		data.countReads(align_quality=options.align_quality,align_score=options.align_score,length=options.length,maximum=options.max_reads,force_single_end=options.force_single_end,distance=options.distance,blocks=options.blocks,unique=options.unique,muts_filter=options.muts,properpair=options.properpairs)
	elif options.file_type == file_types[2]:		# if the file type is a gtf file
		status.write("processing GTF data file...\nNOTE!: flags specific for novo or SAM/BAM files will be ignored!\n")
		data = PyCounters(options.filename,gtf,file_type=options.file_type,ignorestrand=options.nostrand,debug=options.discarded)
		data.dataToDict()
	else:
		parser.error("file type %s is not supported. Please choose from 'sam', 'novo' or 'gtf'" % (options.file_type))
		
	### processing the interval data	
	status.write("counting overlap with genomic features...\n")
	if options.nucdensities:
		data.countNucleotideDensities(min_overlap=options.overlap,sense=sense,anti_sense=anti_sense,sequence=options.sequence)
	else:
		data.countGeneHits(min_overlap=options.overlap,sense=sense,anti_sense=anti_sense,sequence=options.sequence)
	###
	
	if options.discarded:
		data.file_list.append(options.discarded)
	if hittable:
		status.write("printing hittable...\n")
		data.printHitTable(out_file=options.output_file,rpkm=options.rpkm)
	if options.file_type in file_types[:2]:
		if stats_file:
			status.write("printing read statistics...\n")
			data.printFileStats(out_file=options.output_file)
		if gtf_file:
			status.write("printing counter results to GTF files...\n")
			#data.printIntronUTROverlapToGTF(min_overlap=options.overlap,out_file=options.output_file)
			data.printCountResultsToGTF(out_file=options.output_file)
	###
	
	### if requested, compress output files
	if options.zip:					
		import zipfile
		status.write("compressing files...\n")
		file = zipfile.ZipFile(options.zip,mode="w",compression=zipfile.ZIP_DEFLATED)
		for files in data.file_list:
			file.write(files)
		file.close()	
		for files in data.file_list:
			try:
				os.remove(files)
			except OSError:
				pass
	###
						
if __name__ == "__main__":
	main()
