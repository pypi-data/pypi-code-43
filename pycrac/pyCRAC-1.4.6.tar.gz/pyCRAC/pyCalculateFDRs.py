#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.9"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyCalculateFDRs.py
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
import os
import time
import shutil
from optparse import *
from pyCRAC.Classes.NGSFormatWriters import NGSFileWriter
from pyCRAC.Classes.FDR import *
from pyCRAC.Parsers import GTF2
from pyCRAC.Methods import splitData,processChromFile,contigousarray2Intervals,getfilename

def main():
	parser = OptionParser(usage="usage: %prog [options] -f readdatafile --gtf=GTF_annotation_file -o output_file.gtf",version="%s" % __version__)
	parser.add_option("-f", "--readdatafile", dest="readdatafile",help="Name of the bed/gff/gtf file containing the experiment read/cDNA coordinates", metavar="experiment_file",default=None)
	parser.add_option("--control", dest="controldatafile",help="Name of the bed/gff/gtf file containing the control read/cDNA coordinates",metavar="control_file",default=None) # help = Name of the bed/gff/gtf file containing the control data read/cDNA coordinates. If no control data is provided, the reads from the experimental data will be randomely shuffled over genomic features
	parser.add_option("--file_type",dest="file_type",choices=["bed","gtf","gff"],help="this tool supports bed6, gtf and gff input files. Please select from 'bed','gtf' or 'gff'. Default=gtf",default="gtf")	
	parser.add_option("-o", "--outfile",dest="outfile",help="Optional. Provide the name of the output file. Default is 'selected_intervals.gtf'",metavar="outfile.gtf",default="interval_FDRs.gtf")
	parser.add_option("-r","--range",dest="range",type="int",metavar="100",help="allows you to set the length of the UTR regions. If you set '-r 50' or '--range=50', then the program will set a fixed length (50 bp) regardless of whether the GTF file has genes with annotated UTRs.",default=False)
	parser.add_option("-a","--annotation",dest="annotation",help="select which annotation (i.e. protein_coding, ncRNA, sRNA, rRNA,snoRNA,snRNA, depending on the source of your GTF file) you would like to focus your analysis on. Default = all annotations",metavar="protein_coding",default=None)
	parser.add_option("-s","--sequence",dest="sequence",choices=["genomic","coding"],metavar="genomic",help="use 'coding' if you suspect your protein only binds to spliced mRNAs. Default = genomic",default="genomic")
	parser.add_option("-c", "--chromfile",dest="chromfile",help="Location of the chromosome info file. This file should have two columns: first column is the names of the chromosomes, second column is length of the chromosomes. Default is yeast",metavar="yeast.txt",default=None)
	parser.add_option("--gtf",dest="annotation_file",help="Name of the annotation file. Default is %s" % None, metavar="yeast.gtf",default=None)
	parser.add_option("-v", "--verbose",action="store_true",help="to print status messages to a log file",default=False) 
	parser.add_option("-m","--minfdr",dest="minfdr",type="float",help="To set a minimal FDR threshold for filtering interval data. Default is 0.05",default=0.05)
	parser.add_option("--min",dest="min",help="to set a minimal read coverages for a region. Regions with coverage less than minimum will be ignoredve an FDR of zero",type="int",default=1)
	parser.add_option("--iterations",dest="iterations",type="int",help="to set the number of iterations for randomization of read coordinates. Default=100",default=100)
	parser.add_option("--debug",dest="debug",action="store_true",help=SUPPRESS_HELP,default=False)
	parser.add_option("--todisk",dest="todisk",action="store_true",help=SUPPRESS_HELP,default=False)
	parser.add_option("--featlengthlimit",dest="featlength",type="int",help=SUPPRESS_HELP,default=5000000)
	(options, args) = parser.parse_args()
	debug	= options.debug
	status	= sys.stdout
	if options.verbose: status = open("pyCalculateFDRs_log.txt","w")
	
	### Making GTF2 parser object and parsing GTF annotation file ###
	status.write("Parsing GTF annotation data...\n")
	gtf = GTF2.Parse_GTF()
	gtf.read_GTF(options.annotation_file,ranges=options.range,source=options.annotation,transcripts=False)
	###
	
	list_of_tuples = defaultdict(list)
	experimentdataarray = defaultdict(list)
	controldataarray	= defaultdict(list)
	
	### Creating outfile, logfile and outfile GTF writer object ###
	outfile = NGSFileWriter(options.outfile)
	logfile = open("%s_features_FDR_data.txt" % getfilename(options.outfile),"w")
	###
	
	### Making a temporary directory
	tempdir = tempfile.mkdtemp(prefix="pyCalculateFDRs_",suffix="_temp",dir="./")
	controltempdir = None
	
	###

	### It is best to split up the data file in temp files, one for each chromosome ###
	status.write("Creating temporary files for each chromosome...\n")
	status.write("Processing the experimental data...\n")
	datafiles = splitData(options.readdatafile,tempdir)
	
	### if there is a control dataset, do the same:
	
	if options.controldatafile:
		status.write("Processing the control data...\n")
		controltempdir = tempfile.mkdtemp(prefix="pyCalculateFDRs_",suffix="_temp",dir="./")
		controlfiles   = splitData(options.controldatafile,controltempdir)
	
	###
	
	### Creating a ModFDR object ###
	fdr = ModFDR(iterations=options.iterations,mincoverage=options.min,debug=options.debug,minfdr=options.minfdr)
	###
	
	chromlengthfile = open(options.chromfile,"r").readlines()
	chromdict = processChromFile(chromlengthfile)	
	
	### Making a gtf writer object ###
	gffversionstring = "##gff-version 2\n"
	headerstring = "# generated by pyCalculateFDRs version %s, %s\n# %s\n" % (__version__,time.ctime(),' '.join(sys.argv))
	gtfstring	 = "# chromosome\tfeature\tsource\tstart\tend\tminimal_coverage\tstrand\t.\tattributes\n"
	outfile.write("%s%s%s" % (gffversionstring,headerstring,gtfstring))
	logfile.write(headerstring)

	### iterating through the chromosome data files
	for chromosome in sorted(datafiles):
		status.write("Processing data for chromosome %s...\n" % chromosome)
		try:
			chromosomelength = chromdict[chromosome]
			chromosomelength += (2* options.range)	   # otherwise the program would throw an index error for genes close to the edges of the chromosome
		except KeyError:
			sys.stderr.write("\nWARNING! Could not find chromosome %s in the chromosome info file. Please double check if the chromosome names of the chromosome info file and read GTF file match\n\n")
			continue
		file = datafiles[chromosome]
		experimentdataarray,genecoverageinfo = fdr.processReadData(gtf,file.name,chromosomelength,todisk=options.todisk,tempdirectory=tempdir)	# doing this one chromosome at a time significantly reduces memory usage. The datafile does not have to be sorted.
		if options.controldatafile:
			if chromosome in controlfiles:
				file = controlfiles[chromosome]
				controldataarray,controlcoverageinfo = fdr.processReadData(gtf,file.name,chromosomelength,todisk=options.todisk,tempdirectory=controltempdir)
			else:
				controldataarray["+"] = np.zeros(chromosomelength)
				controldataarray["-"] = np.zeros(chromosomelength)
		logfile.write("\n####### chromosome %s #######\n" % chromosome)
		for gene in genecoverageinfo:
			itercoordinates = gtf.geneIterCoordinates(gene,coordinates=options.sequence)
			strand = gtf.strand(gene)
			gene_length = len(itercoordinates)
			if gene_length > options.featlength:
				sys.stderr.write("\tgene %s is longer than the %s nucleotide feature limit and will be ignored\n" % (gene,options.featlength))
				continue
			actualdata = experimentdataarray[strand][itercoordinates]
			start = itercoordinates[0]
			if actualdata.any():
				if options.controldatafile:
					controldata	  = controldataarray[strand][itercoordinates]
					signifregions = fdr.findSignificantRegions(actualdata,controldata,randomised=False)
				else:
					shuffleddata  = fdr.shuffleReadPositions(gene_length,genecoverageinfo[gene])
					signifregions = fdr.findSignificantRegions(actualdata,shuffleddata)
					
				if signifregions.any():		# if there are any significant regions...
					logfile.write("\n# %s\nheight\tFDR\texperimental_data_hits\tcontrol_data_hits\n" % gene)
					fdr.writeFDRData(logfile)
					for coord in contigousarray2Intervals(signifregions):
						outfile.writeGTF(chromosome,"cluster","interval",start+coord[0],start+coord[1]+1,score=fdr.coverage,strand=gtf.strand(gene),frame=".",gene_name=gene,gene_id=gtf.gene2orf(gene),comments=None)
		if options.todisk:
			for i in chromarray["files"]:
				os.unlink(i.name)
		os.unlink(file.name)	# delete the temporary file
	status.write("Removing remaining temporary files...\n")
	try:
		shutil.rmtree(tempdir)
		if controltempdir:
			shutil.rmtree(controltempdir)
	except:
		status.write("\nERROR! Could not delete the temporary files because of permission issues, please do this manually\n")
		
if __name__ == "__main__":
	main()