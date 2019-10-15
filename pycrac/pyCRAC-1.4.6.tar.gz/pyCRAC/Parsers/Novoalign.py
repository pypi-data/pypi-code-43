#!/usr/bin/python

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2018"
__version__     = "0.3.3"
__credits__     = ["Sander Granneman"]
__maintainer__  = "Sander Granneman"
__email__       = "sgrannem@staffmail.ed.ac.uk"
__status__      = "Production"

##################################################################################
#
#	Novoalign.py
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
import six
import pprint
from pyCRAC.Methods import basequality,complement,reverse_complement
from pyCRAC.Classes.Exceptions import *

pp = pprint.PrettyPrinter(indent=4)

SUBS_REGEX		= re.compile('(\d+)([ATGC])>[ATGC]')
DELS_REGEX		= re.compile('(\d+)[-]([ATGC]+)')
INS_REGEX		= re.compile('(\d+)[+]([ATGC]+)')
COLLAPSER_REGEX = re.compile('>(\d+)-(\d+)_(.*)')

def reverse_strand(string):
	if not string:
		return None
	elif string	  == "F":
		return "R"
	elif string == "R":
		return "F"
	elif string == "+":
		return "-"
	else:
		return "+"

class Process_Novo():
	"""Base class for the Novoalign parser"""
	def __init__(self,file_in,base_quality=25):
		""" Initialises the class attributes"""
		self.headers		= list()
		self.__base_quality = base_quality
		self.__file			= None
		if hasattr(file_in,'read'):  					# This allows you to pipe data from the standard input. the input file would be sys.stdin
			self.__file = file_in
		elif isinstance(file_in,tuple):					# This allows you to process novoalign strings in lists
			self.__file = iter(file_in)
		else: 
			self.__file = open(file_in,"r")
		self.__line = str()
		self.__reset()

	def __reset(self):
		""" Resets all the attributes in the Novoalign class. This is done before it reads a new line in the data file. Surprisingly, this is much faster than __slots__ or using named tuples! Keeping it simple is usually better!"""
		self.__line			 = str()		# line of the current file
		self.__qname		 = str()		# Query sequence name
		self.__rname		 = str()		# Reference sequence name
		self.__strand_query	 = str()		# Indicates the strand of the query sequence, default is indicated
		self.__strand_mate	 = str()		# Indicates the strand of the mate sequence, default is indicated
		self.__ispaired		 = False		# Indicates whether the read is paired (True or False)
		self.__seqquery		 = str()		# Sequence
		self.__seqmate		 = str()		# Sequence of the mate sequence on the same strand as the reference
		self.__read_type	 = "S"			# Read is either the first read of the pair ("L") or the second/paired ("R"), default is indicated
		self.__qual			 = str()		# Query quality (ASCII-33=Phred base quality)
		self.__alignscore	 = int()		# Align score (Phred-scaled)
		self.__alignquality	 = int()		# Align quality (or mapping quality, Phred-scaled)
		self.__substitutions = list()		# List containing substitutions (0-based positions to reference sequence!)
		self.__insertions	 = list()		# List containing insertions	(0-based positions to reference sequence!)
		self.__deletions	 = list()		# List containing deletions		(0-based positions to reference sequence!)
		self.__skippedref	 = list()		# List containing numbers of nucleotides that were skipped from the reference
		self.__hit_repeat	 = "U"			# Indicates whether a read was mapped only once ("U") or has multiple alignment records ("R"), default is indicated
		self.__num_of_align	 = int()		# Indicates the number of alignment locations for a read on the genome
		self.__pos			 = int()		# 0-based leftmost mapping POSition
		self.__mpos			 = int()		# 0-based leftmost mapping POSition of the Mate read
		self.__mismatches	 = list()		# mismatches in the read
					
	def decode_Mismatches(self,mismatchstring):
		""" decodes the mismatch information at the end of each line. Novoalign mismatch coordinates are 1-based and are converted to 0-based coordinates """
		self.__substitutions = [(int(i[0])-1,i[1]) for i in SUBS_REGEX.findall(mismatchstring)]
		self.__deletions	 = [(int(i[0])-1,i[1]) for i in DELS_REGEX.findall(mismatchstring)]
		self.__insertions	 = [(int(i[0])-1,i[1]) for i in INS_REGEX.findall(mismatchstring)]
			
	def readline(self,correct_seq=True):
		""" Reads the next line in the file and keeps going until it finds a mapped read """
		self.__reset()
		while True:
			try:
				self.__line = six.next(self.__file)
			except StopIteration:
				return False
			if self.__line.startswith("#"):
				self.headers.append(self.__line)
				continue
			Fld =  self.__line.strip('\n').split('\t')
			if len(Fld) >=12:
				self.__qname		 = Fld[0]
				self.__read_type	 = Fld[1]
				self.__seqquery		 = Fld[2]
				self.__qual			 = Fld[3]
				self.__hit_repeat	 = Fld[4]
				self.__alignscore	 = int(Fld[5])
				self.__alignquality	 = int(Fld[6])
				self.__rname		 = Fld[7][1:]
				self.__pos			 = int(Fld[8])-1				# -1 converts position to 0-based coordinates!!
				self.__strand_query	 = Fld[9]
				self.__strand_mate	 = Fld[12]
				self.__mpos			 = int()
				if Fld[10] == ".": self.__ispaired = True
				if Fld[11] != ".": self.__mpos = int(Fld[11])-1		# -1 converts position to 0-based coordinates!!
				if self.__line[0] == ">":
					self.__qual = len(self.__seqquery)*"L"			# If there is no quality string, all bases get highest base quality value (Phred score of 41, assuming Illumina 1.8).
				try:
					self.__mismatches = Fld[13].split()
					self.decode_Mismatches(Fld[13])
				except IndexError:
					pass

