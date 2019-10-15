#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2018"
__version__		= "0.3.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	SAM.py
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
from pysam import Samfile
from pyCRAC.Methods import basequality,complement,reverse_complement
from pyCRAC.Classes.Exceptions import *
pp = pprint.PrettyPrinter(indent=4)

MUTS_REGEX = re.compile('[0-9]+[A-Z]|[0-9]+\^[A-Z]+')
#COLLAPSER_REGEX = re.compile('>(\d+)-(\d+)_(.*)')			# group 1 is sequence id and group 2 is number of sequences

def string_lower(string,position):
	a = list(string)
	a[position] = a[position].lower()
	return ''.join(a)
	
def reverse_strand(string):
	if not string:
		return None
	elif string == "F":
		return "R"
	elif string == "R":
		return "F"
	elif string == "+":
		return "-"
	else:
		return "+"

class Process_Sam():
	""" Splits the line from a sam file into columns and adds keys values to a dictionary called interval_dict. Use the type variable to indicate whether the file is a SAM or BAM file"""
	def __init__(self,file_in,base_quality=25):
		""" Initializes the class attributes"""
		self.__file			= None
		self.__base_quality = base_quality
		if hasattr(file_in,'read'):  					# This allows you to pipe data from the standard input. the input file would be sys.stdin
			try:
				self.__file = Samfile("-")
			except ValueError:
				self.__file = Samfile("-","rb")
		else: 
			try:
				self.__file = Samfile(file_in)
			except ValueError:
				self.__file = Samfile(file_in,"rb")
		self.__CIGAR_checked = False
		self.__sam_data		 = self.__file.fetch(until_eof=True)
		self.__line			 = str()
		self.__reset()

	def __reset(self):
		""" Resets all the attributes in the SAM class. Surprisingly,this is much faster than __slots__ or using named tuples! Keeping it simple is usually better!"""
		self.__line			 = str()		# line of the current file
		self.__strand_query	 = str()		# Indicates the strand of the query sequence, default is indicated
		self.__strand_mate	 = str()		# Indicates the strand of the mate sequence, default is indicated
		self.__seqquery		 = str()		# Sequence
		self.__seqmate		 = str()		# Sequence of the mate sequence on the same strand as the reference
		self.__read_type	 = "S"			# Read is either the first read of the pair ("L") or the second/paired ("R"), default is indicated
		self.__qual			 = str()		# Query quality (ASCII-33=Phred base quality)
		self.__alignscore	 = int()		# Align score (Phred-scaled)
		self.__substitutions = list()		# List containing substitutions (0-based positions to reference sequence!)
		self.__insertions	 = list()		# List containing insertions	(0-based positions to reference sequence!)
		self.__deletions	 = list()		# List containing deletions		(0-based positions to reference sequence!)
		self.__skippedref	 = list()		# List containing numbers of nucleotides that were skipped from the reference
		self.__hit_repeat	 = "U"			# Indicates whether a read was mapped only once ("U") or has multiple alignment records ("R"), default is indicated
		self.__rname		 = str()		# Reference sequence name
		self.__num_of_align	 = int()		# Indicates the number of alignment locations for a read on the genome

	def printDictionaryLayout(self):
		""" Prints the interval_dict dictionary layout using pretty printer"""
		pp.pprint(self.__dict__)

	def readline(self,correct_seq=True):
		""" Reads the next line in the file and keeps going until it finds a mapped read """
		self.__reset()
		while True:
			try:
				self.__line = six.next(self.__sam_data)
			except StopIteration:
				return False
			if not self.__line:														# if no line exists: continue
				continue
			if self.__line.seq:														# if no sequence exists: continue
				self.__seqquery = self.__line.seq
			else:
				continue
			if self.__line.tid >= 0:
				self.__rname = self.__file.getrname(self.__line.tid)
			else:	
				continue															# if no reference name exists: continue
			self.__qual		= self.__line.qual
			if self.__line.qual == "." or not self.__line.qual:
				self.__qual = len(self.__line.seq)*"L"								# If there is no quality string, all bases get highest base quality value (Phred score of 41, assuming Illumina 1.8).
			self.decode_CIGAR()
			self.decode_TAGs()
			if self.__line.is_reverse:
				self.__strand_query = "R"
			else: 
				self.__strand_query = "F"
			if self.__line.is_paired:
				if not self.__line.mate_is_reverse:
					self.__strand_mate	= "F"
					self.__strand_query = "R"
				else:
					self.__strand_mate	= "R"
					self.__strand_query = "F"
				if self.__line.is_read1:
					self.__read_type = "L"
				if self.__line.is_read2: 
					self.__read_type = "R"
					
