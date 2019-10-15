#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.1.1"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyGTF2BedGraph.py
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

import numpy as np
from collections import defaultdict
from optparse import *
from pyCRAC.Parsers.ParseAlignments import ParseCountersOutput
from pyCRAC.Methods import getfilename,processChromFile,steparray2Intervals
from pyCRAC.Classes.NGSFormatWriters import *

def gtf2bedgraph(datafile,chromosomedata,out_files=[],type="reads",permillion=False,fiveend=False,threeend=False,score=False,log=sys.stdout,name=None,description=None,colorbystrand="red,blue"):
	"""Produces a bedgraph output file for hits, substitutions and deletions. It requires, besides data a file containing 
	chromosome names and chromosome lengths. Expects names for two output files in the out_files variable. The first file is assumed to be the output file
	for the plus strand. """
	typechoices = ["reads","substitutions","deletions","startpositions","endpositions"]
	assert type in typechoices, "The option %s is not supported\n" % type
	out = defaultdict()
	if not out_files: 
		out["+"] = NGSFileWriter()
		out["-"] = NGSFileWriter()
	else:
		out["+"] = NGSFileWriter(out_files[0])
		out["-"] = NGSFileWriter(out_files[1])
		
	### writing track line to output files ###
	if name or description:
		if not name: name = "User_Supplied_Track"
		if not description: description = "User_Supplied_Track" 
		for file in out:
			if file == "+": strand = "plus"
			else: strand = "minus"
			new_name = "%s_%s_strand" % (name,strand)
			new_description = "%s_%s_strand" % (description,strand)
			out[file].writeTrackLine("bedGraph",new_name,new_description,colorbystrand) # write trackline information for visualization in the UCSC genome browser
	###
	data = ParseCountersOutput(datafile)
	data.duplicatesremoved = True
	if score:
		data.duplicatesremoved = False
	current_chromosome = str()
	chromdict = defaultdict(list)
	
	### processing the chromosome data
	chromlengthfile = open(chromosomedata,"r").readlines()
	chromdata = processChromFile(chromlengthfile)
	###
	
	normvalue = int()
	
	while True:
		lines = data.readLineByLine()
		if current_chromosome and data.chromosome != current_chromosome or not lines:
			if permillion and not normvalue:
				if not data.mapped_reads:
					sys.stderr.write("No information on the number of mapped reads could be found in the gtf file. Cannot normalize the data\n")
					normvalue = 1.0
				else:
					normvalue = float(data.mapped_reads)/1000000.0 # to normalize the data to per million reads
			else:
				normvalue = 1
			for strand in chromdict:
				start = 0
				for interval in steparray2Intervals(chromdict[strand]):
					if interval[2] != 0:
						start,end,hits = interval
						hits = float(hits)/normvalue
						out[strand].writeBedgraph(current_chromosome,start,end,hits)
			if not lines:
				break
			current_chromosome = str()
			chromdict = defaultdict(list)
			
		if not current_chromosome:
			chromosome_length = chromdata[data.chromosome]
			chromdict["+"] = np.zeros(chromosome_length)
			chromdict["-"] = np.zeros(chromosome_length)
			current_chromosome = data.chromosome
			log.write("Processing chromosome %s...\n" % current_chromosome)

		if type == "reads": 
			chromdict[data.strand][data.read_start:data.read_end] += data.number_of_reads
		elif type == "startpositions":
			if data.strand == "+":
				chromdict[data.strand][data.read_start] += data.number_of_reads
			else:
				chromdict[data.strand][data.read_end-1] += data.number_of_reads
		elif type == "endpositions":
			if data.strand == "-":
				chromdict[data.strand][data.read_start] += data.number_of_reads
			else:
				chromdict[data.strand][data.read_end-1] += data.number_of_reads
		elif type == "substitutions":
			if data.substitutions: chromdict[data.strand][data.substitutions] += data.number_of_reads
		elif type == "deletions":
			if data.deletions: chromdict[data.strand][data.deletions] += data.number_of_reads
		else:
			break

def main(): 
	parser = OptionParser(usage="usage: %prog [options] --gtf=gtf_file.gtf", version="%s" % __version__)
	files = OptionGroup(parser, "File input options")
	files.add_option("--gtf",dest="input_file",metavar="readdata.gtf",help="type the path to the gtf file data file. Be default it expects data from the standard input",default=None)
	files.add_option("-o",dest="output_file",metavar="converted",help="provide a name for an output file. A file extension or strand information is not necessary.",default=None)
	files.add_option("-c", "--chromfile",dest="chromfile",help="Location of the chromosome info file. This file should have two columns: first column is the names of the chromosomes, second column is length of the chromosomes. Default is yeast",metavar="yeast.txt",default=None)
	common = OptionGroup(parser, "bedgraph output options")
	common.add_option("-t","--type",dest="type",choices=["reads","substitutions","deletions","dropoffrates","startpositions","endpositions"],help="this tool can generate bedgraph files for reads, start positions, end positions, substitutions, deletions, reverse transcription drop-off rates (useful for iCLIP data). Please use 'substitutions','deletions','dropoffrates','startpositions','endpositions' to indicate the type of data. Default='reads'",default="reads")
	common.add_option("--count",dest="count",action="store_true",help="Takes the numbers in the 'score' column of the GTF file as the total number of reads for each position. Default is 1 for each interval.",default=False)
	common.add_option("--permillion",dest="permillion",action="store_true",help="To normalize the coverage to reads/cDNAs per million",default=False)
	common.add_option("-v", "--verbose",action="store_true",help="to print status messages to a log file",default=False)		
	ucsc = OptionGroup(parser, "These options can be used to add a track line for the UCSC genome browser")
	ucsc.add_option("-n","--name",dest="name",help="For the USCS track line: provide a track name. Default is none",default=None)
	ucsc.add_option("-d","--description",dest="description",help="For the USCS track line: provide a track description. Default is none",default=None)
	ucsc.add_option("-s","--colorstrands",dest="strands",help="select the colors for each strand. Default = 'red,blue'",default="red,blue")
	parser.add_option_group(files)
	parser.add_option_group(common)
	parser.add_option_group(ucsc)
	(options, args) = parser.parse_args()

	status = sys.stdout
	if options.verbose:
		status = open("pyGTF2bedGraph_log.txt","w")
	out = getfilename(options.input_file)
	if options.output_file:
		out = options.output_file
	file_1 = "%s_plus_strand_%s.bedgraph" % (out,options.type)
	file_2 = "%s_minus_strand_%s.bedgraph" % (out,options.type)
	outputfiles = [file_1,file_2]

	gtf2bedgraph(options.input_file,options.chromfile,out_files=outputfiles,type=options.type,permillion=options.permillion,log=status,score=options.count,name=options.name,description=options.description,colorbystrand=options.strands)
	
if __name__ == "__main__":
	main()