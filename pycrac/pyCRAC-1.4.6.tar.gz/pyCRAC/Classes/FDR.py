#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.7"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	FDR.py
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

import numpy as np
import tempfile
from pyCRAC.Methods import numpy_overlap
from pyCRAC.Classes.NGSFormatReaders import NGSFileReader
from collections import defaultdict

class ModFDR():
	""" class for calculating False Discovery Rates (FDRs) for NGS data intervals. Inspired by Pyicos
	(http://regulatorygenomics.upf.edu/group/media/pyicos_docs/index.html) but implemented using numpy
	allowing fast numerical calculations on large arrays """
	def __init__(self,iterations=100,mincoverage=1,debug=False,minfdr=0.05):
		limit = 1000
		assert iterations <=limit, "To preserve memory the iteration maximum is set to %s\n" % limit
		self.iterations	  = iterations
		self.mincoverage  = mincoverage
		self.debug		  = debug
		self.minfdr		  = minfdr
		self.FDR		  = float()
		self.FDR_counter  = defaultdict(lambda: defaultdict(list))
		self.coverage	  = int()
		
	def writeFDRData(self,log):
		""" writes coverage and FDR information to a log file. Useful for debugging purposes.
		Resets the FDR_counter dict when finished. """
		assert self.FDR_counter, "No data to be reported\n"
		for fdr in sorted(self.FDR_counter["FDR"]):
			if len(self.FDR_counter["FDR"][fdr]) > 1:
				coverage = min(self.FDR_counter["FDR"][fdr])
				actual	 = sum([self.FDR_counter["actual_coverage"][i] for i in self.FDR_counter["FDR"][fdr]])
				control	 = sum([self.FDR_counter["control_coverage"][i] for i in self.FDR_counter["FDR"][fdr]])
				log.write(">=%s\t%s\t%s\t%s\n" % (coverage,fdr,actual,control))
			else:
				coverage = self.FDR_counter["FDR"][fdr][0]
				actual	 = self.FDR_counter["actual_coverage"][coverage]
				control	 = self.FDR_counter["control_coverage"][coverage]
				log.write("%s\t%s\t%s\t%s\n" % (coverage,fdr,actual,control))
		
	def findSignificantRegions(self,actual,control,randomised=True):
		""" calculates False discovery rates (FDRs) for a region (i.e. gene positions) by comparing the experimental data to randomised data. 
		It then masks regions within the actual data that fall below the set minimal FDR.
		If you provide an array with negative control data, then you have to set the 'randomised' variable to 'False'.
		Requires two numpy arrays with experimental data and one numpy array with randomized or control data. The randomised
		data should be a matrix in which each row represents the randomized coverage for each iteration.
		Returns the results as a dictionary in which each keys are heights and the values are FDRs """
		self.FDR_counter = defaultdict(lambda: defaultdict(list))	# the counter is reset every time to preserve memory
		region_length = float(len(actual))
		max_coverage  = int(actual.max())
		if max_coverage >= self.mincoverage:
			for height in reversed(list(range(1,max_coverage+1))):
				p_actual = (actual >= height).sum(dtype=float)/region_length			# what is the probability of coverage 'height' in the actual data?		
				self.FDR_counter["actual_coverage"][height] = (actual >= height).sum()	# stores occurrences of height in actual data		
				if randomised:															# if the data is randomised read positions, calculate the probabilities and standard deviations for the randomised data
					p_rand = (control >= height).sum(axis=1,dtype=float)/region_length	# what is the probability of coverage 'height' in each of the random iterations?
					if not p_rand.any():												# if p_rand is zero then there is no point in calculating FDRs...
						self.FDR = 0.0
					else:
						p_rand_mean = p_rand.mean(dtype=float)							# mean of the random probabilities for coverage 'height'
						p_rand_std	= p_rand.std(dtype=float)							# standard deviation of the random probabilities for coverage 'height'
						self.FDR	= p_rand_mean + p_rand_std / p_actual
					self.FDR_counter["control_coverage"][height] = (control >= height).sum()/float(self.iterations) # stores occurrences of height in randomized data

				else:																	# if the data is generated from a negative control dataset, calculate the probability using the control data
					p_control = (control >= height).sum(dtype=float)/region_length		# what is the probability of coverage 'height' in the control data?
					if not p_control.any(): 											# if p_control is zero then there is no point in calculating FDRs...
						self.FDR = 0.0
					else:
						self.FDR  = p_control / p_actual	
					self.FDR_counter["control_coverage"][height] = (control >= height).sum()	# stores occurrences of height in control data			
				self.FDR_counter["FDR"][self.FDR].append(height)						# stores FDR value for each height
				if self.FDR >= self.minfdr and height + 1 >= self.mincoverage:
					self.coverage = height+1
					return np.where(actual >= self.coverage)[0]
					
		return np.zeros(1)	# If the coverage is below the mincoverage threshold or it could not find significant regions it returns an empty numpy list
					
	def shuffleReadPositions(self,regionlength,regionreadinfo):
		""" generates a matrix with shape genelength by number of iterations and randomizes read positions (regionreadinfo dict) over each row.
		Returns the matrix with randomized data. The regionreadinfo dictionary should have information about the number of reads that have a particular read length.
		for example regionreadinfo[10] = 5 indicates that the region has 5 reads of read length 10. This information is required for shuffling the read positions over the region of interest. """
		randarray = np.zeros(shape=(self.iterations,regionlength))						# make a matrix with a number of rows, dictated by number_of_iterations
		for readlength in regionreadinfo:												# genereadinfo[readlengths] = 5
			for i in range(regionreadinfo[readlength]):
				random_numbers = np.random.randint(-readlength+1,regionlength,self.iterations)	# generate random numbers for each row as starting positions. I wonder if a better distribution (other than the normal distribution) can be used here
				for j in range(self.iterations):
					if random_numbers[j] < 0: 
						randarray[j][:random_numbers[j]+readlength] += 1
					else:
						randarray[j][random_numbers[j]:random_numbers[j]+readlength] += 1
						
		return randarray
		
	def processReadData(self,gtf,datafile,chromosomelength,type="gtf",todisk=False,ignorestrand=False,tempdirectory="./"):
		""" processes read data from a single chromosome and calculates for each position overlapping sense with a genomic feature using numpy arrays.
		Requires a GTF2.Parse_GTF instance loaded with GTF annotations. Supports bed6, gtf and gff as input files."""
		typechoices = ["bed","gtf","gff"]
		data = NGSFileReader(datafile)
		functions = [data.readBedLine,data.readGTFLine,data.readGFFLine]
		reader = functions[typechoices.index(type)]
		chromarray = defaultdict(list)
		chromarray["+"] = np.zeros(chromosomelength)
		chromarray["-"] = np.zeros(chromosomelength)
		list_of_tuples = defaultdict(list)
		genecoverageinfo = defaultdict(lambda: defaultdict(int))
		score = 1
		while reader():
			if (data.chromosome,data.strand) not in list_of_tuples:
				try:
					list_of_tuples[data.chromosome,data.strand] = gtf.chromosomeGeneCoordIterator(data.chromosome,numpy=True,strand=data.strand)	# I am only allowing 'sense' overlap
				except AssertionError:
					continue
			search_results = numpy_overlap(list_of_tuples[data.chromosome,data.strand],data.start,data.end-1,overlap=1)
			if search_results:																		# only add to the chromarray if overlap was found with a genomic feature
				if data.strand == "." or ignorestrand:												# if the feature has no strand or the data has no strand, put everything in the plus strand array.
					data.strand = "+"
				readlength = data.end - data.start
				if data.score.isdigit(): score = int(data.score)
				chromarray[data.strand][data.start:data.end] += score
				for gene in search_results:
					genecoverageinfo[gene][readlength] += score
		if todisk:																					# not fully tested and experimental
			tempplus  = tempfile.NamedTemporaryFile(mode='w',suffix=".npy",dir=tempdirectory,delete=False)	# making temp files
			tempminus = tempfile.NamedTemporaryFile(mode='w',suffix=".npy",dir=tempdirectory,delete=False)
			np.save(tempplus,chromarray["+"])
			np.save(tempminus,chromarray["-"])
			chromarray["+"] = np.memmap(tempplus.name,shape=(chromosomelength))						# each chromarray key is linked to a numpy.memmap
			chromarray["-"] = np.memmap(tempminus.name,shape=(chromosomelength))
			chromarray["files"] = list()
			chromarray["files"].extend([tempplus,tempminus])
		return chromarray,genecoverageinfo