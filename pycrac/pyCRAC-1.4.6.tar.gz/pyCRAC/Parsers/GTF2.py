#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "1.6.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	GTF2.py
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
import re
import numpy as np
import time
import copy
import itertools
from collections import defaultdict
from pyCRAC.Classes.Exceptions import *
from pyCRAC.Classes.NGSFormatWriters import NGSFileWriter
from pyCRAC.Methods import splitter,reverse_complement,splitString
from pyCRAC.Parsers.fasta2dict import *
from pyCRAC.Parsers.tab2dict import *

#--------------------------------------------------- GenomeSeq class ---------------------------------------------------#

class GenomeSeq():
	""" Takes fasta and tab files and converts them into dictionary """
	def __init__(self):
		self.chr_seq = defaultdict(str)
			
	def read_FASTA(self,fasta_file,chromosomes=[]):
		""" Generates a dictionary from a fasta file"""
		self.chr_seq = Fasta2Dict(fasta_file,ids=chromosomes)
			
	def read_TAB(self,tab_file,chromosomes=[]):
		""" Generates a dictionary from a tab file"""
		self.chr_seq = Tab2Dict(tab_file,ids=chromosomes)
			
	def chromosome_list(self):
		""" returns a list of chromosome names"""
		return [keys for keys in sorted(self.chr_seq)]
							
	def chromosome_length(self,chromosome):
		""" returns the length of a chromosome"""
		if chromosome in self.chr_seq:
			return len(self.chr_seq[chromosome])
		else:
			raise LookupError("I could not find %s in the chromosome list\n" % (chromosome))
					
	def sequence(self,chromosome,strand,upstream,downstream):
		"""returns the nucleotide sequence from "chromosome" using upstream and downstream coordinates.Usage: sequence(chromosome,strand,upstream,downstream)"""
		sequence = str()
		try:
			sequence = self.chr_seq[chromosome][upstream:downstream]
		except IndexError:
			if upstream	  < 0 : upstream = 0
			if downstream > len(chromosome): downstream == len(chromosome)
			sequence = self.chr_seq[chromosome][upstream:downstream]
			
		if not sequence:
			raise LookupError("I could not find a sequence for chromosome %s and coordinates %d-%d, please check your input\n" %(chromosome,upstream,downstream))
				
		if strand == "-" or strand == "R":
			return reverse_complement(sequence)
		else:
			return sequence

#--------------------------------------------------- Transcript class ---------------------------------------------------#

class Transcripts():
	"""A class to store transcript information"""
	def __init__(self):
		self.transcripts = dict()
		self.__features = ["exon","CDS","5UTR","3UTR"]
		self.__othersources	 = ["cluster","motif","reads"]
		self.__otherfeatures = ["start_codon","stop_codon"]
					
	def addTranscript(self,transcript_name,start,end,type,annotation,chromosome,strand,gene_name=None,gene_id=None,transcript_id=None):		# gene_name, gene_id and transcript_id are optional features
		"""method to add new transcripts to the self.transcripts dictionary"""
		if transcript_name not in self.transcripts:						# If the transcript dictionary for a particular transcript does not exist, make one and update the key values.
			self.transcripts[transcript_name] = {						# this dictionary is used to store transcript names and transcript information.
				'chromosome'	: chromosome,
				'gene_id'		: gene_id,
				'gene_name'		: gene_name,
				'protein_id'	: str(),
				'strand'		: strand,
				'annotations'	: set(),
				'exon'			: set(),
				'CDS'			: set(),
				'5UTR'			: list(),
				'3UTR'			: list(),
				'start_codon'	: tuple(),
				'stop_codon'	: tuple(),
				'transcript_id' : transcript_id
				}

		self.transcripts[transcript_name]['annotations'].add(annotation)
		if type in self.__features[:2]:									# the features listed in self.__features are commonly found in GTF files. 
			self.transcripts[transcript_name][type].add((start,end))
		elif type in self.__features[2:]:								
			self.transcripts[transcript_name][type].append((start,end))
		if annotation in self.__othersources:							# when processing pyClusterReads, pyMotif or pyReadCounters GTF files
			self.transcripts[transcript_name]['exon'].add((start,end))

		return True

#--------------------------------------------------- Genes class ---------------------------------------------------#

class Genes():
	"""A class to store gene information"""
	def __init__(self):
		counter = 0
		self.__features = ["exon","CDS","5UTR","3UTR"]
		self.__othersources	 = ["cluster","motif","reads"]
		self.genes = dict()
					
	def addGene(self,gene_name,start,end,type,annotation,chromosome,strand,gene_id=None,transcript_name=None):	# gene_id, transcript_name and transcript_id are optional features
		"""method to add new genes to the to the self.genes dictionary"""
		if gene_name not in self.genes:									# If the gene dictionary for a particular gene does not exist, make one and update the key values.
			self.genes[gene_name] = {									# this dictionary is used to store gene names and gene information.									   
				'chromosome'	: chromosome,
				'gene_id'		: gene_id,
				'strand'		: strand,
				'exon'			: set(),
				'CDS'			: set(),
				'5UTR'			: list(),
				'3UTR'			: list(),
				'transcripts'	: set(),
				'annotations'	: set()
				}

		self.genes[gene_name]['annotations'].add(annotation)
		if transcript_name:
			self.genes[gene_name]['transcripts'].add(transcript_name)
		if type in self.__features[:2]:										# the features listed in self.__features are commonly found in GTF files. 
			self.genes[gene_name][type].add((start,end))
		elif type in self.__features[2:]:
			self.genes[gene_name][type].append((start,end))
		if annotation in self.__othersources:								# when processing pyClusterReads, pyMotif or pyReadCounters GTF files
			self.genes[gene_name]['exon'].add((start,end))
		return True

#--------------------------------------------------- GTF2 class ---------------------------------------------------#

