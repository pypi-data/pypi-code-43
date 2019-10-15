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
#	pyClusterReads.py
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
import time
from optparse import *
from collections import defaultdict
from pyCRAC.Parsers import GTF2
from pyCRAC.Methods import numpy_overlap
from pyCRAC.Classes.NGSFormatReaders import NGSFileReader
from pyCRAC.Classes import NGSFormatWriters
from pyCRAC.Classes.Clustering import *

def main(): 
	
	parser = OptionParser(usage="usage: %prog [options] -f filename", version="%s" % __version__)
	files = OptionGroup(parser, "File input options")
	files.add_option("-f", "--input_file", dest="infile",help="provide the path to your GTF read data file. NOTE the file has to be correctly sorted! If you used pyReadCounters to generate the file you should be fine. If you modified it, use the sort command described in the manual to sort your file first by chromosome, then by strand and then by start position.", metavar="reads.gtf",default=None)
	files.add_option("-o", "--output_file", dest="outfile",help="provide a name for an output file. By default it writes to the standard output", metavar="clusters.gtf",default=None)
	files.add_option("--gtf",dest="annotation_file",metavar="Yourfavoritegtf.gtf",help="type the path to the gtf annotation file that you want to use",default=None)
	common = OptionGroup(parser,"Common pyCRAC options")
	common.add_option("-r","--range",dest="range",type="int",metavar="100",help="allows you to set the length of the UTR regions. If you set '-r 50' or '--range=50', then the program will set a fixed length (50 bp) regardless of whether the GTF annotation file has genes with annotated UTRs.",default=0)
	common.add_option("-a","--annotation",dest="annotation",help="select which annotation (i.e. protein_coding, ncRNA, sRNA, rRNA,snoRNA,snRNA, depending on the source of your GTF file) you would like to focus your analysis on. Default = all annotations",metavar="protein_coding",default=None)
	common.add_option("--debug",dest="debug",action="store_true",help=SUPPRESS_HELP,default=False)
	common.add_option("-v", "--verbose",action="store_true",help="to print status messages to a log file",default=False) 
	clusters = OptionGroup(parser, "Options for cluster analysis")
	clusters.add_option("--cic","--cdnasinclusters",dest="cdnasinclusters",metavar="2",type="int",help="sets the minimal number of overlapping cDNAs in each cluster. Default = 2",default=2)
	clusters.add_option("--co","--clusteroverlap", dest="clusteroverlap",metavar="5",action="store",type="int",help="sets the number of nucleotides cDNA sequences have to overlap to form a cluster. Default = 1 nucleotide",default=1)
	clusters.add_option("--ch","--clusterheight", dest="clusterheight",metavar="5",action="store",type="int",help="sets the minimal height of the cluster. Default = 2 nucleotides",default=2)
	clusters.add_option("--cl","--clusterlength", dest="clusterlength",metavar="100",action="store",type="int",help="to set the maximum cluster sequence length. Default = 200 nucleotides",default=200)		 
	clusters.add_option("--mutsfreq","--mutationfrequency",dest="mutsfreq",action="store",type="int",metavar="10",help="sets the minimal mutations frequency for a cluster position in the GTF output file. Default = 0%. Example: if the mutsfrequency is set at 10 and a cluster position has a mutated in less than 10% of the reads, then the mutation will not be reported.",default=0)
	parser.add_option_group(files)
	parser.add_option_group(common)
	parser.add_option_group(clusters)
	(options, args) = parser.parse_args()
	
	outfile = sys.stdout	### default output is standard output
	status	= sys.stdout	### status messages also go to the standard output
	logfile = open("pyClusterReads_log.txt","w")
	if not options.infile:
		parser.error("you forgot to include your GTF read data file\n")
	if options.verbose: status	= logfile
	if not options.outfile:
		status = logfile	# to prevent having status messages and data printed to the standard output.
	else:
		outfile = open(options.outfile,"w")
	if options.clusterlength < 100:
		parser.error("The minimal setting for the maximum cluster length flag is 100 nucleotides. Please change your settings.\n")
	
	list_of_tuples = defaultdict(list)
	
	### Making GTF2 parser object and parsing GTF annotation file ###
	status.write("Parsing GTF annotation data...\n")
	gtf = GTF2.Parse_GTF()
	gtf.read_GTF(options.annotation_file,source=options.annotation,ranges=options.range,transcripts=False)
	###

	### Making a gtf writer object ###
	gtfwriter = NGSFormatWriters.NGSFileWriter(options.outfile)
	headerstring = "##gff-version 2\n# generated by pyClusterReads.py version %s, %s\n# %s\n# chromosome\tfeature\tsource\tstart\tend\tmax_height\tstrand\tframe\tattributes\n" % (__version__,time.ctime(),' '.join(sys.argv))
	gtfwriter.write(headerstring)
	###

	### creating a ReadClustering object ###
	data = ReadClustering(options.infile,logfile)
	###
	
	### Iterating over the read data file ###
	mappedreads	  = 0
	sense_mapped  = 0
	anti_sense_mapped = 0
	overlappingfeats  = 0

	### finding clusters
	status.write("clustering intervals...\n")
	while True:
		iscluster = data.getCluster(min_overlap=options.clusteroverlap,min_cdnas=options.cdnasinclusters,max_length=options.clusterlength,min_height=options.clusterheight,debug=options.debug)
		if iscluster:
			if data.chromosome not in list_of_tuples:
				try:
					list_of_tuples[data.chromosome] = gtf.chromosomeGeneCoordIterator(data.chromosome,numpy=True)
				except AssertionError:
					continue
			search_results = numpy_overlap(list_of_tuples[data.chromosome],data.start,data.end-1,overlap=1)
			mutsstring = data.mutsAnnotationString(min_frequency=options.mutsfreq)
			if search_results:
				gene_name = ",".join(search_results)
				gene_id = ",".join([gtf.gene2orf(gene) for gene in search_results])
				overlappingfeats += len(search_results)
				for gene in search_results:
					if data.strand == gtf.strand(gene):
						sense_mapped += 1
					else:
						anti_sense_mapped += 1
			else:
				gene_name = "no_matches"
				gene_id = "no_matches"
			gtfwriter.writeGTF(data.chromosome,"cluster","interval",data.start,data.end,score=data.cluster_height,strand=data.strand,gene_name=gene_name,gene_id=gene_id,comments=mutsstring)
		else:
			break
	###				
	gtfwriter.write("# total number of intervals analysed:\t%d\n" % data.line_count)
	gtfwriter.write("# total number of clusters generated:\t%d\n" % data.cluster_count)
	gtfwriter.write("# total number of clusters overlapping genomic features:\t%d\n" % (sense_mapped+anti_sense_mapped))
	gtfwriter.write("# \tsense\t%d\n" % sense_mapped)
	gtfwriter.write("# \tanti-sense\t%d\n" % anti_sense_mapped)
	logfile.close()
	
if __name__ == "__main__":
	main()