#--------------------------------- Sequences are automatically corrected but this can be turned off! If reads contain deletions, dashes are inserted at the positions and substitutions are highlighted as lowercase letters ---------------------------------------------------
			
			if correct_seq: 
				self.correct_seq()
			return True
									
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
			
	def printHeaders(self):
		""" prints the Novo file header info """
		if self.headers:
			for line in self.headers:
				sys.stdout.write(line)
	
	def printDictionaryLayout(self):
		""" Prints the interval_dict dictionary layout using pretty printer"""
		pp.pprint(self.__dict__)
					
	def __call__(self):
		""" Returns the input line as a string"""
		if self.__line:
			return self.__line
		else:	
			return None
					
	def uniqueAlnLocation(self):
		""" From Novoalign documentation: column 5 in the novo file:
		U: A single alignment with this score was found. R: Multiple alignments with similar score were found.
		QC: The read was not aligned as it bases qualities were too low or it was a homopolymer read.
		NM :No alignment was found. QL: An alignment was found but it was below the quality threshold.\
		If a read has been aligned to only one genomic location (i.e. column 5 = "U") then
		this method will return 'True', otherwise it will return 'False'"""
		if self.__hit_repeat == "U":
			return True
		else:
			return False

	def seq_ID(self):
		""" Returns the sequence identification number of the read"""
		if self.__qname.startswith(">"):	# remove the chevron if it is before the header
			return self.__qname[1:]
		else:
			return self.__qname

	def read_type(self):
		""" Returns the read_type indicator ("S" = single end read; "L" or "R" indicate paired end reads)"""
		return self.__read_type
	
	def ismapped(self):
		""" Checks if a read is mapped to the reference sequence """
		if self.__rname:
			return True
		else:
			return False
	
	def sequence(self):
		""" Returns the sequence of the reads"""
		if self.__read_type == "R":
			return reverse_complement(self.__seqquery)
		else:		 
			return self.__seqquery

	def align_score(self):
		""" Returns the Phred format alignment score 10log10(P(R|Ai)).
		For status of 'R' and when not report alignment locations for repeats,
		the alignment score becomes the number of alignments to the read.
		For paired end the alignment score includes the fragment length penalty.
		Align_score is indicated in column 6 of the novo file."""
		if self.__alignscore:
			return self.__alignscore
		else:
			return 0

	def align_quality(self):
		""" Returns the align_quality value of the read sequence,
		which is the Phred format alignment quality score 10log10(1 P(Ai|R, G))
		using Sanger fastq coding method.Align quality is indicated in column 7 
		of the novo file"""
		if self.__alignquality:
			return self.__alignquality
		else:
			return 0

	def alignScoreThreshold(self,number):
		""" Checks whether the alignment score is smaller than the to a threshold set by the
		user. If the alignment score is smaller than the threshold, the method returns 'False' else it returns 'True' """
		if number > self.__alignscore:
			return False
		else:
			return True

	def alignQualityThreshold(self,number):
		""" Checks whether the alignment quality is smaller than to the to a threshold set by the
		user. If the alignment quality is smaller than the threshold, the method returns 'False' else it returns 'True' """
		if number > self.__alignquality:
			return False
		else:
			return True

	def lengthThreshold(self,number):
		""" This method tests whether the length of the read sequence is smaller or equal to a maximum length
		threshold set by the user. If the read is smaller than the threshold the method returns 'True', else
		it returns 'False' """
		if number >= len(self.__seqquery):
			return True
		else:
			return False

	def unique_hits(self):
		""" Returns R or U. R indicates that the read was mapped to multiple genomic locations.
		U indicates that the read mapped to only one location on the genome"""
		return self.__hit_repeat

	def sequenceAlignmentLocations(self):
		"""This method returns the number of alignments to the read"""
		if self.__hit_repeat == "R":
			return self.__alignscore
		if self.__hit_repeat == "U":
			return 1

	def read_start(self):
		""" Returns the 0-based start position of the read on the chromosome"""
		if self.__pos >= 0:
			return self.__pos
		else:
			return None

	def read_start_paired(self):
		""" Returns the start position of the paired read on the chromosome"""
		if self.__mpos >= 0:
			return self.__mpos
		else:
			return None
					
	def paired_sequence(self,distance=1000):
		""" Returns TRUE if the read has a paired read mapped to the same chromosomal location"""
		if self.__ispaired and self.__pos - self.__mpos <= distance or self.__pos - self.__mpos >= distance:
			return True
		else:
			return None
					
	def read_end_paired(self):
		""" Returns the chromosomal end coordinate of the paired read. For paired end reads
		it calculates the end position using the information obtained from the paired read."""
		if self.__mpos <= self.__pos:
			return self.__pos + len(self.__seqquery) - 1
		else:
			return None

	def read_end(self):
		""" Returns the chromosomal end coordinate of the read. For paired end reads
		it calculates the end position using the information obtained from the paired read."""
		if self.__pos >= 0:
			return self.__pos + len(self.__seqquery)
		else:
			return None

	def strand(self):
		""" Returns the read strand of the chromosome ("F" = watson, "R" = crick strand) the read was mapped to
		NOTE: if the read was obtained from the reverse sequencing reaction (i.e. read_type = "R"), then the opposite strand
		will be returned"""
		if self.__read_type == "R":
			return reverse_strand(self.__strand_query)
		else:
			return self.__strand_query

	def strand_paired(self):
		""" Returns the strand of the paired read"""
		if self.__strand_mate:
			return self.__strand_mate
		else:
			return None
	
	def chr_ID(self):
		""" Returns the reference chromosome name/number the read sequence was mapped to"""
		if self.__rname:
			return self.__rname
		else:
			return None

	def baseQuality(self,nucl_nr,qualtype="L"):
		""" This method returns the basequality value (an integer, NOT ASCI!) at position nucl_nr. Usage: base_quality(24)
		NOTE: This method can ONLY be used when the sequence has been corrected for deletions and insertions! (use the correct_seq
		or genomic_seq methods to correct the sequence. You need to include format of the quality scoring, for example: qualtype="sanger" or qualtype="illumina
		S - Sanger		  Phred+33,	 raw reads typically (0, 40)
		X - Solexa		  Solexa+64, raw reads typically (-5, 40)
		I - Illumina 1.3+ Phred+64,	 raw reads typically (0, 40)
		J - Illumina 1.5+ Phred+64,	 raw reads typically (3, 40) with 0=unused, 1=unused, 2=Read Segment Quality Control Indicator (bold) 
		L - Illumina 1.8+ Phred+33,	 raw reads typically (0, 41)
		Default is L """
		quality = self.baseQualityString()
		if len(quality) > 1:
			if nucl_nr > len(quality):
				corr_nr = nucl_nr - self.__pos
				if corr_nr < 0:
					raise BaseQualityError("\n\ncould not calculate the base-quality for nucleotide position %d in read %s\nQuality length\t%s\nposition\t%s" % (nucl_nr,self.__qname,len(quality),nucl_nr))
				else:
					return basequality(quality[corr_nr],ftype=qualtype)
			else:
				return basequality(quality[nucl_nr],ftype=qualtype)
		else:
			return 0
							
	def baseQualityString(self):
		""" Returns the quality string for the sequence in the line"""
		if self.__read_type == "S" or self.__read_type == "L":
			if self.__strand_query == "F":
				return self.__qual
			else:
				return self.__qual[::-1]
		elif self.__read_type == "R":
			if self.__strand_query == "F":
				return self.__qual[::-1]
			else:
				return self.__qual
							
	def mutations(self):
		""" This method returns a list of all the mutations (basically column 13 in the .novo file) found in a read sequence"""
		if self.__mismatches:
			return self.__mismatches
		else:
			return []

	def deletions(self,chromosome_location=False):
		""" Returns a list of deletions found in a read. Offset of mismatches are 0-based relative 
		to the reference sequence alignment location. They are not the location of the mismatches in the read itself
		but in the reference sequence!! If the values are negative then the read is the reverse complement of the reference sequence. 
		If you include the argument 'chromosome_location = True' then the method will only return the chromosomal coordinate. """
		if chromosome_location and self.__deletions:
			return [i[0]+self.__pos for i in self.__deletions]		 # returns a 0-based position			 
		elif self.__deletions:
			if self.__strand_query == "F":
				return [i[0] for i in self.__deletions]	  
			elif self.__strand_query == "R":
				return [-(i[0]+1) for i in self.__deletions]	
		else:
			return [] 
	
	def substitutions(self,chromosome_location=False):
		""" Returns a list of substitutions found in a read. Offset of mismatches are 0-based relative 
		to the reference sequence alignment location. If the values are negative then the read is the reverse complement of the reference sequence.
		If you include the argument 'chromosome_location = True' then the method will return the location of the substitutions on the chromosome.
		If you add basequality=30 then all the substitutions with a basequality lower than 30 will be removed. If you set filtersubs="TC" then
		only T to C conversions will be kept and others will be removed.
		All are 0-based positions"""
		if self.__substitutions:
			if chromosome_location and self.__substitutions:
				return [i[0]+self.__pos for i in self.__substitutions]	  # returns a 0-based position			 
			elif self.__substitutions:
				if self.__strand_query	 == "F":
					return [i[0] for i in self.__substitutions]	  
				elif self.__strand_query == "R":
					return [-(i[0]+1) for i in self.__substitutions]	
			else:
				return []
		else:
			return []

	def filterMutations(self,filter):
		"""Checks if a read has specific deletions or substitutions:
		Choices are:
				'delsonly': checks if a read has deletions.		 If so, it returns True and only deletions will be reported. Else, it returns False.
				'subsonly': checks if a read has substitutions.	 If so, it returns True and only substitutions will be reported. Else, it returns False.
				'nomuts'  : no mutations will be reported.
				'TC'	  : checks if a read has T->C mutations. If so, it removes mutations that do not fit these criteria and returns True, else False.
				'[T,C,G]' : (list) checks if the reads has T's, C's and/or G's mutated. If so, it removes mutations that do not fit these criteria and returns True, else False.
		"""
		if filter	== "delsonly":
			self.__substitutions = []
			if self.__deletions: 
				return True
			else: 
				return False
		elif filter == "subsonly" and self.__substitutions:
			self.__deletions = []
			if self.__substitutions: 
				return True
			else: 
				return False
		elif filter == "nomuts":
			self.__substitutions = []
			self.__deletions	 = []
			return True
				
		elif isinstance(filter,list):
			# format for deletions: 'offset'>'refbase'
			# format for substitutions: 'offset''refbase'>'readbase'
			if self.__substitutions:
				newmutslist = list()
				for (position,nucleotide) in self.__substitutions:
					if self.__read_type == "S" or self.__read_type == "L":
						if self.__strand_query == "R":
							nucleotide = reverse_complement(nucleotide)
					elif self.__read_type == "R":
						if self.__strand_query == "F":
							nucleotide = reverse_complement(nucleotide) 
					if nucleotide.upper() in filter:
						newmutslist.append((position,nucleotide))				# keep only those substitutions that match your criteria
				if newmutslist: 
					self.__substitutions = newmutslist
					return True
				else:
					return False
					
			if self.__deletions:
				newmutslist = list()
				for (position,nucleotide) in self.__deletions:
					if self.__read_type == "S" or self.__read_type == "L":
						if self.__strand_query == "R":
							nucleotide = reverse_complement(nucleotide)
					elif self.__read_type == "R":
						if self.__strand_query == "F":
							nucleotide = reverse_complement(nucleotide) 
					if nucleotide.upper() in filter:
						newmutslist.append((position,nucleotide))				# keep only those deletions that match your criteria
				if newmutslist: 
					self.__deletions = newmutslist	  
					return True
				else:
					return False	
			
			mutations = self.__substitutions + self.__deletions
			if mutations:
				return True						   
			else:
				return False

		elif isinstance(filter,str) and len(filter) == 2:
			# format = 'offset''refbase'>'readbase' 
			self.__deletions = []
			if self.__substitutions:	
				newmutslist = list()
				for subs in self.__substitutions:
					(position,nucleotide) = subs
					mutation = self.sequence()[position]		# read base
					actual	 = nucleotide						# ref base
					if self.__read_type == "S" or self.__read_type == "L":
						if self.__strand_query == "R":
							mutation = self.sequence()[-(position+1)]		# read base
							actual	 = reverse_complement(nucleotide)		# ref base
					elif self.__read_type == "R":
						if self.__strand_query == "F":
							mutation = self.sequence()[-(position+1)]		# read base
							actual	 = reverse_complement(nucleotide)		# ref base
					string = "%s%s" % (actual.upper(),mutation.upper())
					if string == filter:
						newmutslist.append(subs)			# keep only those substitutions that match your criteria
				self.__substitutions = newmutslist
				if self.__substitutions:
						return True
				else:
						return False
			else:
				return False
		else:
			return False
							
	def subsBaseQualFilter(self,basequality=0):
		""" checks the base quality of substitutions in the substitutions list. Returns a filtered list. The method
		expects illumina 1.8+ values"""
		if self.__substitutions:
			for subs in sorted(self.__substitutions):
				if self.baseQuality(subs[0]) < basequality:
					self.__substitutions.remove(subs)
						
		else:
			return []
				 
	def seq_length(self):
		""" Returns the length of the read sequence"""
		return len(self.__seqquery)
			
	def correct_seq(self):
		""" Checks if the sequence has any mutations and if so then removes the insertions
		adds dashes where it found a deletions and highlights substitutions lowercase. This
		method also corrects the base quality string (3rd column in novo file) if deletions
		are present in the sequence. This is essential if you want to know base quality values
		of substitutions"""
		nucleotides = list()
		quality		= list(self.__qual)
		if self.__qname and self.__mismatches:
			try:
				if self.__strand_query == "R":
					nucleotides = list(reverse_complement(self.__seqquery))
					quality.reverse()
				else:
					nucleotides = list(self.__seqquery)
				for i in self.__insertions:
					position,insertion = i[0],i[1]
					length			   = len(insertion)
					del nucleotides[position:position+length]
					del quality[position:position+length]
				for i in self.__deletions:
					position,deletions = i[0],i[1]
					for i in range(len(deletions)):
						nucleotides.insert(position,"-")
						quality.insert(position,"!")	# ! is base_quality of 0
				for i in self.__substitutions:
					position,substitution = i[0],i[1]
					nucleotides[position] = nucleotides[position].lower()
					quality[position]	  = quality[position].lower()
				if self.__strand_query == "R":
					self.__seqquery = reverse_complement(''.join(nucleotides))
					quality.reverse()
					self.__qual		= ''.join(quality)
				else:
					self.__qual		= ''.join(quality)
					self.__seqquery = ''.join(nucleotides)
				return True
			except:
				sys.stderr.write("Error in line %s\tCould not correct the sequence. Please remove from file\n" % self.__line.strip())
				return False
		else:
			return False
		
	def genomic_seq(self):
		""" Checks if the sequence has any mutations and if so then removes the insertions
		corrects the deletions and substitutions and shows these in lowercase. This method
		basically corrects the read sequence to the genomic sequence"""
		nucleotides = list()
		sequence	= str()
		if self.__mismatches:
			try:
				if self.__strand_query == "R":
					nucleotides = list(reverse_complement(self.__seqquery))
				else:
					nucleotides = list(self.__seqquery)
				for i in self.__deletions:
					position,deletions = i[0],i[1]
					for i in range(len(deletions)):
						nucleotides[position] = deletions[i].lower()
				for i in self.__substitutions:
					position,substitution = i[0],i[1]
					nucleotides[position] = substitution.lower()
				if self.__strand_query == "R":
					sequence = reverse_complement(''.join(nucleotides))
				elif self.__read_type == "R":
					sequence = reverse_complement(''.join(nucleotides))
				else:
					sequence = ''.join(nucleotides)
				return sequence
			except:
				sys.stderr.write("Error in line %s\tCould not generate the genomic sequence for this read. Please remove from file\n" % self.__line.strip())
				return self.__seqquery
		else:
			return self.__seqquery

	def fasta(self):
		""" Returns the read ID and read sequence in the fasta format"""
		if self.__qname:
			fasta =	 ">%s\n%s" % (self.__qname,self.__seqquery)
			return fasta
	
	def tab(self):
		""" Returns the read ID and read sequence in the tab delimited format"""
		if self.__qname:
			tab =  "%s\t%s" % (self.__qname,self.__seqquery)
			return tab
