#!/usr/bin/python

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2019"
__version__     = "0.0.4"
__credits__     = ["Sander Granneman"]
__maintainer__  = "Sander Granneman"
__email__       = "sgrannem@staffmail.ed.ac.uk"
__status__      = "Production"

##################################################################################
#
#	Aligner
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

import re
import bisect
import numpy as np
from collections import defaultdict
from pyCRAC.Classes.Exceptions import *
from pyCRAC.Parsers import ParseAlignments
from pyCRAC.Methods import strand_converter,getfilename,reverse_complement


def highlightMutations(sequence,substitutions,deletions):
	""" Corrects the sequence based on the substitutions and deletions information using info from GTF file data. 
	The substitutions and deletions should be 0-based positions of the read and insertions should have been removed"""
	nucleotides = list(sequence)
	if deletions:
		for position in deletions:
			nucleotides.insert(position,"-")
	if substitutions:
		for position in substitutions:
			nucleotides[position] = nucleotides[position].lower()
	return ''.join(nucleotides)

def seqStart(string):
	"""determines the position of the first nucleotide in a string"""
	a = re.search(r'[atgcnATGCN]',string)
	if a.start():
		return a.start()
	else:
		return 0

def sortByHeadGaps(list_input):
	"""sorts the sequences with head and tail gaps by the number of head gaps"""
	a = [(seqStart(keys.split('\n')[1]),keys) for keys in list_input]
	a.sort()
	return [i[1] for i in a]

def getHeadAndTailGaps(itercoordinates,start,end,gene_strand):
	"""calculates the number of head and tail gaps needed for proper alignment"""
	head = str()
	tail = str()
	index_up = bisect.bisect_left(itercoordinates,start)
	index_down = bisect.bisect_right(itercoordinates,end-1) 
	if gene_strand == "+":
		head = "-" * index_up
		tail = "-" * (len(itercoordinates) - index_down)
	elif gene_strand == "-":
		head = "-" * (len(itercoordinates) - index_down)
		tail = "-" * index_up
	else:
		raise InputError("\n\ngetHeadAndTailGaps method did not receive any strand information.\nPlease double check your input.\n")
	return (head,tail)
	
class ReadAligner():
	def __init__(self,data_file,gtf,genes,file_type="novo",sequence="genomic",blocks=False,base_quality=-50,ignorestrand=False,debug=False):
		""" initializes the class attributes. The ReadAligner class requires at least the path to the data file, a GTF2 object with genes and chromosomes stored.
		If the file type of the data file is not a .novo file then the file_type flag needs to be set to sam or gtf. """
		self.sense_seqs			= defaultdict(list)
		self.anti_sense_seqs	= defaultdict(list)
		self.file_name			= data_file
		self.file_list			= list()
		self.file_type			= file_type.lower()
		self.genes				= genes
		self.data				= None
		self.__blocksremoved	= blocks
		self.__seq_line			= defaultdict(str)
		self.__sequence			= sequence
		self.__gene_sequence	= defaultdict(str)
		self.__itercoordinates	= defaultdict(list)
		self.__alnfile			= None	
		self.__ignorestrand		= ignorestrand
		self.__gtf				= gtf
		if debug: self.file_list.append(debug)
		self.__supported_filetypes = ["novo","sam","gtf"] # index = [0,1,2]; [:2] = novo and sam, [2] = gtf .
		self.__determineFileType(data_file,file_type,debug)

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
			raise FileTypeError("\n\nThe file type % is not supported by ReadAligner, please choose from the following options: %s\n" % (file_type, ",".join(self.__supported_filetypes))) 
			
#------------------------------------	aligning reads	------------------------------------- 

	def alignReads(self,length=1000,align_quality=0,align_score=0,MAX=-1,limit=5000,unique=False,muts_filter=None):
		"""This method aligns reads from a Novoalign output file (.novo extension) to reference sequences, supplied in a list file
		input required: genes.list file and novoalign file. Options: self,length=1000,flank_seq=0,align_quality=0,align_score=0,correct_sequence=True,MAX=500,sequence="genomic",insertions=False"""
		head_gaps = str()
		line_out  = str()
		tail_gaps = str()
		counter	  = defaultdict(int)
		  
#------------------------------------ if the input file is a novo or sam file -----------------------------------------------	  

		if self.file_type in self.__supported_filetypes[:2]:
			while self.data.getRead(align_quality=align_quality,align_score=align_score,maximum=MAX,blocks=self.__blocksremoved,length=length,unique=unique,force_single_end=True,muts_filter=muts_filter):
				if not self.genes: break
				if muts_filter and not self.data.hasmutation: continue
				for gene in self.genes:
					if counter[gene] == limit: self.genes.remove(gene)
					if self.__gtf.chromosome(gene) == self.data.chromosome:
						overlap = list(self.__itercoordinates[gene][np.logical_and(self.__itercoordinates[gene] >= self.data.read_start,self.__itercoordinates[gene] < self.data.read_end)])
						if len(overlap) == len(self.data.read_seq):
							counter[gene] += 1
							(head_gaps,tail_gaps) = getHeadAndTailGaps(self.__itercoordinates[gene],self.data.read_start,self.data.read_end,self.__gtf.strand(gene))
							if strand_converter(self.data.strand) == self.__gtf.strand(gene):
								dashed_seq = head_gaps+self.data.read_seq+tail_gaps
								line_out = ">%s\n%s" % (self.data.read_seq_ID,dashed_seq)
								self.sense_seqs[gene].append(line_out)		  
									
							elif self.__ignorestrand:
								dashed_seq = head_gaps+reverse_complement(self.data.read_seq)+tail_gaps
								line_out = ">%s\n%s" % (self.data.read_seq_ID,dashed_seq)
								self.sense_seqs[gene].append(line_out)	 
		
							elif strand_converter(self.data.strand) != self.__gtf.strand(gene):
								dashed_seq = head_gaps+reverse_complement(self.data.read_seq)+tail_gaps
								line_out = ">%s\n%s" % (self.data.read_seq_ID,dashed_seq)
								self.anti_sense_seqs[gene].append(line_out)
															
