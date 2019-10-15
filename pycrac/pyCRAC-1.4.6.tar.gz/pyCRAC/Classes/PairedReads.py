#!/usr/bin/python

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2019"
__version__     = "0.1.3"
__credits__     = ["Sander Granneman"]
__maintainer__  = "Sander Granneman"
__email__       = "sgrannem@staffmail.ed.ac.uk"
__status__      = "Production"

##################################################################################
#
#   PairedReads
#
#
#   Copyright (c) Sander Granneman 2019
#   
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#
##################################################################################

from pyCRAC.Classes.Exceptions import *

class PairedReadCollector():
	""" This class is used to TEMPORARILY store information about paired reads.
	To preserve memory, it will only store information for two reads at a time and then automatically starts removing the first read in the list.
	Useful to extract the necessary information from paired reads for analyses and the discard them."""
	def __init__(self):
		"""Initialises the class attributes"""
		self.read_list   = list()

	def addRead(self,interval):
		"""method to add read information to the read dictionary. Hit repeat = "U" indicates that the read has a single alignment location. "R" indicates the reads has multiple alignment locations\
		 read_types: 'L' = first read or read from a forward sequencing reaction, 'R' = second read or read from a reverse sequencing reaction. Object indicates a novoalign or SAM class object. 'line'\
		 indicates a string representing the entire line from the alignment file."""
		if self.numberOfReadsinList() == 2:
			self.removeRead()
		self.read_list.append({
			"chr_ID"        : interval.chr_ID(),
			"read_type"     : interval.read_type(),
			"read_id"       : interval.seq_ID(),
			"strand"        : interval.strand(),
			"read_start"    : interval.read_start(),
			"read_end"      : interval.read_end(),
			"deletions"     : interval.deletions(chromosome_location=True),
			"substitutions" : interval.substitutions(chromosome_location=True),
			"sequence"      : interval.sequence(),
		})
		return True

	def removeRead(self):
		"""removes the first read dictionary from the read list. Useful if two reads are not 'truly' paired"""
		del self.read_list[0]

	def reset(self):
		"""resets the read list and read dictionary"""
		self.read_list = []

	def strand(self,read="L"):
		"""returns the strand of the Forward (L) or Reverse (R) read for properly paired reads"""
		if self.numberOfReadsinList() == 2:
			if read == "L":
				return self.read_list[0]["strand"]
			elif read == "R":
				return self.read_list[1]["strand"]
			else:
				raise InputError("\n\ncould not determine whether you want the strand from the first ('L') or second ('R') read.n\n")
		else:
			return None

	def read_ID(self,read="L"):
		"""returns the sequence name or header of the Forward (L) or Reverse (R) read for properly paired reads"""
		if self.numberOfReadsinList() == 2:
			if read == "L":
				return self.read_list[0]["read_id"]
			elif read == "R":
				return self.read_list[1]["read_id"]
			elif read == "both":
				return (self.read_list[0]["read_id"],self.read_list[1]["read_id"])
			else:
				raise InputError("\n\ncould not determine whether you want the read ID from the first ('L') or second ('R') read\n\n")
		else:
			return None

	def read_type(self,read="L"):
		"""returns the read header of the Forward (L) or Reverse (R) read for properly paired reads"""
		if self.numberOfReadsinList() == 2:
			if read == "L":
				return self.read_list[0]["read_type"]
			elif read == "R":
				return self.read_list[1]["read_type"]
			elif read == "both":
				return (self.read_list[0]["read_type"],self.read_list[1]["read_type"])
			else:
				raise InputError("\n\ncould not determine whether you want the read ID from the first ('L') or second ('R') read\n\n")
		else:
			return None

	def chr_ID(self,read="L"):
		"""returns the read header of the Forward (L) or Reverse (R) read for properly paired reads"""
		if self.numberOfReadsinList() == 2:
			if read == "L":
				return self.read_list[0]["chr_ID"]
			elif read == "R":
				return self.read_list[1]["chr_ID"]
			elif read == "both":
				return (self.read_list[0]["chr_ID"],self.read_list[1]["chr_ID"])
			else:
				raise InputError("\n\ncould not determine whether you want the reference sequence ID from the first ('L') or second ('R') read.\n\n")
		else:
			return None

	def coordinates(self,read="both"):      # read can be "L", "R" or "both". The latter returns min and max coordinates from both reads
		"""returns a tuple with start and end position of a cDNA using paired read coordinates min and max values"""
		if self.numberOfReadsinList() == 2:
			if read == "both":
				coordinates = [self.read_list[0]["read_start"],self.read_list[0]["read_end"],self.read_list[1]["read_start"],self.read_list[1]["read_end"]]
				#print coordinates
				return (min(coordinates),max(coordinates))
			elif read == "L":
				return [self.read_list[0]["read_start"],self.read_list[0]["read_end"]]
			elif read == "R":
				return [self.read_list[1]["read_start"],self.read_list[1]["read_end"]]
			else:
				raise InputError("\n\ncould not determine whether you want the mapping coordinates for the first ('L') or second ('R') read.n\n")
		else:
			return None

	def cDNALength(self):
		"""returns the length of a cDNA using paired read coordinates"""
		positions = self.coordinates()
		if positions:
			start = positions[0]
			end   = positions[1]
			return end-start-1

	def numberOfReadsinList(self):
		"""returns the number of reads present in the self.read_list list"""
		return len(self.read_list)

	def ispaired(self):
		"""checks whether the two reads in the read list are proper pairs and whether the file has the correct order of reads"""
		if self.numberOfReadsinList() == 2:
			if self.read_list[0]["read_type"] == "L" and self.read_list[1]["read_type"] == "R" and self.chr_ID(read="L") == self.chr_ID(read="R"):
				return True
			else:
				return False
		else:
			return False

	def deletions(self,read="both"):                # read can be "L", "R" or "both". The latter returns deletions from all reads
		"""returns a list of all the deletions in the paired reads. Can be genomic positions or read positions"""
		if self.numberOfReadsinList() == 2:
			if read == "both":
				return self.read_list[0]["deletions"] + self.read_list[1]["deletions"]
			elif read == "L":
				return self.read_list[0]["deletions"]
			elif read == "R":
				return self.read_list[1]["deletions"]
			else:
				raise InputError("\n\ncould not determine from which read you want deletions (L,R or both)\n")
		else:
				return None

	def substitutions(self,read="both"):            # read can be "L", "R" or "both". The latter returns substitutions from all reads
		"""returns a list of all the substitutions in the paired reads. Can be genomic positions or read positions"""
		if self.numberOfReadsinList() == 2:
			if read == "both":
				return self.read_list[0]["substitutions"] + self.read_list[1]["substitutions"]
			elif read == "L":
				return self.read_list[0]["substitutions"]
			elif read == "R":
				return self.read_list[1]["substitutions"]
			else:
				raise InputError("\n\ncould not determine from which read you want substitutions (L,R or both)\n" )
		else:
			return None

	def sequence(self,read="both"):                 # read can be "L", "R" or "both". The latter returns sequences from all reads in a list
		"""returns sequences from paired reads"""
		if self.numberOfReadsinList() == 2:
			if read == "both":
				return [self.read_list[0]["sequence"], self.read_list[1]["sequence"]]
			elif read == "L":
				return self.read_list[0]["sequence"]
			elif read == "R":
				return self.read_list[1]["sequence"]
			else:
				raise InputError("\n\ncould not determine from which read you want the sequence (L,R or both)\n")
		else:
			return None

	def mutations(self):
		"""returns a list of all the mutations in the paired reads."""
		return self.deletions(read="both") + self.substitutions(read="both")