class Parse_GTF(GenomeSeq,Genes,Transcripts):
	"""reads the GTF file and stores the info into memory. You need to supply a GTF file name (including path)
	The 'ranges' option allows you to manually set the lengths of the 5' and 3' UTR or flanking sequences."""
	def __init__(self):		 
		"""initialises the class attributes"""
		GenomeSeq.__init__(self)
		Genes.__init__(self)
		Transcripts.__init__(self)
		self.__ranges	 = int()
		self.chromosomes = set()
		self.gtfsources	 = set()
			
	def read_GTF(self,gtf_file,ranges=0,genes=[],source=None,transcripts=True):		# you can set 'ranges' at this stage or later when running methods.
		"""parses the GTF file"""
		self.__ranges = ranges
		with open(gtf_file) as gtf:
			for line in gtf:
				try:
					if line[0] == "#": continue
					Fld = line.strip('\n').split('\t')	  
					chromosome,annotation,type,start,end,strand = Fld[0],Fld[1],Fld[2],int(Fld[3])-1,int(Fld[4]),Fld[6]
					[g_name,g_id,t_name,t_id,g_biotype] = self.getAttributes(Fld[8].strip())
					if g_biotype: annotation = g_biotype							# the more recent GTF files from ENSEMBL have "gene_biotype" in the comments section. Use this rather than column 2 (source)
					if source and source != annotation: continue					# in case you only want to analyse genes associated with specific annotations, such as protein_coding.
					if genes and g_name not in genes: continue						# in case you only want to look at a handfull of genes from the gtf file.
					if g_name == "no_matches": continue								# entries containing "no_matches" can be found in the pyReadCounters output files and these should be ignored.
					self.chromosomes.add(chromosome)
					self.gtfsources.add(annotation)			
					self.addGene(		   
								g_name,												# adding gene names 
								start,
								end,
								type,
								annotation,
								chromosome,
								strand,
								gene_id=g_id,
								transcript_name=t_name,
								)
					if transcripts and t_name:										# transcript positions can also be added if needed				
						self.addTranscript(	   
								t_name,
								start,
								end,
								type,
								annotation,
								chromosome,
								strand,
								gene_name=g_name,
								gene_id=g_id,
								transcript_id=t_id
								)
				except IndexError:
					sys.stderr.write("\nIndexError at line:\n%s\n" % line)
					pass
			
