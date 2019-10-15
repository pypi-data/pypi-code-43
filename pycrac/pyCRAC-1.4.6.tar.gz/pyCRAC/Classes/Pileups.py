#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.1.4"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	Pileups
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
import numpy as np
import time
from collections import defaultdict
from pyCRAC.Parsers import ParseAlignments
from pyCRAC.Classes.Exceptions import *
from pyCRAC.Methods import strand_converter,reverse_strand,getfilename

class Pileup():
	"""Generates tabular pileup files for novo, sam or pyReadCounters/pyMotif GTF files.
	Requires a GTF annotation file, tab delimited genomic reference 
	sequence and alignment file"""
	def __init__(self,data_file,gtf,genes,file_type="novo",sequence="genomic",muts_filter=None,debug=False):
		self.substitutions		= defaultdict(int)
		self.deletions			= defaultdict(int)
		self.gene_hits			= defaultdict(int)
		self.hits				= defaultdict(int)
		self.reads_in_cluster	= defaultdict(list)
		self.data				= None
		self.genes				= genes
		self.file_type			= file_type.lower()
		self.file_name			= data_file
		self.file_list			= list()
		self.orientation		= "sense"
		self.__muts_filter		= muts_filter
		self.__gtf				= gtf
		self.__gene_sequence	= defaultdict(str)
		self.__seq_line			= defaultdict(str)
		self.__itercoordinates	= defaultdict(list)
		self.__sequence			= sequence
		self.__supported_filetypes = ["novo","sam","gtf"] # index = [0,1,2]; [:2] = novo and sam, [2] = gtf .
		self.__determineFileType(data_file,file_type,debug)
		self.__orientations = ["sense","anti-sense"]

		for gene in self.genes:						   
			if self.__sequence == "coding":
				self.__gene_sequence[gene] = gtf.codingSequence(gene)
			elif self.__sequence == "genomic":
				self.__gene_sequence[gene] = gtf.genomicSequence(gene)
			self.__itercoordinates[gene] = gtf.geneIterCoordinates(gene,coordinates=sequence,output="numpy")
			self.__seq_line[gene] = ">%s\n%s" % (gene,self.__gene_sequence[gene])
			
	def __determineFileType(self,data_file,file_type,debug):
		"""Checks the file type of the data file"""
		if self.file_type in self.__supported_filetypes[:2]:
			self.data = ParseAlignments.ParseAlignmentFile(data_file,file_type,debug=debug)
			self.data.gtfdatatype = None
		elif self.file_type == self.__supported_filetypes[2]:
			self.data = ParseAlignments.ParseCountersOutput(data_file)
		else:
			raise FileTypeError("\n\nThe file type % is not supported by pyPileup, please choose from the following options: %s\n" % (file_type, ",".join(self.__supported_filetypes))) 
	
#--------------------------------------------- Processing alignment files ---------------------------------------------------

	def countGeneNucleotideCoverage(self,unique=False,distance=1000,length=1000,limit=-1,max_reads=-1,align_quality=0,align_score=0,min_overlap=1,blocks=False,ignorestrand=False,fiveends=False,threeends=False,orientation="sense"):
		""" Takes the alignment file read sequences and aligns them to selected reference sequences"""	
		assert orientation in self.__orientations, "Error! Orientation %s is not recognized. Please choose %s" % (orientation, " or ".join(self.__orientations))
		self.orientation = orientation
		self.data.number_of_reads = 1
		self.__align_quality = align_quality
		self.__align_score	 = align_score
		self.__length		 = length
		self.__blocksremoved = blocks
		overlap = list()

#------------------------------------ if the input file is a novo or sam file -----------------------------------------------
			
		if self.file_type in self.__supported_filetypes[:2]:
			while self.data.getRead(align_quality=align_quality,align_score=align_score,maximum=max_reads,blocks=blocks,distance=distance,length=length,unique=unique,muts_filter=self.__muts_filter):		# novo or sam input file
				if not self.genes:
					break
				strand = strand_converter(self.data.strand)
				if orientation == "anti-sense":
					strand = reverse_strand(strand)
				for gene in self.genes:
					if self.data.chromosome == self.__gtf.chromosome(gene) and strand == self.__gtf.strand(gene):
						overlap = list()
						if fiveends:				# will report the first nucleotide upstream of the
							if self.__gtf.strand(gene) == "+":
								if self.data.read_start in self.__itercoordinates[gene]:
									overlap = [self.data.read_start]
							else:
								if self.data.read_end in self.__itercoordinates[gene]:
									overlap = [self.data.read_end-1]	
							min_overlap = 1
						elif threeends:
							if self.__gtf.strand(gene) == "+":	  
								if self.data.read_end in self.__itercoordinates[gene]:
									overlap = [self.data.read_end-1]
							else:
								if self.data.read_start in self.__itercoordinates[gene]:
									overlap = [self.data.read_start]
							min_overlap = 1
						else:
							overlap = list(self.__itercoordinates[gene][(self.__itercoordinates[gene] >= self.data.read_start) & (self.__itercoordinates[gene] < self.data.read_end)])
						if len(overlap) >= min_overlap:
							if self.gene_hits[gene] == limit:
								self.genes.remove(gene)
							else:
								for i in overlap:
									self.hits[gene,i] += self.data.number_of_reads
								for j in self.data.substitutions:
									self.substitutions[gene,j] += self.data.number_of_reads
								for k in self.data.deletions:
									self.deletions[gene,k] += self.data.number_of_reads
								self.gene_hits[gene] += self.data.number_of_reads

