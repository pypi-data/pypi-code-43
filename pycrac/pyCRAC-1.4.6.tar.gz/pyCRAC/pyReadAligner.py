#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.2.3"
__credits__		= ["Sander Granneman", "Shaun Webb"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyReadAligner.py
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
from optparse import *
from pyCRAC.Parsers import GTF2
from pyCRAC.Classes.Aligner import *

def main():
	parser = OptionParser(usage="usage: %prog [options] -f filename -g gene_list", version="%s" % __version__)
	files = OptionGroup(parser,"File input options")
	files.add_option("-f", "--input_file", dest="filename",help="As input files you can use Novoalign native output or SAM files as input file. By default it expects data from the standard input. Make sure to specify the file type of the file you want to have analyzed using the --file_type option!", metavar="FILE",default=None)
	files.add_option("-o", "--output_file", dest="output_file",help="Use this flag to override the standard output file names. All alignments will be written to one output file.",default=None)
	files.add_option("-g", "--genes_file", dest="genes",help="here you need to type in the name of your gene list file (1 column) or the hittable file", metavar="FILE",default=None)
	files.add_option("--chr", dest="chr_coord",help="if you simply would like to align reads against a genomic sequence you should generate a tab delimited file containing an identifyer, chromosome name, start position, end position and strand ('-' or '+')", metavar="FILE",default=None)
	files.add_option("--gtf",dest="annotation_file",metavar="annotation_file.gtf",help="type the path to the gtf annotation file that you want to use",default=None)
	files.add_option("--tab",dest="tab_file",metavar="tab_file.tab",help="type the path to the tab file that contains the genomic reference sequence",default=None)
	files.add_option("--file_type",dest="file_type",choices=["novo","sam","gtf"],help="use this option to specify the file type (i.e. 'novo', 'sam', 'gtf'). This will tell the program which parsers to use for processing the files. Default = 'novo'",default="novo")
	specific = OptionGroup(parser,"pyReadAligner specific options")
	specific.add_option("--limit",dest="limit",metavar="500",type="int",help="with this option you can select how many reads mapped to a particular gene/ORF/region you want to count. Default = All",default=-1)
	common = OptionGroup(parser, "Common options")
	common.add_option("-v","--verbose",dest="verbose",action="store_true",help="prints all the status messages to a file rather than the standard output",default=False)
	common.add_option("--ignorestrand",dest="nostrand",action="store_true",help="this flag tells the program to ignore strand information and all overlapping reads will considered sense reads. Useful for analysing ChIP or RIP data",default=False)
	common.add_option("--zip", dest="zip", metavar="FILE", help="use this option to compress all the output files in a single zip file", default=None)
	common.add_option("--overlap",dest="overlap",help="sets the number of nucleotides a read has to overlap with a gene before it is considered a hit. Default =  1 nucleotide",type="int",metavar="1",default="1")
	common.add_option("-s","--sequence",dest="sequence",metavar="genomic",help="with this option you can select whether you want the reads aligned to the genomic or the coding sequence. Default = genomic",default="genomic")
	common.add_option("-r","--range",dest="range",type="int",metavar="100",help="allows you to set the length of the UTR regions. If you set '-r 50' or '--range=50', then the program will set a fixed length (50 bp) regardless of whether the GTF file has genes with annotated UTRs.",default=False)
	novo = OptionGroup(parser, "Options for novo, SAM and BAM files")
	novo.add_option("--align_quality", "--mapping_quality", dest="align_quality", metavar="100", type="int", help="with these options you can set the alignment quality (Novoalign) or mapping quality (SAM) threshold. Reads with qualities lower than the threshold will be ignored. Default = 0", default=0)
	novo.add_option("--align_score", dest="align_score", metavar="100", type="int", help="with this option you can set the alignment score threshold. Reads with alignment scores lower than the threshold will be ignored. Default = 0", default=0)
	novo.add_option("-l","--length",dest="length",metavar="100",type="int",help="to set read length threshold. Default = 1000",default=1000)
	novo.add_option("-m","--max",dest="max_reads",metavar="100000",type="int",help="maximum number of mapped reads that will be analyzed. Default = All",default=float("infinity"))
	novo.add_option("--unique",dest="unique",action="store_true",help="with this option reads with multiple alignment locations will be removed. Default = Off",default=False)		
	novo.add_option("--blocks",dest="blocks",action="store_true",help="with this option reads with the same start and end coordinates on a chromosome will only be counted once. Default = Off",default=False)
	novo.add_option("--discarded",dest="discarded",metavar="FILE", help="prints the lines from the alignments file that were discarded by the parsers. This file contains reads that were unmapped (NM), of poor quality (i.e. QC) or paired reads that were mapped to different chromosomal locations or were too far apart on the same chromosome. Useful for debugging purposes",default=None)
	novo.add_option("-d","--distance",dest="distance",metavar="1000",type="int",help="this option allows you to set the maximum number of base-pairs allowed between two non-overlapping paired reads. Default = 1000",default=1000)
	novo.add_option("--mutations",dest="muts",metavar="delsonly",help="Use this option to only track mutations that are of interest. For CRAC data this is usually deletions (--mutations=delsonly). For PAR-CLIP data this is usually T-C mutations (--mutations=TC). Other options are: do not report any mutations: --mutations=nomuts. Only report specific base mutations, for example only in T's, C's and G's :--mutations=[TCG]. The brackets are essential. Other nucleotide combinations are also possible",default=None)
	parser.add_option_group(files)
	parser.add_option_group(specific)
	parser.add_option_group(common)
	parser.add_option_group(novo)
	(options, args) = parser.parse_args()
	status = sys.stdout
	if options.verbose:
		status = open("pyReadAligner_log.txt","w")
	if not options.filename:
		options.filename = sys.stdin
	if options.muts:
		mutslist = re.compile("\[([A-Za-z]+)\]")
		mutstype = mutslist.findall(options.muts)
		if mutstype: options.muts = [i for i in mutstype[0]]
	if len(sys.argv) < 2:
		parser.error("usage: %prog [options] -f filename -g genes_list. Use -h or --help for options\n")
	if options.genes is None and options.chr_coord is None:
		parser.error("you forgot to input your genes list, hittable file or chromosome coordinate file. Use -g, --genes or --chr options\n")
	if options.tab_file is None:	
		parser.error("you forgot to input the tab file containing the genomic references sequence. Use --tab=yourfavoritetab.tab option\n")
	if options.filename:
		status.write("processing %s data...\n" % options.file_type)
	
	genes = list()
	
	### Making GTF2 parser object and parsing GTF annotation file ###
	gtf = GTF2.Parse_GTF()
	###
	
	### processing list of genes or chromosome coordinate files:
	if options.genes:
		status.write("parsing GTF reference file...\n")
		genes = [line.strip() for line in open(options.genes,"r").readlines()]
		gtf.read_GTF(options.annotation_file,ranges=options.range,genes=genes,transcripts=True)
	
	elif options.chr_coord:
		status.write("processing chromosomal coordinates file...\n")
		for coord in open(options.chr_coord,"r").readlines():
			gene,chromosome,start,end,strand =	coord.strip().split()
			start = int(start)
			end	  = int(end)
			genes.append(gene)
			gtf.addGene(gene,start,end,"exon",None,chromosome,strand)
	###
	
	### storing chromosomes into memory:
	chromosomes = [gtf.chromosome(gene) for gene in genes]
	status.write("storing relevant reference sequences into memory...\n")
	gtf.read_TAB(options.tab_file,chromosomes)	# only the chromosomes that are required are stored into memory.
	###
		 
	### creating a ReadAligner object:	 
	solexadata = ReadAligner(options.filename,gtf,genes,file_type=options.file_type,sequence=options.sequence,blocks=options.blocks,debug=options.discarded)
	###
	
	### Aligning the reads:
	solexadata.alignReads(length=options.length,align_quality=options.align_quality,align_score=options.align_score,MAX=options.max_reads,limit=options.limit,unique=options.unique,muts_filter=options.muts)
	###
	
	### if no sense or anti-sense reads were mapped to any of our genes, report this to the log or standard output
	nosensehits		= list()
	noantisensehits = list()
	for gene in genes:
		if gene not in solexadata.sense_seqs:
			nosensehits.append(gene)
		if gene not in solexadata.anti_sense_seqs:
			noantisensehits.append(gene)
	if nosensehits	  : status.write("Could not find any sequences overlapping 'sense' with genes %s...\n" % (','.join(nosensehits)))
	if noantisensehits: status.write("Could not find any sequences overlapping 'anti-sense' with genes %s...\n" % (','.join(noantisensehits)))
	###
	
	status.write("printing output files...\n")
	solexadata.printFastaWithAlignments(out_file=options.output_file)
	
	### compressing output files, if requested.
	if options.zip:					
		import zipfile
		status.write("compressing files...\n")
		file = zipfile.ZipFile(options.zip,mode="w",compression=zipfile.ZIP_DEFLATED)
		for files in solexadata.file_list:
			file.write(files)
		file.close()	
		for files in solexadata.file_list:
			try:
				os.remove(files)
			except OSError:
				pass	
	###
		
if __name__ == "__main__":
	main()