#------------------------------------ if the input file is a pyReadCounter/pyMotif GTF file ----------------------------------- 

		elif self.file_type == self.__supported_filetypes[2]:
			while self.data.readLineByLine():
				if not self.genes: break
				genesinboth = set(self.genes) & set(self.data.genes)
				if genesinboth:
					for gene in genesinboth:
						if counter[gene] == limit: 
							self.genes.remove(gene)
						if self.__gtf.chromosome(gene) == self.data.chromosome:
							sequence = self.__gtf.sequence(self.data.chromosome,strand_converter(self.data.strand),self.data.read_start,self.data.read_end)
							substitutions = [i - self.data.read_start for i in self.data.substitutions] 
							deletions	  = [i - self.data.read_start for i in self.data.deletions]
							self.data.read_seq	  = highlightMutations(sequence,substitutions,deletions)
							self.data.read_seq_ID = "%s_%s_%s" % (gene,self.data.read_start,self.data.read_end)
							overlap = list(self.__itercoordinates[gene][np.logical_and(self.__itercoordinates[gene] >= self.data.read_start,self.__itercoordinates[gene] < self.data.read_end)])
							if len(overlap) == len(self.data.read_seq):
								counter[gene] += 1
								(head_gaps,tail_gaps) = getHeadAndTailGaps(self.__itercoordinates[gene],self.data.read_start,self.data.read_end,self.__gtf.strand(gene))
								if strand_converter(self.data.strand) == self.__gtf.strand(gene):
									dashed_seq = head_gaps+self.data.read_seq+tail_gaps
									line_out = ">%s\n%s" % (self.data.read_seq_ID,dashed_seq)
									self.sense_seqs[gene].append(line_out)		  
										
								elif self.__ignorestrand:
									dashed_seq = head_gaps+reverse_complement(self.data.read_seq)+tail_gaps
									line_out = ">%s\n%s" % (self.data.read_seq_ID,dashed_seq)
									self.sense_seqs[gene].append(line_out)	 
			
								elif strand_converter(self.data.strand) != self.__gtf.strand(gene):
									dashed_seq = head_gaps+reverse_complement(self.data.read_seq)+tail_gaps
									line_out = ">%s\n%s" % (self.data.read_seq_ID,dashed_seq)
									self.anti_sense_seqs[gene].append(line_out)										 
														  

	#------------------------------------ printing the alignments -------------------------------------

	def __createFileHandles(self,gene,file_type,file_extension="fasta"):
		""" does what it says """
		filename = str()								 
		filename = "%s-%s_%s_%s_%s.%s" % (file_type,self.__insert,gene,self.__sequence,getfilename(self.file_name),file_extension)
		self.file_list.append(filename)
		return filename
	
	def printFastaWithAlignments(self,out_file=False):
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
		if not self.sense_seqs and not self.anti_sense_seqs:
			raise NoResultsError("\n\nCould not find any reads that matched your criteria.\nPlease double check your settings.\n")
		file_out = None
		if out_file:
			if out_file == "default":
				file_name = "%s_%s_%s.fasta" % (self.__insert,getfilename(self.file_name),self.__sequence)
			else:
				file_name = out_file
			file_out = open(file_name,"w")
			self.file_list.append(file_name)
			for gene in self.__gene_sequence:
				if self.sense_seqs[gene]:
					sorted_tuple_list = sortByHeadGaps(self.sense_seqs[gene])
					file_out.write("### %s sense %s ###\n" % (gene,self.__insert))
					file_out.write("%s\n" % self.__seq_line[gene])
					for lines in sorted_tuple_list:
							file_out.write("%s\n" % lines)
					file_out.write("\n\n")
				if self.anti_sense_seqs[gene]:
					sorted_tuple_list = sortByHeadGaps(self.anti_sense_seqs[gene])
					file_out.write("### %s anti-sense %s ###\n" % (gene,self.__insert))
					file_out.write("%s\n" % self.__seq_line[gene])
					for lines in sorted_tuple_list:
							file_out.write("%s\n" % lines)
					file_out.write("\n\n")	
			file_out.close()
		else:
			for gene in self.__gene_sequence:
				if self.sense_seqs[gene]:
					sorted_tuple_list = sortByHeadGaps(self.sense_seqs[gene])
					file_type = "sense"
					file_name = self.__createFileHandles(gene,file_type,file_extension="fasta")
					file_out  = open(file_name,"w")
					file_out.write("%s\n" % self.__seq_line[gene])
					for lines in sorted_tuple_list:
							file_out.write("%s\n" % lines)
					file_out.close()

				if self.anti_sense_seqs[gene]:
					sorted_tuple_list = sortByHeadGaps(self.anti_sense_seqs[gene])
					file_type = "anti_sense"
					file_name = self.__createFileHandles(gene,file_type,file_extension="fasta")
					file_out  = open(file_name,"w")								 
					file_out.write("%s\n" % self.__seq_line[gene])
					for lines in sorted_tuple_list:
							file_out.write("%s\n" % lines)
					file_out.close()