#------------------------------------ if the input file is a pyReadCounter/pyMotif/pyClusterReads GTF file -----------------------------------

		elif self.file_type in self.__supported_filetypes[2]:
			while self.data.readLineByLine():
				if not self.genes:
					break
				strand = strand_converter(self.data.strand)
				if orientation == "anti-sense":
					strand = reverse_strand(strand)
				genesinboth = set(self.genes) & set(self.data.genes)
				if genesinboth:
					for gene in genesinboth:
						if self.data.chromosome == self.__gtf.chromosome(gene) and strand == self.__gtf.strand(gene):
							if fiveends:				# will report the first nucleotide upstream of the
								if self.__gtf.strand(gene) == "+":
									if self.data.read_start in self.__itercoordinates[gene]:
										overlap = [self.data.read_start]
								else:
									if self.data.read_end in self.__itercoordinates[gene]:
										overlap = [self.data.read_end-1]	
								min_overlap = 1
							elif threeends:
								if self.__gtf.strand(gene) == "+":	  
									if self.data.read_end in self.__itercoordinates[gene]:
										overlap = [self.data.read_end-1]
								else:
									if self.data.read_start in self.__itercoordinates[gene]:
										overlap = [self.data.read_start]
								min_overlap = 1
							else:
								overlap = list(self.__itercoordinates[gene][(self.__itercoordinates[gene] >= self.data.read_start) & (self.__itercoordinates[gene] < self.data.read_end)])
							if len(overlap) >= min_overlap:
								for i in overlap:
									self.hits[gene,i] += self.data.number_of_reads
								for j in self.data.substitutions:
									self.substitutions[gene,j] += self.data.number_of_reads
								for k in self.data.deletions:
									self.deletions[gene,k] += self.data.number_of_reads
								self.gene_hits[gene] += self.data.number_of_reads

#-------------------------------------------------------- Printing to output files --------------------------------------------------------

	def __createFileHandles(self,gene,file_type,file_extension="pileup"):
		""" does what it says """
		filename = str()							  
		filename = "%s-%s_%s_%s_%s.%s" % (file_type,self.__insert,gene,self.__sequence,getfilename(self.file_name),file_extension)
		self.file_list.append(filename)
		return filename

	def printPileup(self,out_file=None):
		""" does what it says """
		if not self.gene_hits:
			raise NoResultsError("\n\nNo hits were found. Are you sure you used the right options?\nDid you set the file type option (novo,sam,gtf)?\nDid you include the correct GTF file?\nDid you include the correct tab file?\nAre the chromosome names in the novo/SAM file the same as in the GTF reference file?\n")
		file_out  = defaultdict(str)
		self.__insert = "reads"
		if self.data.gtfdatatype:
			if self.data.gtfdatatype == "blocks":
				self.__insert = "cDNAs"
			elif self.data.gtfdatatype == "clusters":
				self.__insert = "clusters"
			elif self.data.gtfdatatype == "peaks":
				self.__insert = "peaks"
		else:
			if self.__blocksremoved:
				self.__insert = "cDNAs"
		if out_file:						## in Galaxy all the pileups are printed into a single file, whereas in the command line sense and anti-sense hits are printed in seperate files
			file_name = str()
			if out_file == "default":
				file_name = open(self.__createFileHandles("genes","all"),"w")
			else:
				file_name = open(out_file, "w")
			for gene in sorted(self.gene_hits):
				file_out[gene] = file_name
		else:
			for gene in sorted(self.gene_hits):
				file_out[gene] = open(self.__createFileHandles(gene,self.orientation),"w")
		for gene in sorted(self.gene_hits):
			if self.__gtf.strand(gene) == "-":
				self.__itercoordinates[gene] = self.__itercoordinates[gene][::-1]
			file_out[gene].write("# %s\n" % (' '.join(sys.argv)))
			file_out[gene].write("# %s\n" % (time.ctime()))
			file_out[gene].write("# align quality threshold:\t%s\n# align score threshold:\t%s\n# read length threshold:\t%s\n" % (self.__align_quality,self.__align_score,self.__length))
			file_out[gene].write("# total number of %s:\t%s\n" % (self.__insert,self.data.total_reads))
			file_out[gene].write("# total number of mapped %s:\t%s\n" % (self.__insert,self.data.mapped_reads))
			file_out[gene].write("# total number paired reads:\t%s\n" % (self.data.paired_reads))
			file_out[gene].write("# total number single reads:\t%s\n" % (self.data.single_reads))
			file_out[gene].write("# total %s %s %s found:\t%s\n" % (self.orientation,gene,self.__insert,self.gene_hits[gene]))
			file_out[gene].write("# gene\tposition\tnucleotide\thits\tsubstitutions\tdeletions\n")
			try:
				for rank,numbers in enumerate(self.__itercoordinates[gene],start=1):
					file_out[gene].write("%s\t%s\t%s\t%d\t%d\t%d\n" % (gene, rank, self.__gene_sequence[gene][rank-1], self.hits[gene,numbers],self.substitutions[gene,numbers],self.deletions[gene,numbers]))
			except IndexError:
				sys.stderr.write("IndexError for gene %s with gene length %s at position %s\n" % (gene,len(self.__gene_sequence[gene]),rank-1))
				pass
			file_out[gene].write("\n\n")
		for i in file_out:
			file_out[i].close()
