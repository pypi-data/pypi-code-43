#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.1.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyCalculateMutationFrequencies.py
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
import tempfile
import shutil
import numpy as np
from optparse import *
from collections import defaultdict
from pyCRAC.Classes import NGSFormatWriters
from pyCRAC.Parsers.ParseAlignments import ParseCountersOutput
from pyCRAC.Methods import splitData,processChromFile

def processReadData(datafile,chromosomelength,tempdir="./"):
	""" stores the read data in numpy arrays. """
	data = ParseCountersOutput(datafile)

	chromarray = defaultdict(list)	
	chromarray["+"] = np.zeros((3,chromosomelength),dtype=float)	# one for hits, one for deletions and one for substitutions
	chromarray["-"] = np.zeros((3,chromosomelength),dtype=float)

	while data.readLineByLine():
		chromarray[data.strand][0][data.read_start:data.read_end] += float(data.score)
		if data.substitutions:							# only present in GTF files
			chromarray[data.strand][1][data.substitutions] += float(data.score)
		if data.deletions:
			chromarray[data.strand][2][data.deletions] += float(data.score)
	return chromarray

def mutsAnnotationString(chromarray,strand,start,end,min_frequency=0):
	"""Makes a CIGAR-type string for mutations in reads or clusters"""
	subsstring = str()
	delsstring = str()
	mutlist	   = list()
	subsfreqarray,delsfreqarray = mutsCountsToFrequencies(chromarray,strand,start,end,min_frequency=float(min_frequency))
	for nr in range(len(subsfreqarray)):
		if subsfreqarray[nr]:
			subsstring = "S%.1f" % subsfreqarray[nr]
		if delsfreqarray[nr]:
			delsstring = "D%.1f" % delsfreqarray[nr]
		mutsstring = "%s%s%s" % (start+nr+1,subsstring,delsstring) 
		if subsstring or delsstring:
			mutlist.append(mutsstring)
			subsstring = str()
			delsstring = str()
	if mutlist:
		return ','.join(mutlist)
	else:
		return None

def mutsCountsToFrequencies(chromarray,strand,start,end,min_frequency=0.0):
	""" uses the cluster data to convert mutation numbers to mutation frequencies for each position """
	min_frequency = float(min_frequency)		# set the minimal mutation frequency
	data = chromarray[strand][0][start:end]		# assuming here that 'end' is a 1-based coordinate
	subs = chromarray[strand][1][start:end]
	dels = chromarray[strand][2][start:end]
	subsfreqs = np.ma.fix_invalid(subs*100.0/data,copy=False,fill_value=0.0)	# make an array of substitution frequencies. Remove any NaNs or Infs
	delsfreqs = np.ma.fix_invalid(dels*100.0/data,copy=False,fill_value=0.0)	# make an array of deletion frequencies. Remove any NaNs or Infs
	substitutions = np.where(subsfreqs >= min_frequency,subsfreqs,0.0)			# return all the positions larger than the minimum selected frequency
	deletions	  = np.where(delsfreqs >= min_frequency,delsfreqs,0.0)
	return substitutions,deletions

def main(): 
	parser = OptionParser(usage="usage: %prog [options] -i intervaldata -r readdata", version="%s" % __version__)
	parser.add_option("-i", "--intervaldatafile", dest="intervaldata",help="provide the path to your GTF interval data file.", metavar="intervals.gtf",default=None)
	parser.add_option("-r", "--readdatafile", dest="readdatafile",help="provide the path to your GTF read data file.", metavar="reads.gtf",default=None)
	parser.add_option("-c", "--chromfile",dest="chromfile",help="Location of the chromosome info file. This file should have two columns: first column is the names of the chromosomes, second column is length of the chromosomes.",metavar="yeast.txt",default=None)
	parser.add_option("-o", "--output_file", dest="outfile",help="provide a name for an output file. By default it writes to the standard output", metavar="intervals_with_muts.gtf",default=None)
	parser.add_option("-v", "--verbose",action="store_true",help="to print status messages to a log file",default=False) 
	parser.add_option("--mutsfreq","--mutationfrequency",dest="mutsfreq",action="store",type="int",metavar="10",help="sets the minimal mutations frequency for an interval that you want to have written to our output file. Default = 0%. Example: if the mutsfrequency is set at 10 and an interval position has a mutated in less than 10% of the reads,then the mutation will not be reported.",default=0)
	parser.add_option("--debug",dest="debug",action="store_true",help=SUPPRESS_HELP,default=False)	
	(options, args) = parser.parse_args() 
	outfile = sys.stdout				### default output is standard output
	status	= sys.stdout				### status messages go to the standard output if an output file name has been provided
	logfile = open("pyCalculateMutationFrequencies_log.txt","w")
	if not options.readdatafile:
		parser.error("you forgot to include your GTF read data file")
	if not options.intervaldata:
		parser.error("you forgot to include your GTF interval data file")
	if options.verbose: status	= logfile
	if not options.outfile:
		status = logfile	# to prevent having status messages and data printed to the standard output.
	else:
		outfile = open(options.outfile,"w")
	
	chromlengthfile = open(options.chromfile,"r").readlines()
	chromdict = processChromFile(chromlengthfile)	
	
	### Making a temporary directory ###
	tempdir = tempfile.mkdtemp(prefix="pyCalculateMutationFrequencies_",suffix="_temp",dir="./")
	###
	
	### It is best to split up the data file in temp files, one for each chromosome ### 
	status.write("Creating temporary files for each chromosome in the read data...\n")
	datafiles = splitData(options.readdatafile,tempdir)

	### Making a gtf writer object ###
	gtfwriter = NGSFormatWriters.NGSFileWriter(options.outfile)
	###
		
	### processing the interval data line by line ###
	currentchromosome = str()
	temp = tempfile.NamedTemporaryFile(prefix='intervals',dir=tempdir,suffix='.tmp', delete=False)
	status.write("Sorting interval data...\n")
	os.system("sort -k1,1 -k4,4n %s > %s" % (options.intervaldata,temp.name))
	intervals = ParseCountersOutput(temp.name)
	status.write("Starting analysis...\n")
	while intervals.readLineByLine():
		if intervals.line.startswith("#"): 
			outfile.write(intervals.line)
		chromosome = intervals.chromosome
		if chromosome != currentchromosome:
			status.write("Processing data for chromosome %s...\n" % chromosome)
			file = datafiles[chromosome]
			chromosomelength = chromdict[chromosome]
			chromarray = processReadData(file.name,chromosomelength,tempdir=tempdir)
			currentchromosome = chromosome
		mutsstring = mutsAnnotationString(chromarray,intervals.strand,intervals.read_start,intervals.read_end,min_frequency=options.mutsfreq)
		if mutsstring: 
			outfile.write("%s # %s\n" % (intervals.line.strip(),mutsstring))
		else:
			outfile.write(intervals.line)
	os.unlink(temp.name)
	status.write("Removing remaining temporary files...\n")
	shutil.rmtree(tempdir)	  

if __name__ == "__main__":
	main()