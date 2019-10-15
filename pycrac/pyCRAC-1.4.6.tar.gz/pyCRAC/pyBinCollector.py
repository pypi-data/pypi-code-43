#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.5.7"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyBinCollector.py
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

import os
import sys
import time
import tempfile
import shutil
import numpy as np
from pyCRAC.Classes.Coverage import BinCollector
from pyCRAC.Parsers import GTF2
from pyCRAC.Methods import splitData,getfilename,sortbylistlength
from optparse import *
from collections import defaultdict
							
def main():
	parser = OptionParser(usage="usage: %prog [options] -f filename --gtf=yeast.gtf -n 100 -r 50 --outputall --normalize", version="%s" % __version__)
	files = OptionGroup(parser, "File input options")
	files.add_option("-f", "--input_file", dest="input_file",help="Provide the path and name of the pyClusterReads, pyReadCounters or pyMotif GTF output file. By default the program expects data from the standard input.", metavar="FILE")
	files.add_option("-o","--output_file",dest="output_file",help="To set an output file name. Do not add a file extension. By default, if the --outputall flag is not used, the program writes to the standard output.",default=None)
	files.add_option("--gtf",dest="annotation_file",metavar="yeast.gtf",help="type the path to the gtf annotation file that you want to use.")
	common = OptionGroup(parser, "Common pyCRAC options")
	common.add_option("-r","--range",dest="range",type="int",metavar="100",help="allows you to set the length of the UTR regions. If you set '-r 50' or '--range=50', then the program will set a fixed length (50 bp) regardless of whether the GTF file has genes with annotated UTRs.",default=0)
	common.add_option("-s","--sequence",dest="sequence",metavar="intron",choices=["intron","coding","genomic","CDS","exon","5UTR","3UTR","5ss","3ss","TSS","5end","3end","CDSstart","CDSend"],help="with this option you can select whether you want to generate bins from the coding or genomic sequence or intron, exon, CDS, UTR, 5ss, 3ss, TSS, 5end, 3end, CDSstart or CDSend coordinates. Default = genomic.",default="genomic")
	common.add_option("--ignorestrand",dest="nostrand",action="store_true",help="To ignore strand information and all reads overlapping with genomic features will be considered sense reads. Useful for analysing ChIP or RIP data.",default=False)
	common.add_option("-v","--verbose",dest="verbose",action="store_true",help="prints all the status messages to a file rather than the standard output.",default=False)
	common.add_option("-a","--annotation",dest="annotation",help="select an annotation (i.e. protein_coding, ncRNA, sRNA, rRNA, tRNA, snoRNA) you would like to focus your search on. Default = all.", metavar="protein_coding",default=None)
	common.add_option("--readoverlap",dest="readoverlap",type="int",metavar="1",help="the minimum number of nucleotides a read has to overlap with a feature to be considered a hit. Default is one nucleotide.",default=1)
	specific = OptionGroup(parser, "pyBinCollector specific options")
	specific.add_option("--anti_sense",dest="anti_sense",action="store_true",help="by default pyBinCollector only looks at intervals that overlap 'sense' with features. Use this flag if you only want to plot intervals that map anti-sense.",default=False)
	specific.add_option("--deletions",dest="deletions",action="store_true",help="By default pyBinCollector only looks at interval coordinates. Use this flag to make distribution plots of deletions over genomic features.",default=False)
	specific.add_option("--substitutions",dest="substitutions",action="store_true",help="By default pyBinCollector only looks at interval coordinates. Use this flag to make distribution plots of substitutions over genomic features.",default=False)	
	specific.add_option("--min_length",dest="min_length",metavar="20",type="int",help="to set a minimum length threshold for genes. Genes shorter than the minimal length will be discarded. Default = 1.", default=1)
	specific.add_option("--max_length",dest="max_length",metavar="10000",type="int",help="to set a maximum length threshold for genes. Genes larger than the maximum length will be discarded. Default = 100000000.", default=100000000)
	specific.add_option("-n","--numberofbins",dest="numberofbins",help="Use this flag if you want to normalize feature lengths by dividing them in an equal number fo bins. Default is None.",metavar="100",type="int", default=0)
	specific.add_option("--binoverlap",dest="binoverlap",nargs=2,type="int",metavar="2 4",help="Allows you to print out intervals that were allocated to specific bins. This option expects two numbers, one for each bin, separated by a space. For example: --binoverlap 20 30.", default=[])
	specific.add_option("--overlap",dest="overlap",action="store_true",help="bedtool-like function. Allows you to print out overlap between intervals and specific features such as 5UTR,3UTR,exons, etc without binning.", default=False)
	specific.add_option("--outputall",dest="outputall",action="store_true",help="use this flag to output the interval distribution for each individual gene, rather than making a cumulative coverage plot. Useful for making box plots or for making heat maps.", default=False)
	specific.add_option("--normalize",dest="normalize",action="store_true",help="calculates nucleotide density frequencies for each bin for each feature by dividing the value in each bin by the total read density for the feature.", default=False)
	specific.add_option("--unique",dest="unique",action="store_true",help="To only count an interval in the data gtf file once. Essentially ignores the number in column 5 of the pyCRAC gtf files.", default=False)
	parser.add_option_group(files)
	parser.add_option_group(common)
	parser.add_option_group(specific)
	(options, args) = parser.parse_args()
	status = sys.stdout
	orientation = "sense"
	feature = "intervals"
	if options.anti_sense:
		orientation = "anti_sense"
	if options.deletions:
		feature = "deletions"
	if options.substitutions:
		feature = "substitutions"
	output = None
	if options.outputall and options.binoverlap:
		parser.error("cannot combine --outputall and --binoverlap flags\n")
	if options.overlap and options.binoverlap:
		parser.error("cannot combine --overlap and --binoverlap flags\n")
	if options.verbose or not options.output_file:
		status = open("pyBinCollector_log.txt","w")
	if len(sys.argv) < 1:
		parser.error("usage: %prog [options] -f filename -g gene_list. Use -h or --help for options\n")
	binoverlapion = []
	if not options.input_file:
		parser.error("you forgot to include a data file\n")
	if options.output_file:
		output = options.output_file
	if options.binoverlap: binoverlapion = [options.binoverlap[0]-1,options.binoverlap[1]]

	### Making GTF2 parser object and parsing GTF annotation file ###
	status.write("Parsing GTF annotation file...\n")
	gtf = GTF2.Parse_GTF()
	gtf.read_GTF(options.annotation_file,source=options.annotation,transcripts=False)
	###
	
	status.write("Collecting data...\n")

	if options.overlap:
		data = BinCollector()
		data.annotation = options.annotation
		data.findOverlap(options.input_file,gtf,sequence=options.sequence,minfeatlength=options.min_length,maxfeatlength=options.max_length,orientation=orientation,ignorestrand=options.nostrand,out_file=output,ranges=options.range,overlap=options.readoverlap)
	elif options.binoverlap:
		data = BinCollector()
		data.annotation = options.annotation
		data.numberofbins = options.numberofbins
		status.write("Looking for intervals that overlap with bins %s to %s...\n" % (binoverlapion[0]+1,binoverlapion[-1]))
		data.findBinOverlap(options.input_file,gtf,ignorestrand=options.nostrand,sequence=options.sequence,minfeatlength=options.min_length,maxfeatlength=options.max_length,orientation=orientation,out_file=output,printbins=binoverlapion,ranges=options.range,overlap=options.readoverlap)
	elif options.outputall:
		outputfiles = list()
		if options.output_file:
			outfile = open(options.output_file,"w")
		else:
			outfile = open("%s_%s_%s.%s" % (orientation,feature,getfilename(options.input_file),"txt"),"w")
		tempdir = tempfile.mkdtemp(prefix="pyBinCollector_",suffix="_temp",dir="./")
		tempfiles = list()
		status.write("Creating temporary files for each chromosome in the read data...\n")
		datafiles = splitData(options.input_file,tempdir)
		for chromosome in sorted(datafiles):
			status.write("Processing data for chromosome %s...\n" % chromosome)
			temp = tempfile.NamedTemporaryFile(prefix='%s_table' % chromosome,dir=tempdir,suffix='.tmp', delete=False)
			file = datafiles[chromosome]
			table = open(file.name,"r")
			tempfiles.extend([temp,file])
			outputfiles.append(temp.name)
			data = BinCollector()
			data.annotation = options.annotation
			data.numberofbins = options.numberofbins			
			data.countFeatureDensities(table,gtf,sequence=options.sequence,ignorestrand=options.nostrand,minfeatlength=options.min_length,maxfeatlength=options.max_length,feature=feature,orientation=orientation,ranges=options.range,overlap=options.readoverlap,unique=options.unique)
			if data.dataarray:
				if data.numberofbins:
					data.binFeatureDensities(numberofbins=data.numberofbins)
				try:	
					data.printBinCountingResults(out_file=temp.name,normalize=options.normalize)
				except AssertionError:
					status.write("...No data for chromosome %s\n" % chromosome)
			table.close()
		status.write("Merging output files...\n")
		alldata = defaultdict(list)
		for file in outputfiles:
			table = open(file,"r")
			for line in table:
				Fld = line.strip().split()
				gene_name = Fld[0]
				alldata[gene_name] = Fld[1:]
			table.close()
		sortedbylength = sortbylistlength(alldata)
		longestgenelength = sortedbylength[0][1]
		outfile.write("%s\n" % ("\t".join([str(i) for i in range(1,longestgenelength+1)])))
		for gene,length in sortedbylength:
			outfile.write("%s\t%s\n" % (gene,"\t".join([str(i) for i in alldata[gene]])))
		outfile.close()
		status.write("Removing temporary files...\n")
		for i in tempfiles:
			os.unlink(i.name)
		shutil.rmtree(tempdir)		
	else:
		outputfiles = list()
		data = BinCollector()
		data.annotation = options.annotation
		data.numberofbins = options.numberofbins
		if options.output_file:
			outfile = open(options.output_file,"w")
		else:
			outfile = open("%s_%s_%s.%s" % (orientation,feature,getfilename(options.input_file),"txt"),"w")
		status.write("Creating temporary files for each chromosome in the read data...\n")
		tempdir = tempfile.mkdtemp(prefix="pyBinCollector_",suffix="_temp",dir="./")
		datafiles = splitData(options.input_file,tempdir)
		status.write("Calculating cumulative bin densities...\n")	
		tempfiles = list()
		for chromosome in sorted(datafiles):
			data.dataarray = defaultdict(list)
			status.write("Processing data for chromosome %s...\n" % chromosome)
			file  = datafiles[chromosome]
			table = open(file.name,"r")
			tempfiles.append(file)
			data.countFeatureDensities(table,gtf,sequence=options.sequence,ignorestrand=options.nostrand,minfeatlength=options.min_length,maxfeatlength=options.max_length,feature=feature,orientation=orientation,ranges=options.range,overlap=options.readoverlap,unique=options.unique)
			if data.dataarray:
				temp = tempfile.NamedTemporaryFile(prefix='%s_table' % chromosome,dir=tempdir,suffix='.tmp',delete=False)
				tempfiles.append(temp)
				outputfiles.append(temp.name)
				data.binFeatureDensities(numberofbins=data.numberofbins)
				try:
					data.printBinCountingResults(out_file=temp.name,normalize=options.normalize,cumulative=True)
				except AssertionError:
					status.write("...No data for chromosome %s\n" % chromosome)
			table.close()
		cumulativedata = np.zeros(data.numberofbins)
		status.write("Printing results to output file...\n")
		for file in outputfiles:
			cumulativedata += np.loadtxt(file,delimiter="\t",dtype=float)
		outfile.write("# generated by BinCollector, %s\n# %s\n" % (time.ctime(),' '.join(sys.argv)))
		outfile.write("# bin\thits_or_fraction\n")
		for i in range(data.numberofbins):
			outfile.write("%s\t%s\n" % (i+1,cumulativedata[i]))
		outfile.close()
		status.write("Removing temporary files...\n")
		try:
			for i in tempfiles:
				os.unlink(i.name)
			shutil.rmtree(tempdir)
		except:
			status.write("\nERROR! Could not delete the temporary files because of permission issues, please do this manually\n")

	status.write("DONE!\n")
	
if __name__ == "__main__":
	main()