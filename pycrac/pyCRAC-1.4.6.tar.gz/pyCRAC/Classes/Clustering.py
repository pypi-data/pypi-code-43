#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2018"
__version__		= "0.0.3"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	Clustering.py
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

from pyCRAC.Parsers.ParseAlignments import ParseCountersOutput
from pyCRAC.Methods import overlap
import numpy as np
import sys

class ReadClustering():
	""" Class for generating read clusters out of read intervals.
	Only accepts GTF files as input file. Made for using with pyReadCounters read interval GTF files. """
	def __init__(self,datafile,logfile=sys.stderr):
		self.data = ParseCountersOutput(datafile,index=True)	# read data file needs to be indexed!
		np.seterrcall(self.__catchErrors)
		np.seterr(all='call')
		self.__end_not_reached = True
		self.__cluster_start = int()
		self.__cluster_end	 = int()
		self.__max_position	 = int()
		self.__max_read_end	 = int()
		self.__line_position = int()
		self.logfile		 = logfile
		self.index			 = None
		self.coveragearray	 = None
		self.subsarray		 = None
		self.delsarray		 = None
		self.chromosome		 = str()
		self.strand			 = str()
		self.read_length	 = 0
		self.line_count		 = 0
		self.cluster_height	 = 0
		self.cluster_length	 = 0
		self.cluster_count	 = 0
		self.cluster_read_count = 0
		self.max_cluster_length = int()
	
	def __catchErrors(self,type,flag):
		""" catches any numpy floating point errors and prints the problem cases to the standard error"""
		self.logfile.write("\nZero division error (%s), with flag %s\n%s" % (type,flag,self.data.line))
		self.logfile.write("subsarray:\n%s\ndelsarray:\n%s\ncoverageaarray:\n%s\n" % (self.subsarray,self.delsarray,self.coveragearray))
		
	def __trimNumpyArrays(self):
		""" shrinks the numpy arrays by removing any zeros """
		position = np.where(self.coveragearray > 0)[0][-1] + 1
		self.coveragearray = self.coveragearray[:position]
		self.subsarray	   = self.subsarray[:position]
		self.delsarray	   = self.delsarray[:position]
		
	def mutsAnnotationString(self,min_frequency=0):
		"""Makes a CIGAR-type string for mutations in reads or clusters"""
		subsstring = str()
		delsstring = str()
		mutlist	   = list()
		subsfreqarray,delsfreqarray = self.mutsCountsToFrequencies(min_frequency=float(min_frequency))
		for nr in range(len(subsfreqarray)):
			if subsfreqarray[nr]:
				subsstring = "S%.1f" % subsfreqarray[nr]
			if delsfreqarray[nr]:
				delsstring = "D%.1f" % delsfreqarray[nr]
			mutsstring = "%s%s%s" % (self.index[nr]+1,subsstring,delsstring) 
			if subsstring or delsstring:
				mutlist.append(mutsstring)
				subsstring = str()
				delsstring = str()
		if mutlist:
			return ','.join(mutlist)
		else:
			return None

	def mutsCountsToFrequencies(self,min_frequency=0):
		""" uses the cluster data to convert mutation numbers to mutation frequencies for each position """
		min_frequency = float(min_frequency)	# set the minimal mutation frequency
		subsfreqarray = self.subsarray * 100 / self.coveragearray # make an array of substitution frequencies
		delsfreqarray = self.delsarray * 100 / self.coveragearray # make an array of deletion frequencies
		substitutions = np.where(subsfreqarray > min_frequency,subsfreqarray,0)		# return all the positions larger than the min frequency
		deletions	  = np.where(delsfreqarray > min_frequency,delsfreqarray,0)
		return substitutions,deletions

	def __startNewCluster(self):
		""" method for setting up a new cluster. Note that the method assumes that you have already read a new line from the data file."""
		self.__start_new_cluster = False					# indicate that no new cluster has to be made in the next iteration.
		self.subsarray	= np.zeros(self.max_cluster_length)
		self.delsarray	= np.zeros(self.max_cluster_length)
		self.coveragearray = np.zeros(self.max_cluster_length)
		self.index		= np.arange(self.__cluster_start,self.__cluster_start+self.max_cluster_length)
		self.chromosome = self.data.chromosome
		self.strand		= self.data.strand
		self.start		= int()
		self.end		= int()
		self.cluster_height = 1
		self.cluster_read_count = 1
		if not self.__cluster_start:
			self.__cluster_start = self.data.read_start
		self.__max_position = self.__cluster_start + self.max_cluster_length
		self.__cluster_end = self.data.read_end
		self.__updateCluster()	# update the arrays with the information from the first read in the cluster. 
 
	def __finishCluster(self):
		""" When a cluster has been made it corrects the length of the arrays. It also keeps track of the number of clusters made. """
		self.cluster_length = self.end - self.start						# get the cluster length.
		self.subsarray = self.subsarray[:self.cluster_length]			# update the length of the arrays to make them as long as the cluster.
		self.delsarray = self.delsarray[:self.cluster_length]
		self.coveragearray = self.coveragearray[:self.cluster_length]
		self.cluster_count += 1											# update the cluster count.
		
	def __getNewRead(self):
		self.__end_not_reached = self.data.readLineByLine(numpy=True)	# get a line from the read data file
		self.read_length = self.data.read_end - self.data.read_start	# determine the read length
		self.line_count +=1												# add 1 to the read counter.
			
	def __updateCluster(self):
		""" adds the read information to the arrays."""
		self.data.number_of_reads
		self.coveragearray += np.where(((self.index <= self.data.read_end) & (self.index >= self.data.read_start)),self.data.number_of_reads,0)
		self.subsarray[np.in1d(self.index,self.data.substitutions)] += self.data.number_of_reads	# update the substitutions array.
		self.delsarray[np.in1d(self.index,self.data.deletions)] += self.data.number_of_reads		# update the deletions array.
		self.cluster_read_count += self.data.number_of_reads						                # update the cluster read count.
	
	def getCluster(self,min_overlap=1,min_cdnas=2,max_length=100,min_height=2,min_length=10,debug=False):
		"""Outputs strings of sequences that contain at least two single overlapping reads and it ignores repeated sequences. Behaves as an iterator.
		NOTE! For the clustering to work properly the GTF file has to be sorted in a specific way! First by chromosome, then by strand and then by start
		position! Use the sort -k1,1 -k7 -k4,4n to sort your GTF file. Returns 'True' if it found a new cluster and has updated all the class variables. 
		For each cluster it generates numpy arrays for substitutions deletions and the coverage (self.subsarray,self.delsarray and self.coveragearray). 
		It also keeps track of the read count whilst reading through the read gtf file. 
		You can put this method in a while loop as it returns 'False' when it reaches the end of the file.
		while object.getCluster():
			do something.....
				cluster_start = object.start
				cluster_end = object.end
				coverage  = object.coveragearray
				etc...
		Requires the file to be sorted first by chromosome and then by start position!!!!
		The maximum cluster length is set at 100 bp but this can be changed by setting the max_length variable."""
		self.max_cluster_length = max_length
		while self.__end_not_reached:
			if not self.line_count:									# start a new cluster if the first line in the file has not been read yet.
				self.__getNewRead()									# get a line from the file.
				self.__startNewCluster()							# start a new cluster.
			elif self.__start_new_cluster:							# if the cluster has been returned, start a new one.
				self.__startNewCluster()							# start a new cluster if a cluster has been returned.
			else:													# if a start to a new cluster has been made, just get another read.
				self.__getNewRead()									# get a line from the file.
				if self.data.chromosome == self.chromosome and self.data.strand == self.strand and overlap(self.data.read_start,self.data.read_end-1,self.__cluster_start,self.__cluster_end,overlap=min_overlap):	# if they are on the same chromosome and strand and overlap, continue
					self.__updateCluster()									# update the arrays with the read information.
					self.__start_new_cluster = False						# we don't have to start thinking about a new cluster as long as there is overlap.
					if self.data.read_end > self.__max_position:			# if the end position of the last read is beyond the cluster boundary, note position of the read in the file and continue.
						if not self.__line_position:
							self.__line_position = self.line_count - 1		# it needs to remember on which line this occurred. After finishing the cluster, it needs to go back to these lines for the next cluster.
						self.__cluster_end = self.__max_position			# but the end position of the cluster can already be set here.
					else:
						if self.data.read_end >= self.__cluster_end:		# if the read falls completely within the cluster boundaries, just continue.
							self.__cluster_end = self.data.read_end			# if not, just set the end position of the cluster.
				else:
					self.start = self.__cluster_start						# set the start position of the current cluster.
					self.end   = self.__cluster_end							# set the end position of the current cluster.
					self.__start_new_cluster = True							# indicate that a new cluster has to be made in the next iteration.
					if self.__line_position:								# if there is no longer overlap,
						self.data.seek(self.__line_position)				# go back to position where the end position was larger than the cluster boundary and start from there for the next cluster.
						self.line_count = self.__line_position				# after seek, the read count needs to be set back to that position.
						self.__getNewRead()									# then re-read the interval data at that position.
						self.__line_position = int()						# reset the line position variable.
						self.__cluster_start = self.__max_position + 1		# set the new cluster start.
					else:
						self.__cluster_start = self.data.read_start			# set the start position of the next cluster
					#### does the existing cluster fit all the criteria? ###	  
					self.cluster_height = int(self.coveragearray.max())										# calculate the cluster height.
					if self.cluster_read_count >= min_cdnas and self.cluster_height >= min_height:			# if the cluster fits all the criteria, return True.
						self.__finishCluster()																# adjust the length of the arrays and finish the cluster.
						if self.cluster_length >= min_length:
							return True																		# indicate that a cluster was found.
						