#--------------------------------- Sequences are automatically corrected but this can be turned off! If reads contain deletions, dashes are inserted at the positions and substitutions are highlighted as lowercase letters ---------------------------------------------------
			
			if correct_seq: 
				self.correct_seq()
			return True
									
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	def decode_CIGAR(self):
		""" Decodes the SAM CIGAR info
		Documentation:
		SAM		BAM		Description
		M		0		alignment match (can be a sequence match or mismatch)
		I		1		insertion to the reference
		D		2		deletion from the reference
		N		3		skipped region from the reference
		S		4		soft clipping (clipped sequences present in SEQ)
		H		5		hard clipping (clipped sequences NOT present in SEQ)
		P		6		padding (silent deletion from padded reference)
		=		7		sequence match
		X		8		sequence mismatch
		- H can only be present as the first and/or last operation.
		- S may only have H operations between them and the ends of the CIGAR string.
		- For mRNA-to-genome alignment, an N operation represents an intron. For other types of alignments, the interpretation of N is not defined.
		- Sum of lengths of the M/I/S/=/X operations shall equal the length of SEQ.
		Example:
		CIGAR: 1S29M2D1I25M
		Sequence : TTGCAATTCGCCAGCAAGCACCCAAGGCCTCCGCCAAGTGCACCGTTGCTAGCCT
		position 1 'T', softclip, then 29 matched, then 31 and 32 are deleted, one nucleotide insertion and the remaining 25 are matched
		"""
		start = 0		  # start = 0 is the start position of the read
		self.__CIGAR_checked = True
		cigar_list = self.__line.cigar
		#assert self.__seqquery, "no seq at line:\n %s\n" % self.__line
		sequence = list()
		quality	 = list()
		if type(cigar_list) is list:
			sequence = list(self.__seqquery)
			quality	 = list(self.__qual)
			for (code,position) in cigar_list:
				if	 code == 0:
					start += position
				elif code == 1:
					self.__insertions.extend(list(range(start,start+position)))
					del sequence[start:start+position]
					start += position
				elif code == 3:															   # I have not (yet) come across a read that has this so I haven't been able to test this code properly
					self.__skippedref.append((start,position))		  
				elif code == 4:
					del sequence[start:start+position]
				else:
					continue
			self.__seqquery = "".join(sequence)
			self.__qual		= "".join(quality)
			return True
		else:
			return False
			
	def __call__(self):
		""" Returns the input line as a string"""
		if self.__line:
			return "%s\n" % self.__line
		else:	
			return None

	def decode_TAGs(self):
		"""
		Type	Description
		A		Printable character
		i		Signed 32-bit integer
		f		Single-precision float number
		Z		Printable string
		H		Hex string (high nybble first)

		Tag		Type	Description
		X?		?		Reserved fields for end users (together with Y? and Z?)
		RG		Z		Read group. Value matches the header RG-ID tag if @RG is present in the header.
		LB		Z		Library. Value should be consistent with the header RG-LB tag if @RG is present.
		PU		Z		Platform unit. Value should be consistent with the header RG-PU tag if @RG is present.
		PG		Z		Program that generates the alignment; match the header PG-ID tag if @PG is present.
		AS		i		Alignment score generated by aligner
		SQ		H		Encoded base probabilities for the suboptimal bases at each position (deprecated by E2 and U2)
		OQ		Z		Original base quality. Encoded in the same wasy as QUAL.
		E2		Z		The 2nd most likely base base call.
		U2		Z		Phred-scaled log-lk ratio of the 2nd to the 3rd most likely base calls. Encoding is the same as QUAL.
		MQ		i		The mapping quality score of the mate alignment
		NM		i		Number of nucleotide differences (i.e. edit distance to the reference sequence)
		H0		i		Number of perfect hits
		H1		i		Number of 1-difference hits (an in/del counted as a difference)
		H2		i		Number of 2-difference hits (an in/del counted as a difference)
		UQ		i		Phred likelihood of the read sequence, conditional on the mapping location being correct
		PQ		i		Phred likelihood of the read pair, conditional on both the mapping locations being correct
		NH		i		Number of reported alignments that contains the query in the current record
		IH		i		Number of stored alignments in SAM that contains the query in the current record
		HI		i		Query hit index, indicating the alignment record is the i-th one stored in SAM
		MD		Z		String for mismatching positions in the format of [0-9]+(([ACGTN]|\^[ACGTN]+)[0-9]+)*
		CS		Z		Color read sequence on the same strand as the reference 4
		CQ		Z		Color read quality on the same strand as the reference; encoded in the same way as <QUAL>
		CM		i		Number of color differences 2
		R2		Z		Sequence of the mate.
		Q2		Z		Phred quality for the mate (encoding is the same as <QUAL>).
		S2		H		Encoded base probabilities for the other 3 bases for the mate-pair read. Same encoding as SQ 
		CC		Z		Reference name of the next hit; "=" for the same chromosome
		CP		i		Leftmost coordinate of the next hit
		SM		i		Mapping quality if the read is mapped as a single read rather than as a read pair
		AM		i		Smaller single-end mapping quality of the two reads in a pair
		MF		i		MAQ pair flag (MAQ specific)

		Example:

		AS:i:30 UQ:i:30 NM:i:1	MD:Z:24G9

		Alignment score generated by aligner = 30, Phred likelyhood of the read sequence = 30, Number of nucleotide differences: 1, Mismatching position: 24, mismatched nucleotide: G
		MD example: a string "10A5^AC6" means from the leftmost reference base in the alignment, there are 10 matches followed by an A on the reference which is different from the aligned read base; 
		the next 5 reference bases are matches followed by a 2bp deletion from the reference; the deleted sequence is AC; the last 6 bases are matches. The MD field ought to match the CIGAR string.
		All the information about substitutions and deletions is 0-based!
		"""
		if self.__line.tags:
			for tags in self.__line.tags:
				if tags[0] == "AS"or tags[0] == "UQ":
					self.__alignscore = int(tags[1])
				elif tags[0] == "R2":
					self.__seqmate = tags[1]
				elif tags[0] == "NH":
					if int(tags[1]) == 1:
						self.__hit_repeat == "U"
					else:
						self.__hit_repeat == "R"
					self.__num_of_align = int(tags[1])
				elif tags[0] == "MD":
					start = 0				# start = 0 is the start position of the read
					results = MUTS_REGEX.findall(tags[1])
					if results:
						for i in results:
							subs = re.match("([0-9]+)([A-Z])",i)
							dels = re.match("([0-9]+)\^([A-Z]+)",i)
							if subs:
								substitution = subs.group(2)
								start		+= int(subs.group(1))
								length		 = len(substitution)
								nuc			 = subs.group(2)
								self.__substitutions.append((start,nuc))
								start		+= length
							elif dels:
								start		+= int(dels.group(1))
								deletions	 = dels.group(2)
								length		 = len(deletions)
								self.__deletions.extend([(start+i,deletions[i]) for i in range(length)])
								start		+= length
							else:
								sys.stderr.write("Illegal character in tag search\n")
				else:
					continue
			return True
		else:
			return False
	
	def ismapped(self):
		""" Checks if a read is mapped to the reference sequence """
		if not self.__line.is_unmapped:
			return True
		else:
			return False

	def correct_seq(self):
		""" Corrects the sequence for substitutions and deletions. Insertions and 'softclips' are automatically removed when reading the CIGAR """
		if self.__CIGAR_checked:
			try:
				sequence = list(self.__seqquery)
				quality	 = list(self.__qual)
				for pos in self.__deletions:
					position,deletions = pos[0],pos[1]
					for i in range(len(deletions)):
						sequence.insert(position,"-")
						quality.insert(position,"!")	# ! is base_quality of 0
				for pos in self.__substitutions:
					position,nucleotide = pos[0],pos[1]
					sequence[position]	= sequence[position].lower()
				self.__seqquery = "".join(sequence)
				self.__qual		= "".join(quality)
				return True
			except:
				sys.stderr.write("Error in line %s\tCould not correct the sequence. Please remove from file\n" % self.__line.strip())
				return False
		else:
			sys.stderr.write("you need to run the decode_CIGAR method first before you can use the correct_seq method\n")

	def genomic_seq(self):
		""" Looks if the sequence has any mutations and if so then removes the insertions
		corrects the deletions and substitutions to the genomic sequence and shows these in lowercase."""
		if self.__CIGAR_checked:
			try:
				sequence = list(self.__seqquery)
				for pos in self.__deletions:
					position,deletions = pos[0],pos[1]
					for i in range(len(deletions)):
						sequence[position] = deletions[i].lower()
				for pos in self.__substitutions:
					position,nucleotide = pos[0],pos[1]
					sequence[position]	=  nucleotide.lower()
				return "".join(sequence)
			except:
				sys.stderr.write("Error in line %s\tCould not correct the sequence. Please remove from file\n" % self.__line.strip())
				return sequence
		else:
			sys.stderr.write("you need to run the decode_CIGAR method first before you can use the genomic_seq method\n")

	def deletions(self,chromosome_location=False):
		""" Returns a list of deletions found in a read. Offset of mismatches are 0-based relative 
		to the reference sequence alignment location. If the values are negative then the read is the reverse complement of the reference sequence. 
		If you include the argument 'chromosome_location = True' then the method will return the location of the deletion on the chromosome
		All positions are 0-based positions"""
		if self.__deletions:
			dels = list()
			for i in self.__deletions:
				position,deletion = i[0],i[1]
				dels.extend(list(range(position,position+1)))
			if chromosome_location:
				return [y+self.__line.pos for y in dels]
			else:
				if self.__read_type == "S":
					if self.__strand_query == "F":
						return dels
					if self.__strand_query == "R":
						return [-(y+1) for y in dels]
				elif self.__read_type == "L":
					if self.__strand_query == "F":
						return dels
					if self.__strand_query == "R":
						return [-(y+1) for y in dels]
				elif self.__read_type == "R":
					if self.__strand_query == "F":
						return [-(y+1) for y in dels]
					else:
						return dels
		else:
			return []
					
	def substitutions(self,chromosome_location=False,base_quality=30,filtersubs=None):
		""" Returns a list of substitutions found in a read. Offset of mismatches are 0-based relative 
		to the reference sequence alignment location. If the values are negative then the read is the reverse complement of the reference sequence.\ 
		If you include the argument 'chromosome_location = True' then the method will return the location of the substitutions on the chromosome.\
		If you add basequality=30 then all the substitutions with a basequality lower than 30 will be removed. If you set filtersubs="TC" then\
		only T to C conversions will be kept and others will be removed.\
		All are 0-based positions"""
		if self.__substitutions:
			subs = list()
			for i in self.__substitutions:
				position = i[0]
				subs.append(position)
			if chromosome_location:
				return [y+self.__line.pos for y in subs]
			else:
				if self.__read_type == "S":
					if self.__strand_query == "F":
						return subs
					if self.__strand_query == "R":
						return [-(y+1) for y in subs]
				elif self.__read_type == "L":
					if self.__strand_query == "F":
						return subs
					if self.__strand_query == "R":
						return [-(y+1) for y in subs]
				elif self.__read_type == "R":
					if self.__strand_query == "F":
						return [-(y+1) for y in subs]
					else:
						return subs
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
						newmutslist.append((position,nucleotide))
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
						newmutslist.append((position,nucleotide))
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
							mutation = self.sequence()[-(position+1)]
							actual	 = reverse_complement(nucleotide)
					string = "%s%s" % (actual.upper(),mutation.upper())
					if string == filter:
						newmutslist.append(subs)		# keep only those substitutions that match your criteria
				self.__substitutions = newmutslist
				if newmutslist:
					return True
				else:
					return False
			else:
				return False
		else:
			return False
					
	def subsBaseQualFilter(self,basequality=0):
		""" checks the base quality of substitutions in the substitutions list. Returns a filtered list """
		for subs in sorted(self.__substitutions):
			if self.baseQuality(subs[0]) < basequality:
				self.__substitutions.remove(subs)
		return True

	def baseQuality(self,nucl_nr,qualtype="L"):
		""" This method returns the basequality value (an integer, NOT ASCI!) at position nucl_nr. Usage: base_quality(24)
		You need to include format of the quality scoring, for example: qualtype="sanger" or qualtype="illumina
		S - Sanger		  Phred+33,	 raw reads typically (0, 40)
		X - Solexa		  Solexa+64, raw reads typically (-5, 40)
		I - Illumina 1.3+ Phred+64,	 raw reads typically (0, 40)
		J - Illumina 1.5+ Phred+64,	 raw reads typically (3, 40) with 0=unused, 1=unused, 2=Read Segment Quality Control Indicator (bold) 
		L - Illumina 1.8+ Phred+33,	 raw reads typically (0, 41)
		Default is L """
		quality = self.__qual
		if len(quality) > 1:
			if nucl_nr > len(quality):
				corr_nr = nucl_nr - self.__line.pos
				if corr_nr < 0:
					raise BaseQualityError("\n\ncould not calculate the base-quality for nucleotide position %d in read %s\nQuality length\t%s\nposition\t%s" % (nucl_nr,self.__line.qname,len(quality),nucl_nr))
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
		""" This method returns a list of chromosomal coordinates for all the mutations found in a read sequence"""
		mutations = self.__substitutions + self.__insertions + self.__deletions
		if mutations:
			return mutations
		else:
			return None
							
	def sequence(self):
		""" Returns the sequence of the reads. The orientation depends on whether single end or paired
		end sequencing was performed and to which strand the read was mapped. Note that in the SAM file all 
		mapped reads are represented on the forward genomic strand. The bases are reverse complemented from the 
		unmapped read sequence and the quality scores and cigar strings are recorded consistently with the bases. """
		if self.__read_type == "S" or self.__read_type == "L":
			if self.__strand_query == "F":
				return self.__seqquery
			else:
				return reverse_complement(self.__seqquery)
		elif self.__read_type == "R":
			if self.__strand_query == "F":
				return reverse_complement(self.__seqquery)
			else:
				return self.__seqquery

	def uniqueAlnLocation(self):
		""" Returns 'True' if a read has only one genomic location. Otherwise returns 'False''"""
		if self.__hit_repeat == "U":
			return True
		else:
			return False
					
	def seq_ID(self):
		""" Returns the sequence identification number of the read"""
		if self.__line.qname.startswith(">"):
			return self.__line.qname[1:]
		else:
			return self.__line.qname

	def read_type(self):
		""" Rreturns the read_type indicator ("S" = single end read; "L" or "R" indicate paired end reads)"""
		return self.__read_type
	
	def align_score(self):
		""" Returns the Phred format alignment score 10log10(P(R|Ai)).
		For status of 'R' and when not report alignment locations for repeats,
		the alignment score becomes the number of alignments to the read.
		For paired end the alignment score includes the fragment length penalty"""
		if self.__alignscore:
			return self.__alignscore
		else:
			return 0

	def alignScoreThreshold(self,number):
		""" Bool method. Checks whether the alignment score is smaller or equal to the to a threshold set by the
		user. If the alignment score is smaller than the threshold, the method returns 'False' else it returns 'True' """
		if number > self.__alignscore:
			return False
		else:
			return True

	def align_quality(self):
		""" MAPping Quality (phred-scaled posterior probability that the mapping position of this read is incorrect)
		Field MAPQ considers pairing in calculation if the read is paired. Providing MAPQ is recommended. If such a
		calculation is difficult, 255 should be applied, indicating the mapping quality is not available."""
		if int(self.__line.mapq):
			return int(self.__line.mapq)
		else:
			return 0

	def alignQualityThreshold(self,number):
		""" Checks whether the alignment quality is smallor or equal to the to a threshold set by the
		user. If the alignment quality is smaller than the threshold, the method returns 'False' else it returns 'True' """
		if number > int(self.__line.mapq):
			return False
		else:
			return True

	def lengthThreshold(self,number):
		""" Tests whether the length of the read sequence is smaller or equal to a maximum length
		threshold set by the user. If the read is smaller than the threshold the method returns 'True', else
		it returns 'False' """
		if number > len(self.__seqquery):
			return True
		else:
			return False

	def unique_hits(self):
		""" Returns R or U. R indicates that the read was mapped to multiple genomic locations.
		U indicates that the read mapped to only one location on the genome"""
		if self.__num_of_align == 1:
			return "U"
		else:
			return "R"
					
	def sequenceAlignmentLocations(self):
		""" Returns the number of alignments to the read"""
		return self.__num_of_align

	def read_start(self):
		""" Returns a left most 0-based start position of the read on the chromosome"""
		if self.__line.pos >= 0:
			return self.__line.pos	# although SAM start coordinates are 1-based, pysam coordinates are ALWAYS 0-based!!!
		else:
			return None

	def read_end(self):
		""" Returns the 0-based end position of the read on the chromosome"""
		if self.__line.pos >= 0:
			return self.__line.pos + len(self.__seqquery)
		else:
			return None

	def read_start_paired(self):
		""" Returns the left most 0-based start position of the paired read, if there is one"""
		if self.__line.mpos >= 0:
			return self.__line.mpos # although SAM start coordinates are 1-based, pysam coordinates are ALWAYS 0-based!!!
		else:
			return None
					
	def read_end_paired(self):
		""" Returns the 0-based end position of the paired read, if there is one"""
		if self.__seqmate:
			if self.__line.mpos <= self.__line.pos:
				return self.__line.mpos + len(self.__seqmate) - 1
			else:
				return None 
									   
	def paired_sequence(self,distance=1000):
		""" This BOOL method returns TRUE if the read has a paired read mapped to the same chromosomal location"""
		if self.__line.is_paired and self.__line.mpos >= 0 and not self.__line.mate_is_unmapped and self.__line.isize > -(distance) and self.__line.isize < distance:
			return True
		else:
			return False
					
	def strand(self):
		""" Returns the strand of the chromosome ("F" = plus, "R" = minus strand) the read was mapped to
		Note that for paired end reads the strand of the reverse sequencing reaction will be reversed"""
		if self.__read_type == "R":
			return self.__strand_mate
		else:
			return self.__strand_query

	def strand_paired(self):
		""" Returns the strand of the paired read if there is one"""
		if self.__line.is_paired and self.__strand_mate:
			return self.__strand_mate
		else:
			return None
	
	def chr_ID(self):
		""" Returns the chromosome the read sequence was mapped to"""
		return self.__rname
	
	def seq_length(self):
		""" Returns the length of the read sequence"""
		return len(self.__seqquery)

	def fasta(self):
		""" Returns the read ID and read sequence in the fasta format"""
		if self.__line.qname:
			fasta =	 ">%s\n%s" % (self.__line.qname,self.__seqquery)
			return fasta
	
	def tab(self):
		""" Returns the read ID and read sequence in the tab delimited format"""
		if self.__line.qname:
			tab =  "%s\t%s" % (self.__line.qname,self.__seqquery)
			return tab