#------------------------------------------------------------------------------ API ------------------------------------------------------------------------------	   

	def getAttributes(self,attributes):
		"""takes the attributes from column 9 in the GTF file and extracts gene_name,transcript_name, etc information"""
		info			= attributes.split(";")
		gene_id			= str()
		transcript_id	= str()
		gene_name		= str()
		transcript_name = str()
		gene_biotype    = str()
		for i in info:
			i = i.strip()
			if i.startswith('gene_id'):
				gene_id = splitter(i)	   
			elif i.startswith('transcript_id'):
				transcript_id = splitter(i)
			elif i.startswith('gene_name'):
				gene_name = splitter(i)
			elif i.startswith('transcript_name'):
				transcript_name = splitter(i)
			elif i.startswith('gene_biotype'):
				gene_biotype = splitter(i)
						
		if not gene_name:
			gene_name = gene_id
		if not transcript_name:
			transcript_name = transcript_id
		return [gene_name,gene_id,transcript_name,transcript_id,gene_biotype]

	def printGeneFlankingCoordinatesAsGTF(self,output=None):
		""" For each gene in the genes dictionary it calculates its extremities based on exon coordinates and prints these out as a gtf file.
		This is useful when using bedtools to look for overlap between intervals and GTF annotation files."""
		if output: out = NGSFileWriter(output)
		out.write("##gff-version 2\n")
		for i in sorted(self.chromosomes):
			for j in sorted(self.chromosomeGeneCoordIterator(i)):
				for annotation in self.annotations(j[2]):
					out.writeGTF(i,annotation,"exon",j[0]-1,j[1],score=".",strand=self.strand(j[2]),frame=".",gene_name=j[2],transcript_name=j[2],gene_id=self.gene2orf(j[2]),transcript_id=self.gene2orf(j[2]),exon_number=None,comments=None)

	def strand(self,gene):
		"""returns the strand (watson or crick: "F" or "R") on which the query gene or ORF is located. Usage: strand("BET1L")"""
		if gene in self.genes:	
			return self.genes[gene]['strand']
		elif gene in self.transcripts:
			return self.transcripts[gene]['strand']
		else:
			raise LookupError("I could not find a strand for gene %s" % gene)
					
	def chromosome(self,gene):
		"""returns the chromosome name on which the query gene or ORF is located. Usage: chromosome("BET1L")"""
		if gene in self.genes:
			return self.genes[gene]['chromosome']
		elif gene in self.transcripts:
			return self.transcripts[gene]['chromosome']
		else:
			raise LookupError("I could not find a chromosome for gene %s" % gene)

	def gene2orf(self,gene):
		"""allows you to convert a gene name to an open reading frame (ORF) name. Usage gene2orf("BET1L")"""
		if gene in self.genes:
			return self.genes[gene]['gene_id']
		elif gene in self.transcripts:
			return self.transcripts[gene]['gene_id']
		else:
			return gene
						
	def orf2gene(self,gene_id):
		"""allows you to convert an open reading frame (ORF) name to a gene name. Usage orf2gene("ENSG00000177951")"""
		result = False
		for x in self.genes:
			if self.genes[x]['gene_id'] == gene_id:
				return x
		return gene_id

	def geneLength(self,gene,type="gene",ranges=0):
		"""returns the length of a gene or transcript. If type is 'gene', it returns the length of a gene_name.
		If type= 'transcript' it returns the length of a transcript_name. """
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		up,down = self.__calcExtremities(gene,gene_type=type,ranges=flank_seq)
		return down-up
	
	def annotations(self,gene):
		"""returns a list of annotations associated with a particular gene or transcript. Requires a gene or transcript name input"""
		if gene in self.genes:
			return self.genes[gene]['annotations']
		elif gene in self.transcripts:
			return self.transcripts[gene]['annotations']
		else:
			return None
					
	def geneTranscriptList(self,gene):
		"""returns a list of (alternatively spliced) transcripts associated with a gene"""
		assert self.genes[gene]['transcripts'], "\n\ncould not find any transcripts for %s\n" % gene
		return self.genes[gene]['transcripts']
			
	def __checkDict(self,gene,dictionary,chromosome=None,annotation=None,strand=None):
		"""checks the genes dictionary to see if it finds any genes that match the specified criteria:
		mapped to 'chromosome'? does it belong to 'annotation'? Is it located on strand 'strand'? 
		The dictionary should be self.genes or self.transcripts """
		results = list()
		if chromosome: results.append(dictionary[gene]['chromosome'] == chromosome)
		if annotation: results.append(annotation in dictionary[gene]['annotations'])
		if strand	 : results.append(dictionary[gene]['strand'] == strand)
		if False in results: 
			return False
		else: 
			return True
			
	def chromosomesTranscriptList(self,chromosome,annotation=None,strand=None):
		"""returns a list of transcripts located on a specified chromosome. One can also select genes with specific annotations or strands.
		Strand should be "+" or "-" and the annotation should be in the gtfsources list.
		Use the pyGetSourcesFromGTF.py script if you want to have a list of all annotations in your GTF file.
		
		Examples: 
		chromosomesTranscriptList("chrXII") = ["A","B","C","D"]
		chromosomesTranscriptList("chrXII",annotation="protein_coding") = ["A","C","D"]
		chromosomesTranscriptList("chrXII",annotation="protein_coding",strand="+") = ["A","D"]
		"""
		if annotation:	
			assert annotation in self.gtfsources, "\n\nthe specified annotation %s does not exist. Choices are:\n%s" % (annotation,"\n".join(self.gtfsources))
		if strand:
			strandoptions = ["+","-"]
			assert strand in strandoptions, "\n\nthe strand %s does not exist\n" % strand
		
		transcriptlist = [i for i in self.transcripts if self.__checkDict(i,self.transcripts,chromosome=chromosome,annotation=annotation,strand=strand)]
		assert transcriptlist, "\n\n Could not find any transcripts on chromosome %s\n" % chromosome
		return transcriptlist
					
	def chromosomesGenesList(self,chromosome,annotation=None,strand=None):
		"""returns a list of genes located on a specified chromosome. One can also select genes with specific annotations or strands.
		Strand should be "+" or "-" and the annotation should be in the gtfsources list.
		Use the pyGetSourcesFromGTF.py script if you want to have a list of all annotations in your GTF file.
		
		Example: 
		chromosomesGenesList("chrXII") = ["A","B","C","D"]
		chromosomesGenesList("chrXII",annotation="protein_coding") = ["A","C","D"]
		chromosomesGenesList("chrXII",annotation="protein_coding",strand="+") = ["A","D"]
		"""
		if annotation:
			assert annotation in self.gtfsources, "\n\nthe specified annotation %s does not exist. Choices are:\n%s" % (annotation,"\n".join(self.gtfsources))
		if strand:
			strandoptions = ["+","-"]
			assert strand in strandoptions, "\n\nthe strand %s does not exist\n" % strand
								
		genelist = [i for i in self.genes if self.__checkDict(i,self.genes,chromosome=chromosome,annotation=annotation,strand=strand)]
		assert genelist, "\n\n Could not find any genes on chromosome %s\n" % chromosome
		return genelist
			
	def __calcExtremities(self,gene,gene_type="gene",ranges=0):
		"""looks at all UTR and exon coordinates, puts them all together and returns the maximum and minimum values in a single tuple.
		if range is set to larger than zero, then UTR coordinates will be ignored"""
		sumlist = list()
		dictionary = dict()
		start = int()
		end	  = int()
		if gene_type == "gene":
			dictionary = self.genes
		elif gene_type == "transcript":
			dictionary = self.transcripts
		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)
		
		if ranges:
			sumlist = dictionary[gene]['exon'] | dictionary[gene]['CDS']
			if not sumlist:
				raise NoResultsError("\nNo exon or CDS coordinates available for gene %s. Please correct your GTF annotation file\n" % gene)
			flattenedlist = list(itertools.chain(*sumlist))
			try:
				start = min(flattenedlist) - ranges
				end	  = max(flattenedlist) + ranges
			except ValueError:
				sys.stderr.write("sumlist =  %s\nflattenedlist = %s\n" % (sumlist,flattenedlist))
			if start < 0: start = 0
		else:
			sumlist = dictionary[gene]['exon'] | dictionary[gene]['CDS'] | set(dictionary[gene]['5UTR']) | set(dictionary[gene]['3UTR'])
			flattenedlist = list(itertools.chain(*sumlist))
			try:
				start = min(flattenedlist)
				end	  = max(flattenedlist)
			except ValueError:
				sys.stderr.write("sumlist =  %s\nflattenedlist = %s\n" % (sumlist,flattenedlist))
		if not sumlist:
			raise NoResultsError("\nNo exon or CDS coordinates available for gene %s. Please correct your GTF annotation file\n" % gene)
		return (start,end)
		
	def genomicSequence(self,gene,ranges=0,format=None,split=False):
		"""returns the genomic sequence of transcripts/genes. 
		You need a gene name or ORF name (all UPPERCASE) and you can also set the "ranges" variable (i.e. ranges=50). 
		This will allow you to addd flanking sequences to the genomic sequence. 5UTR or 3UTR coordinates provided in the GTF file
		will automatically be included, unless the ranges value is higher than 0"""
		allowedformats = ["fasta","tab"]
		if format: assert format in allowedformats, "\nthe format you specified is not recognized, please use 'fasta' or 'tab'\n"
		output = str()
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		if gene in self.genes:
			chr_ID = self.genes[gene]['chromosome']
			if self.chr_seq[chr_ID]:
				(up,down) = self.__calcExtremities(gene,gene_type="gene",ranges=flank_seq)
				output = self.chr_seq[chr_ID][up:down]
				if self.genes[gene]['strand'] == "-":
					output = reverse_complement(output)
			else:
				raise NoSequenceError("No sequence information available for %s. Did you load the reference sequence using the read_TAB method?\n" % (gene))	
		elif gene in self.transcripts:
			chr_ID = self.transcripts[gene]['chromosome']
			if self.chr_seq[chr_ID]:
				(up,down) = self.__calcExtremities(gene,gene_type="transcript",ranges=flank_seq)
				output = self.chr_seq[chr_ID][up:down]
				if self.transcripts[gene]['strand'] == "-":
					output = reverse_complement(output)
			else:
				raise NoSequenceError("No sequence information available for %s. Did you load the reference sequence using the read_TAB method?\n" % (gene))			  
		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)

		if not format:	
			return output				 
		elif format == "fasta":
			if split:
				return ">%s\n%s" % (gene,splitString(output))
			else:
				return ">%s\n%s" % (gene,output)
		elif format == "tab":				
			return "%s\t%s" % (gene,output)
							
	def codingSequence(self,gene,ranges=0,format=None,split=False):
		"""returns the coding sequence of genes/transcripts. You need a gene name or ORF name (all UPPERCASE) and you can also set the "ranges" variable (i.e. ranges=50). This will allow you to addd flanking sequences to the coding sequence"""
		allowedformats = ["fasta","tab"]
		if format: assert format in allowedformats, "\nthe format you specified is not recognized, please use 'fasta' or 'tab'\n"
		output = str()
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		if gene in self.genes:
			chr_ID = self.genes[gene]['chromosome']
			sequence = str()
			if self.chr_seq[chr_ID]:
				if len(self.genes[gene]['CDS']):
					seq_copy = sorted(copy.deepcopy(self.genes[gene]['CDS']))
					if flank_seq > 0:
						seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
						seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
					for coordinates in seq_copy:
						sequence += self.chr_seq[chr_ID][coordinates[0]:coordinates[1]]
					if self.genes[gene]['strand'] == "+":
						output = sequence
					else:
						output = reverse_complement(sequence)
				elif not len(self.genes[gene]['CDS']):
					seq_copy = sorted(copy.deepcopy(self.genes[gene]['exon']))
					if flank_seq > 0:
						seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
						seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
					for coordinates in seq_copy:
						sequence += self.chr_seq[chr_ID][coordinates[0]:coordinates[1]]
					if self.genes[gene]['strand'] == "+":
						output = sequence
					else:
						output = reverse_complement(sequence)
			else:
				raise NoSequenceError("No sequence information available for %s. Did you load the reference sequence using the read_TAB method?\n" % (gene)) 
		
		elif gene in self.transcripts:
			chr_ID = self.transcripts[gene]['chromosome']
			sequence = str()
			if self.chr_seq[chr_ID]:
				if self.transcripts[gene]['CDS']:
					seq_copy = sorted(copy.deepcopy(self.transcripts[gene]['CDS']))
					if self.transcripts[gene]['start_codon'] and self.transcripts[gene]['stop_codon']:
						if self.transcripts[gene]['strand'] == "-":
							seq_copy[0]	 = (min(self.transcripts[gene]['stop_codon']), seq_copy[0][1])
							seq_copy[-1] = (seq_copy[-1][0], max(self.transcripts[gene]['start_codon']))
						else:
							seq_copy[0]	 = (min(self.transcripts[gene]['start_codon']), seq_copy[0][1])
							seq_copy[-1] = (seq_copy[-1][0], max(self.transcripts[gene]['stop_codon']))
					if flank_seq > 0:
						seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
						seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
					for coordinates in seq_copy:
						sequence += self.chr_seq[chr_ID][coordinates[0]:coordinates[1]]
					if self.transcripts[gene]['strand'] == "+":
						output = sequence
					else:
						output = reverse_complement(sequence)
				elif not self.transcripts[gene]['CDS']:						
					seq_copy = sorted(copy.deepcopy(self.transcripts[gene]['exon']))
					if flank_seq > 0:
						seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
						seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
					for coordinates in seq_copy:
						sequence += self.chr_seq[chr_ID][coordinates[0]:coordinates[1]]
					if self.transcripts[gene]['strand'] == "+":
						output = sequence
					else:
						output = reverse_complement(sequence)
			else:
				raise NoSequenceError("No sequence information available for %s. Did you load the reference sequence using the read_TAB method?\n" % (gene))

		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)

		if not format:	
			return output				 
		elif format == "fasta":
			if split:
				return ">%s\n%s" % (gene,splitString(output))
			else:
				return ">%s\n%s" % (gene,output)
		elif format == "tab":				
			return "%s\t%s" % (gene,output)
								 
	def exonCoordinates(self,gene,ranges=0):
		"""Returns a list with tuples of exon coordinates for genes or transcripts. It can have coordinates for multiple exons"""
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		if gene in self.genes:
			if self.genes[gene]['exon']:
				seq_copy = sorted(copy.deepcopy(self.genes[gene]['exon']))
				if flank_seq > 0:
					seq_copy = [(i[0]-flank_seq,i[1]+flank_seq) for i in seq_copy]
				return seq_copy
			else:
				return []
		elif gene in self.transcripts:
			if self.transcripts[gene]['exon']:
				seq_copy = sorted(copy.deepcopy(self.transcripts[gene]['exon']))
				if flank_seq > 0:
					seq_copy = [(i[0]-flank_seq,i[1]+flank_seq) for i in seq_copy]
				return seq_copy
			else:
				return []
		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)

	def cdsCoordinates(self,gene,ranges=0):
		"""Returns a list with tuples of CDS coordinates for genes or transcripts. It can have coordinates for multiple exons"""
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		if gene in self.genes:
			if self.genes[gene]['CDS']:
				seq_copy = sorted(copy.deepcopy(self.genes[gene]['CDS']))
				if flank_seq > 0:
					seq_copy = [(i[0]-flank_seq,i[1]+flank_seq) for i in seq_copy]
				return seq_copy
			else:
				return []
		elif gene in self.transcripts:
			if self.transcripts[gene]['CDS']:
				seq_copy = sorted(copy.deepcopy(self.transcripts[gene]['CDS']))
				if flank_seq > 0:
					seq_copy = [(i[0]-flank_seq,i[1]+flank_seq) for i in seq_copy]
				return seq_copy		
			else:
				return []
		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)
					
	def fivePrimeSpliceSites(self,gene):
		""" returns five prime splice site coordinates for a gene, if any """
		fiveprimess = list()
		introncoordinates = self.intronCoordinates(gene)
		if introncoordinates:
			for (start,end) in introncoordinates:
				if self.strand(gene) == "+":
					fiveprimess.append(start)
				else:
					fiveprimess.append(end-1)   # 1 has to be subtracted as the end coordinate is a 1-based coordinate!
		return fiveprimess
		
	def threePrimeSpliceSites(self,gene):
		""" returns three prime splice site coordinates for a gene, if any """
		threeprimess = list()
		introncoordinates = self.intronCoordinates(gene)
		if introncoordinates:
			for (start,end) in introncoordinates:
				if self.strand(gene) == "+":
					threeprimess.append(end-1)  # 1 has to be subtracted as the end coordinate is a 1-based coordinate!
				else:
					threeprimess.append(start)
		return threeprimess
		
	def fivePrimeEnd(self,gene,ranges=0):
		""" returns coordinates for the very first nucleotide in the gene. UTRs are included """
		flank_seq = ranges
		if self.__ranges:
			flank_seq = 0		# here you want flank_seq to be ignored if self.__ranges has already been set. Otherwise the two would be added up and longer UTR coordinates would be returned.
		if not gene:
			raise InputError("you forgot to enter the gene/transcript name\n")
		start,end = self.chromosomeCoordinates(gene,ranges=flank_seq)
		if self.strand(gene) == "+":
			return start
		else:
			return end - 1      # 1 has to be subtracted as the end coordinate is a 1-based coordinate!

	def threePrimeEnd(self,gene,ranges=0):
		""" returns coordinates for the very first nucleotide in the gene. UTRs are included """
		flank_seq = ranges
		if self.__ranges:
			flank_seq = 0		# here you want flank_seq to be ignored if self.__ranges has already been set. Otherwise the two would be added up and longer UTR coordinates would be returned.
		if not gene:
			raise InputError("you forgot to enter the gene/transcript name\n")
		start,end = self.chromosomeCoordinates(gene,ranges=flank_seq)
		if self.strand(gene) == "+":
			return end - 1      # 1 has to be subtracted as the end coordinate is a 1-based coordinate!
		else:
			return start
	
	def transcriptionStartSite(self,gene,ranges=0):
		""" returns coordinates for the very first nucleotide for genes that have annotated 5' UTRs """
		flank_seq = ranges
		if self.__ranges:
			flank_seq = 0		# here you want flank_seq to be ignored if self.__ranges has already been set. Otherwise the two would be added up and longer UTR coordinates would be returned.
		if not gene:
			raise InputError("you forgot to enter the gene/transcript name\n")
		(fiveutr,threeutr) = self.utrCoordinates(gene,ranges=flank_seq)
		if fiveutr:
			start,end = fiveutr
			if self.strand(gene) == "+":
				return start
			else:
				return end - 1  # 1 has to be subtracted as the end coordinate is a 1-based coordinate!
		elif not fiveutr:
			start = self.fivePrimeEnd(gene,ranges)
			return start
		else:
			return None
	
	def cdsStart(self,gene):
		""" returns coordinates for the very first nucleotide for genes that have annotated CDS coordinates """
		if not gene:
			raise InputError("you forgot to enter the gene/transcript name\n")
		else:
			coordinates = self.cdsCoordinates(gene)
			flattenedlist = list(itertools.chain(*coordinates))
			if self.strand(gene) == "+":
				return min(flattenedlist)
			else:
				return max(flattenedlist) - 1

	def cdsEnd(self,gene):
		""" returns coordinates for the very first nucleotide for genes that have annotated CDS coordinates """
		if not gene:
			raise InputError("you forgot to enter the gene/transcript name\n")
		else:
			coordinates = self.cdsCoordinates(gene)
			flattenedlist = list(itertools.chain(*coordinates))
			if self.strand(gene) == "+":
				return max(flattenedlist) - 1
			else:
				return min(flattenedlist)
	
	def intronCoordinates(self,gene):
		"""Calculates intron coordinates for genes or transcripts using the exon coordinates present in the 'exon' list. The reason for using the exon
		feature is that not all GTF files have proper CDS coordinates. Splice junctions are usually the same in exon and CDS coordinates. These are 0-based coordinates """
		array = list()
		introns = list()
		if gene in self.genes:
			array = sorted(self.genes[gene]['exon'])
		elif gene in self.transcripts:
			array = sorted(self.transcripts[gene]['exon'])
		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)			
		start = int()
		end = int()
		newarray = list()
		for i in array:						# remove exon coordinates that contain positions for start and end coordinates
			if i[-1]-i[0] > 3:
				newarray.append(i)
		newarray.sort()
		if len(newarray) > 1:
			for i in range(0,len(newarray)-1):
				start = max(newarray[i])
				end = min(newarray[i+1])
				if end - start > 4:
					introns.append((start,end))
		return introns
			
	def chromosomeGeneCoordIterator(self,chromosome,annotation=None,strand=None,sequence="genomic",numpy=False,ranges=0):
		"""Returns a list of tuples containing start,end and gene names for a specified chromosome. Format: (start,end,gene_name). 
		The user can also include an annotation or source (from column 2 in the GTF file) to select only genes that, for example, are snRNAs or snoRNA. 
		Make sure that the annotation name is identical to the one in the GTF file. Use the pyGetSourcesFromGTF.py script if you are not sure.
		Ranges allows you to manually set the length of UTR/flanking sequence. If 5UTR and 3UTR coordinates are provided in the GTF file it will try and calculate the extremities of the gene using
		UTR and exon coordinates."""
		gene_list = self.chromosomesGenesList(chromosome,annotation=annotation,strand=strand)
		coordinatesoptions = ["coding", "genomic","intron","exon","CDS","5UTR","3UTR","5end","3end","TSS","CDSstart","CDSend"]
		assert sequence in coordinatesoptions, "Please use the following options for the sequence flag:\n%s\n" % ",".join(coordinatesoptions)
		chromosome_gene_tuple_list = list()
		flank_seq = int()
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		if gene_list:
			for gene in gene_list:
				if sequence == "genomic" or sequence == "coding":
					(up,down) = self.__calcExtremities(gene,gene_type="gene",ranges=flank_seq)
					if up < 0: up = 0
					chromosome_gene_tuple_list.append((up,down-1,gene))
				elif sequence == "CDS":
					cds_coord = self.cdsCoordinates(gene,ranges=flank_seq)
					if cds_coord:
						for (up,down) in cds_coord:
							chromosome_gene_tuple_list.append((up,down-1,gene))
				elif sequence == "exon":
					exon_coord = self.exonCoordinates(gene,ranges=flank_seq)
					if exon_coord:
						for (up,down) in exon_coord:
							chromosome_gene_tuple_list.append((up,down-1,gene))
				elif sequence == "intron":
					intron_coord = self.intronCoordinates(gene)
					if intron_coord:
						for (up,down) in intron_coord:
							chromosome_gene_tuple_list.append((up,down-1,gene))
				elif sequence == "5UTR":
					utrcoord = self.utrCoordinates(gene,ranges=flank_seq)
					if utrcoord and utrcoord[0]:
						(up,down) = utrcoord[0]
						chromosome_gene_tuple_list.append((up,down-1,gene))
				elif sequence == "3UTR":
					utrcoord = self.utrCoordinates(gene,ranges=flank_seq)
					if utrcoord and utrcoord[1]:
						(up,down) = utrcoord[1]
						chromosome_gene_tuple_list.append((up,down-1,gene))
				elif sequence == "5ss":
					fiveprimess = self.fivePrimeSpliceSites(gene)
					if fiveprimess:
						for coord in fiveprimess:
							chromosome_gene_tuple_list.append((coord-flank_seq,coord+flank_seq,gene))
				elif sequence == "3ss":
					threeprimess = self.threePrimeSpliceSites(gene)
					if threeprimess:
						for coord in threeprimess:
							chromosome_gene_tuple_list.append((coord-flank_seq,coord+flank_seq,gene))
				elif sequence == "5end" or sequence == "TSS":
					fiveprimeend = self.fivePrimeEnd(gene)
					chromosome_gene_tuple_list.append((fiveprimeend-flank_seq,fiveprimeend+flank_seq,gene))
				elif sequence == "3end":
					threeprimeend = self.threePrimeEnd(gene)
					chromosome_gene_tuple_list.append((threeprimeend-flank_seq,threeprimeend+flank_seq,gene))
				elif sequence == "CDSstart":
					if self.genes[gene]['CDS']:
						fiveprimeend= self.cdsStart(gene)
						chromosome_gene_tuple_list.append((fiveprimeend-flank_seq,fiveprimeend+flank_seq,gene))
				elif sequence == "CDSend":
					if self.genes[gene]['CDS']:
						threeprimeend = self.cdsEnd(gene)
						chromosome_gene_tuple_list.append((threeprimeend-flank_seq,threeprimeend+flank_seq,gene))
				else:
					raise InputError("I did not recognize the %s option. Please double check your input\n" % sequence)
		if numpy:
			return np.array(chromosome_gene_tuple_list, dtype='i,i,U100')	# gene_name length of 100 characters is the absolute maximum
		else:
			return chromosome_gene_tuple_list
	
	def geneIterCoordinates(self,gene,coordinates="genomic",ranges=0,output="numpy"):
		""" Returns chromosomal positions for a gene as a a numpy, set or python array. Very useful for making pileups!
		By default it returns numpy arrays but you can tell it to return standard python lists or set() lists by stipulating output="list" or output="set"
		as an argument when using this method. Coordinate input choices: genomic, coding,intron, exon, CDS, 5UTR, 3UTR (untranslated regions), 3ss, 5ss (splice sites)
		, TSS (transcription start sites, (if any)), 5end and 3end (5' and 3' end coordinates, respectively). 
		If you choose genomic or coding sequence coordinates, then setting ranges will add extra coordinates upstream and downstream of the sequences. 
		When choosing exon, CDS or intron coordinates, ranges adds extra coordinates to each individual exon, CDS or intron. """
		coordinatesoptions = ["genomic","coding","intron","exon","CDS","5UTR","3UTR","5ss","3ss","TSS","5end","3end","CDSstart","CDSend"]
		assert coordinates in coordinatesoptions, "\n\nCould not find coordinates for %s. Please choose from the following options:\n%s\n" % (coordinates,"\n".join(coordinatesoptions))
		if not gene:
			raise InputError("you forgot to enter the gene/transcript name\nCould there be an error in your GTF annotation file?")
		if coordinates == "genomic":																# returns genomic sequence coordinates. Contain intronic sequences
			coord = self.chromosomeCoordinates(gene,ranges=ranges)
			if output == "numpy":
				return np.arange(coord[0],coord[1],dtype=int)
			elif output == "set":
				return set(range(coord[0],coord[1]))
			elif output == "list":
				return list(range(coord[0],coord[1]))
		elif coordinates == "coding":																# returns coding sequence coordinates. Introns have been removed
			cds_array = list()
			coding_seq_coord = self.codingSequenceCoordinates(gene,ranges=ranges)
			if coding_seq_coord:
				for coord in coding_seq_coord:
					cds_array.extend(list(range(coord[0],coord[1])))
				if output == "numpy":
					return np.array(cds_array,dtype=int)
				elif output == "set":
					return set(cds_array)
				elif output == "list":
					return cds_array
			else:
				return []								
		elif coordinates == "intron":
			intron_array = list()
			intron_coord = self.intronCoordinates(gene)
			if intron_coord:
				for coord in intron_coord:
					if output == "numpy":
						intron_array.append(np.arange(coord[0]-ranges,coord[1]+ranges))				#NOTE!!! ranges adds extra coordinates upstream and downstream of each intron, not entire gene!
					elif output == "set":
						intron_array.append(set(range(coord[0]-ranges,coord[1]+ranges)))
					elif output == "list":
						intron_array.append(list(range(coord[0]-ranges,coord[1]+ranges)))
				return intron_array
			else:
				return []						
		elif coordinates == "exon":
			exon_array = list()
			exon_coord = self.exonCoordinates(gene)
			if exon_coord:
				for coord in exon_coord:
					if output == "numpy":
						exon_array.append(np.arange(coord[0]-ranges,coord[1]+ranges))				#NOTE!!! ranges adds extra coordinates upstream and downstream of each exon, not entire gene!
					elif output == "set":
						exon_array.append(set(range(coord[0]-flank_seq,coord[1]+ranges)))
					else:
						exon_array.append(list(range(coord[0]-ranges,coord[1]+ranges)))
				return exon_array
			else:
				return []						
		elif coordinates == "CDS":
			CDS_array = list()
			CDS_coord = self.cdsCoordinates(gene)
			if CDS_coord:
				for coord in CDS_coord:
					if output == "numpy":
						CDS_array.append(np.arange(coord[0]-ranges,coord[1]+ranges))				#NOTE!!! ranges adds extra coordinates upstream and downstream of each CDS, not entire gene!
					elif output == "set":
						CDS_array.append(set(range(coord[0]-ranges,coord[1]+ranges)))
					else:
						CDS_array.append(list(range(coord[0]-ranges,coord[1]+ranges)))
				return CDS_array
			else:
				return []			
		elif re.search("UTR",coordinates,re.I):
				UTR_coord = self.utrCoordinates(gene,ranges=ranges)
				if coordinates.upper() == "5UTR":
					fiveUTR_coord = UTR_coord[0]
					if fiveUTR_coord:
						if output == "numpy":
							return np.arange(fiveUTR_coord[0],fiveUTR_coord[1])
						elif output == "set":
							return set(range(fiveUTR_coord[0],fiveUTR_coord[1]))
						else:
							return list(range(fiveUTR_coord[0],fiveUTR_coord[1]))
					else:
						return []
								
				elif coordinates.upper() == "3UTR":
					threeUTR_coord = UTR_coord[1]
					if threeUTR_coord:
						if output == "numpy":
							return np.arange(threeUTR_coord[0],threeUTR_coord[1])
						elif output == "set":
							return set(range(threeUTR_coord[0],threeUTR_coord[1]))
						else:
							return list(range(threeUTR_coord[0],threeUTR_coord[1]))
					else:
						return [] 
		elif coordinates in coordinatesoptions[6:]:			# in case it is a single value; "5ss","3ss","TSS","5end" and"3end"
			positions = list()
			if coordinates == "5ss":
				fiveprimess = self.fivePrimeSpliceSites(gene)
				if fiveprimess:
					for coord in fiveprimess:
						positions.append(list(range(coord-ranges,coord+ranges+1)))
			elif coordinates == "3ss":
				threeprimess = self.threePrimeSpliceSites(gene)
				if threeprimess:
					for coord in threeprimess:
						positions.append(list(range(coord-ranges,coord+ranges+1)))
			elif coordinates == "5end":
				fiveprimeend = self.fivePrimeEnd(gene)
				positions = list(range(fiveprimeend-ranges,fiveprimeend+ranges+1))
			elif coordinates == "TSS":
				TSS = self.transcriptionStartSite(gene)
				if TSS:
					positions = list(range(TSS-ranges,TSS+ranges+1))
			elif coordinates == "3end":
				threeprimeend = self.threePrimeEnd(gene)
				positions = list(range(threeprimeend-ranges,threeprimeend+ranges+1))
			elif coordinates == "CDSstart":
				fiveprimeend= self.cdsStart(gene)
				if fiveprimeend:
					positions = list(range(fiveprimeend-ranges,fiveprimeend+ranges+1))
			elif coordinates == "CDSend":
				threeprimeend = self.cdsEnd(gene)
				if threeprimeend:
					positions = list(range(threeprimeend-ranges,threeprimeend+ranges+1))
			else:
				sys.stderr.write("\n\nCould not find coordinates for %s. Please choose from the following options:\n%s\n" % (coordinates,"\n".join(coordinatesoptions)))
			if positions:
				if output == "numpy": 
					return np.array(positions)
				if output == "set":	  
					return set(positions)
				else:
					return positions
			else:
				return []
		else:
			raise InputError("I did not recognize the %s option. Please double check your --sequence input\n" % coordinates)

	def utrCoordinates(self,gene,ranges=0):
		""" This function calculates the UTR coordinates using the exon and CDS coordinates in 
		the a Parse_GTF dictionary object if UTR coordinates were not defined in the GTF file.
		If a range has been set then UTR coordinates in the GTF file will be ignored."""
		dictionary = dict()
		if gene in self.genes:
			dictionary = self.genes
		elif gene in self.transcripts:
			dictionary = self.transcripts
		else:
			sys.stderr.write("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file\n" % gene)
			return None
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		def calc5UTR(gene,dictionary):
			""" calculates 5'UTR coordinates """
			if not flank_seq:
				if dictionary[gene]['5UTR']:
					return dictionary[gene]['5UTR'][0]
				elif not dictionary[gene]['exon']:
					return ()
				elif dictionary[gene]['exon'] and dictionary[gene]['CDS']:
					five_UTR	= tuple()
					listofexons = list(itertools.chain(*dictionary[gene]['exon']))
					listofcds	= list(itertools.chain(*dictionary[gene]['CDS']))
					maxlistofexons = max(listofexons)
					minlistofexons = min(listofexons)
					maxlistofcds  = max(listofcds)
					minlistofcds  = min(listofcds)
					if dictionary[gene]['strand'] == "+":
						if minlistofexons < minlistofcds:
							upstream   = minlistofexons
							downstream = minlistofcds - 1
							five_UTR   = (upstream,downstream)
				 
					elif dictionary[gene]['strand'] == "-":
						if maxlistofexons > maxlistofcds:
							upstream   = maxlistofcds
							downstream = maxlistofexons
							five_UTR   = (upstream,downstream)
					return five_UTR
			elif flank_seq:
				if dictionary[gene]['CDS']:
					five_UTR  = tuple()
					listofcds = list(itertools.chain(*dictionary[gene]['CDS']))
					maxlistofcds  = max(listofcds)
					minlistofcds  = min(listofcds)
					if dictionary[gene]['strand'] == "+":
						downstream = minlistofcds
						upstream   = downstream - flank_seq
						five_UTR   = (upstream,downstream)
					elif dictionary[gene]['strand'] == "-":
						upstream   = maxlistofcds
						downstream = upstream + flank_seq
						five_UTR   = (upstream,downstream)
					return five_UTR
				if not dictionary[gene]['CDS'] and dictionary[gene]['exon']:
					five_UTR	= tuple()
					listofexons = list(itertools.chain(*dictionary[gene]['exon']))
					maxlistofexons = max(listofexons)
					minlistofexons = min(listofexons)
					if dictionary[gene]['strand'] == "+":
						downstream = minlistofexons
						upstream   = downstream - flank_seq
						five_UTR   = (upstream,downstream)
					elif dictionary[gene]['strand'] == "-":
						upstream   = maxlistofexons
						downstream = upstream + flank_seq
						five_UTR   = (upstream,downstream)
					return five_UTR
			else:
				return ()

		def calc3UTR(gene,dictionary):
			""" calculates 3'UTR coordinates """ 
			if not flank_seq:
				if dictionary[gene]['3UTR'] :
					return dictionary[gene]['3UTR'][0]
				elif not dictionary[gene]['exon']:
					return ()
				elif dictionary[gene]['exon'] and dictionary[gene]['CDS']:
					three_UTR	= tuple()
					listofexons = list(itertools.chain(*dictionary[gene]['exon']))
					listofcds	= list(itertools.chain(*dictionary[gene]['CDS']))	 
					maxlistofexons = max(listofexons)
					minlistofexons = min(listofexons)
					maxlistofcds  = max(listofcds)
					minlistofcds  = min(listofcds)
					if dictionary[gene]['strand'] == "+":		
						if maxlistofexons > maxlistofcds:
							upstream   = maxlistofcds
							downstream = maxlistofexons
							three_UTR  = (upstream,downstream)
						else:
							three_UTR  = ()
					elif dictionary[gene]['strand'] == "-":
						if minlistofexons < minlistofcds:
							upstream   = minlistofexons
							downstream = minlistofcds
							three_UTR  = (upstream,downstream)
						else:
							three_UTR  = ()
					return three_UTR	
			elif flank_seq > 0:
				if dictionary[gene]['CDS']:
					three_UTR = tuple()
					listofcds = list(itertools.chain(*dictionary[gene]['CDS']))
					maxlistofcds  = max(listofcds)
					minlistofcds  = min(listofcds)
					if dictionary[gene]['strand'] == "+":		
						upstream   = maxlistofcds
						downstream = upstream + flank_seq
						three_UTR  = (upstream,downstream)
					elif dictionary[gene]['strand'] == "-":
						downstream = minlistofcds
						upstream   = downstream - flank_seq
						three_UTR  = (upstream,downstream)
					return three_UTR
					
				elif not dictionary[gene]['CDS'] and dictionary[gene]['exon']:
					three_UTR	= tuple()
					listofexons = list(itertools.chain(*dictionary[gene]['exon']))
					maxlistofexons = max(listofexons)
					minlistofexons = min(listofexons)
					if dictionary[gene]['strand'] == "+":
						upstream   = maxlistofexons
						downstream = upstream + flank_seq
						three_UTR  = (upstream,downstream)
					elif dictionary[gene]['strand'] == "-":
						downstream = minlistofexons
						upstream   = downstream - flank_seq
						three_UTR  = (upstream,downstream)
					return three_UTR
			else:
				return ()
						
		return [calc5UTR(gene,dictionary),calc3UTR(gene,dictionary)]
			
	def codingSequenceCoordinates(self,gene,ranges=0):
		"""returns a list with tuples of coding sequence (CDS) coordinates for genes or transcripts. It can have coordinates for
		multiple CDSs. Returns a list of exon coordinates if the gene or transcript has no CDS coordinates"""
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
					
		if gene in self.genes:
			if self.genes[gene]['CDS']:
				seq_copy = sorted(copy.deepcopy(self.genes[gene]['CDS']))
				if flank_seq > 0:
					seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
					seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
				return seq_copy
			else:
				seq_copy = sorted(copy.deepcopy(self.genes[gene]['exon']))
				if flank_seq > 0:
					seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
					seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
				return seq_copy						
		elif gene in self.transcripts:
			if self.transcripts[gene]['CDS']:
				seq_copy = sorted(copy.deepcopy(self.transcripts[gene]['CDS']))
				if self.transcripts[gene]['start_codon'] and self.transcripts[gene]['stop_codon']:
					if self.transcripts[gene]['strand'] == "-":
						seq_copy[0]	 = (min(self.transcripts[gene]['stop_codon']), seq_copy[0][1])
						seq_copy[-1] = (seq_copy[-1][0], max(self.transcripts[gene]['start_codon']))
					elif self.transcripts[gene]['strand'] == "+":
						seq_copy[0]	 = (min(self.transcripts[gene]['start_codon']), seq_copy[0][1])
						seq_copy[-1] = (seq_copy[-1][0], max(self.transcripts[gene]['stop_codon']))
				if flank_seq > 0:
						seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
						seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
				return seq_copy
			else:
				seq_copy = sorted(copy.deepcopy(self.transcripts[gene]['exon']))
				if flank_seq > 0:
					seq_copy[0]	 = (seq_copy[0][0] - flank_seq, seq_copy[0][1])
					seq_copy[-1] = (seq_copy[-1][0], seq_copy[-1][1] + flank_seq)
				return seq_copy			
		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)

	def intronSequences(self,gene,format=None,split=False):
		"""returns a list with the intron sequences for a gene or ORF of interest. Returns an empty list if the gene has no introns. Usage: intron("RPL7A")"""
		allowedformats = ["fasta","tab"]
		if format: assert format in allowedformats, "\nthe format you specified is not recognized, please use 'gb', 'fasta' or 'tab'\n"
		introns = list()
		out		= str()
		chr_ID	= str()
		strand	= str()
		if gene in self.transcripts:  
			chr_ID = self.transcripts[gene]['chromosome']
			strand = self.transcripts[gene]['strand']
		elif gene in self.genes:	  
			chr_ID = self.genes[gene]['chromosome']
			strand = self.genes[gene]['strand']
		else:
			raise LookupError("Could not find %s in the genes or transcript dictionary. Note that gene and transcript names must be exactly the same as in the GTF file" % gene)
		if not self.chr_seq[chr_ID]:
			raise NoSequenceError("No intronic sequences available. Did you forgot to load the genomic reference sequence? Use the read_TAB method to load the fasta file containing the genome\n")
		intron_coordinates = sorted(self.intronCoordinates(gene))
		if intron_coordinates:
			for coord in intron_coordinates:
				intron_up	= coord[0]
				intron_down = coord[1]
				if strand  == "+":
					intron = self.chr_seq[chr_ID][intron_up-1:intron_down+1]
					introns.append(intron)
				elif strand	 == "-":
					intron = self.chr_seq[chr_ID][intron_up-1:intron_down+1]
					introns.append(reverse_complement(intron))
		else:
			return None

		if not format:	
			return introns				
		elif format == "fasta":
			for nr,intron in enumerate(introns,start=1):
				if split:
					out += ">%s_intron_%s\n%s\n" % (gene,nr,splitString(intron))
				else:
					out += ">%s_intron_%s\n%s\n" % (gene,nr,intron)
			return out
		elif format == "tab":				
			for intron in introns:
				out += "%s\t%s\n" % (gene,intron)
		return out

	def chromosomeCoordinates(self,gene,ranges=0):
		"""	 returns a tuple of chromosome coordinates for a genes or ORFS. Usage: chromosomeCoordinates("RRP9")"""
		if self.__ranges: 
			flank_seq = self.__ranges
		else:
			flank_seq = ranges
		if gene in self.genes:
			return self.__calcExtremities(gene,gene_type="gene",ranges=flank_seq)
		elif gene in self.transcripts:
			return self.__calcExtremities(gene,gene_type="transcript",ranges=flank_seq)
		else:
			raise LookupError("could not find chromosome coordinates for this %s\n" % (gene))
