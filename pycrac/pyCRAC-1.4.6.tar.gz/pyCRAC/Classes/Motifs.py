#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.2.3"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	Motifs
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

import math
import time
from random import randint
from collections import defaultdict
from pyCRAC.Classes.NGSFormatWriters import *
from pyCRAC.Parsers import ParseAlignments
from pyCRAC.Methods import sortbyvalue,orientation,numpy_overlap,getfilename,check_list,reverse_complement

def randomizeSequences(orientation,sequence,gene_sequence):
	"""Returns a random sequence from a particular gene. If the read sequence is in the
	anti-sense orientation, the reverse_complement of a random sequence will be returned"""
	rand_start = 0
	rand_end   = 0
	limit	   = len(gene_sequence)-len(sequence)
	if len(gene_sequence)-len(sequence) + 1 > 2:					# The difference in length between the gene sequence and the read sequence has to be at least two nucleotides
		rand_start = randint(1,limit)								# Otherwise, randint will only be able to generate '1' as random number
		rand_end   = rand_start + len(sequence)
	else:															# If the gene sequence is smaller than the actual read sequence (think tRNAs, small snoRNAs, etc) then
		rand_start = 1												# randint gets a negative number. This obviously won't work so in these cases the gene sequences are simply returned
		rand_end   = len(gene_sequence)								# It is important that tRNAs are not (always) included in the motif searches since these are very similar and highest scoring motifs would
	if orientation == "sense":										# therefore almost always come from tRNAs.
		rand_seq   = gene_sequence[rand_start:rand_end]
		return rand_seq
	elif orientation == "anti-sense":
		rand_seq   = reverse_complement(gene_sequence)[rand_start:rand_end]
		return rand_seq
	else:
		sys.stderr.write("could not return a random sequence from your input\nPlease check your input\n")

class FindMotifs():
	"""This class extracts motifs from intervals, calculates the Z-score for each motif found and prints a file where in genes
	these motifs were found. A file containing the hits for each motifs in the reads and a file with hits for randomly
	generated motifs will also be printed. Requires a GTF2 object to find overlap between intervals and genomic features """
	def __init__(self):
		self.__genomic_seq		= str()
		self.__gene_rand_seq	= list()
		self.__rand_count		= defaultdict(int)
		self.__motif_dict		= defaultdict(set)
		self.__motif_count		= defaultdict(int)
		self.__rand_motif_count = defaultdict(int)
		self.__k_length_range	= list()
		self.__insert			= str()
		self.__insert2			= str()
		self.__gtf				= None
		self.annotation			= str()
		self.total_intervals	= 0
		self.total_motif_count	= 0
		self.z_scores			= defaultdict(int)
		self.file_name			= str()
		self.file_list			= list()

	def setKmerLength(self,k_min=4,k_max=8):
		"""To change the default k-mer length settings (defaults are between 4 and 8 nucleotides)"""
		if k_max > k_min:
			self.__k_length_range = range(k_min,(k_max+1))
		elif k_max < k_min:										# in case people flip the two accidentally
			self.__k_length_range = range(k_max,(k_min+1))
		else:
			self.__k_length_range = [k_min]						# in k_min and k_max are the same

	def findMotifs(self,gtf,datafile,min_overlap=1):
		"""Extracts the motifs from intervals."""
		#-----------------------------------------------------------------------------------------------------------------------------------

		search_results	  = list()
		motif_list		  = list()
		list_of_tuples	  = defaultdict(list)
		self.__gtf		  = gtf

		#------------ extracting motifs from each read coordinate. Anti-sense hits are considered but unmapped reads are not ---------------

		data = ParseAlignments.ParseCountersOutput(datafile)
		self.file_name = getfilename(datafile)
		while data.readLineByLine(collectmutations=False):
			data.duplicatesremoved = True
			self.total_intervals += 1
			read_sequence = gtf.sequence(data.chromosome,data.strand,data.read_start,data.read_end)
			motif_start = int()
			motif_end	= int()
			readorientation = str()
			overlapping_genes = list()
			for gene in data.genes:
				if gene == "no_matches":		# if the interval has not been mapped to a genomic feature, ignore it
					continue
				try:
					readorientation = orientation(data.strand,gtf.strand(gene))
				except LookupError:
					continue
				if readorientation == "sense":																	# If the intervals are sense to the gene or GTF feature
					if gtf.strand(gene) == "+":
						for k_length in self.__k_length_range:
							length_seq = len(read_sequence) - k_length
							for i in range (0,length_seq+1):
								motif = read_sequence[i:(i+k_length)]
								if check_list(motif_list,motif):												# checks if the motif sequence has already been seen in the read or cluster.
									motif_start = data.read_start + i
									self.total_motif_count += 1
									self.__motif_count[motif] += 1
									self.__motif_dict[motif].add((data.chromosome,data.strand,motif_start))
							motif_list = list()

					elif gtf.strand(gene) == "-":
						for k_length in self.__k_length_range:
							length_seq = len(read_sequence) - k_length
							for i in range (0,length_seq+1):
								motif = read_sequence[i:(i+k_length)]
								if check_list(motif_list,motif):
									motif_start = data.read_end - k_length - i
									self.total_motif_count += 1
									self.__motif_count[motif] += 1
									self.__motif_dict[motif].add((data.chromosome,data.strand,motif_start))
							motif_list = list()

				elif readorientation == "anti-sense":															# If the intervals are anti-sense to the gene or GTF feature
					if gtf.strand(gene) == "-":
						for k_length in self.__k_length_range:
							length_seq = len(read_sequence) - k_length
							for i in range (0,length_seq+1):
								motif = read_sequence[i:(i+k_length)]
								if check_list(motif_list,motif):
									motif_start = data.read_start + i
									self.total_motif_count += 1
									self.__motif_count[motif] += 1
									self.__motif_dict[motif].add((data.chromosome,data.strand,motif_start))
							motif_list = list()


					elif gtf.strand(gene) == "+":
						for k_length in self.__k_length_range:
							length_seq = len(read_sequence) - k_length
							for i in range (0,length_seq+1):
								motif = read_sequence[i:(i+k_length)]
								if check_list(motif_list,motif):
									motif_start = data.read_end - k_length - i
									self.total_motif_count += 1
									self.__motif_count[motif] += 1
									self.__motif_dict[motif].add((data.chromosome,data.strand,motif_start))
							motif_list = list()


				random_sequence = randomizeSequences(readorientation,read_sequence,gtf.genomicSequence(gene,ranges=len(read_sequence)-min_overlap))		        # some of the reads may overlap with the 5' and 3' UTR, therefore,
				for k_length in self.__k_length_range:																											# for making random sequences the program includes a stretch
					length_seq = len(random_sequence) - k_length																								# of the 5' and 3' UTRs with the length of the read sequence length!
					for i in range (0,length_seq+1):
						rand_motif = random_sequence[i:(i+k_length)]
						if check_list(motif_list,rand_motif):
							self.__rand_count[rand_motif] += 1
					motif_list = list()

		return True

	def __createFileHandles(self,file_type,file_extension="txt"):
		""" does what it says """
		annotation = "all"
		if self.annotation:
			annotation = self.annotation
		filename = "%s_%s_%s.%s" % (self.file_name,annotation,file_type,file_extension)
		self.file_list.append(filename)
		return filename

	def printRandKmers(self,output_file=None,max_motifs=1000):
		"""Prints a list of hits for randomly generated k-mers"""
		assert self.__motif_count, "\n\nYou need to run the extractMotifs method first before you can print the k-mers\n"
		file_name = None
		file_type = "random_k-mers_count"
		if output_file:
			self.file_name = output_file
		file_name = self.__createFileHandles(file_type)
		file_out = open(file_name, "w")
		file_out.write("# %s\n# %s\n" % (' '.join(sys.argv),time.ctime()))
		file_out.write("# k-mer lengths:\n#\tmin: %s\n#\tmax: %s\n" % (self.__k_length_range[0],self.__k_length_range[-1]))
		file_out.write("# %s intervals\n\n# k-mer\tnumber_of_occurrences\n" % (self.total_intervals))
		for (motifs,value) in sortbyvalue(self.__rand_count)[0:max_motifs]:
			file_out.write("%s\t%s\n" % (motifs,self.__rand_count[motifs]))
		file_out.close()

	def printExperimentalKmers(self,output_file=None,max_motifs=1000):
		"""Prints a k-mer hit list extracted from the data"""
		assert self.__motif_count, "\n\nYou need to run the extractMotifs method first before you can print the k-mers\n"
		file_name = None
		file_type = "data_k-mers_count"
		if output_file:
			self.file_name = output_file
		file_name = self.__createFileHandles(file_type)
		file_out = open(file_name, "w")
		file_out.write("# %s\n# %s\n" %(' '.join(sys.argv),time.ctime()))
		file_out.write("# k-mer lengths:\n#\tmin: %s\n#\tmax: %s\n" % (self.__k_length_range[0],self.__k_length_range[-1]))
		file_out.write("# %s intervals\n\n# k-mer\tnumber_of_occurrences\n" % self.total_intervals)
		for (motifs,value) in sortbyvalue(self.__motif_count)[0:max_motifs]:
			file_out.write("%s\t%s\n" % (motifs,self.__motif_count[motifs]))
		file_out.close()

	def calcMotifZscores(self):
		"""Calculates the Z-scores for each k-mer sequence"""
		assert self.__motif_count, "\n\nYou need to run the extractMotifs method first before you can calculate Z-scores\n"
		motif_list = list()
		a = set(self.__motif_count.keys())
		b = set(self.__rand_count.keys())
		motif_list	 = a | b
		for motifs in motif_list:
			p1 = float(self.__motif_count[motifs]) / self.total_motif_count
			p2 = float(self.__rand_count[motifs]) / self.total_motif_count
			try:
				if p1 or p2:
					Z_score = math.sqrt(self.total_motif_count) * (p1-p2) / math.sqrt(p1*(1-p1) + p2*(1-p2))
					self.z_scores[motifs] = Z_score
			except ValueError:
				sys.stderr.write("\nValueError! Can not calculate a Z-score for the %s motif. The number of motifs (%s) is higher than the total number of sequences (%s)\n" % (motifs,self.__motif_count[motifs],self.total_motif_count))
				pass
		return True

	def printMotifZscores(self,output_file=None,max_motifs=1000):
		"""Prints the Z-scores for the top k-mers"""
		assert self.__motif_count, "\n\nYou need to run the extractMotifs method first before you can print the Z-scores\n"
		file_type = "k-mer_Z_scores"
		file_name = None
		if output_file:
			self.file_name = output_file
		file_name = self.__createFileHandles(file_type)
		file_out = open(file_name,"w")
		file_out.write("# %s\n# %s\n" % (' '.join(sys.argv),time.ctime()))
		file_out.write("# k-mer lengths:\n#\tmin: %s\n#\tmax: %s\n" % (self.__k_length_range[0],self.__k_length_range[-1]))
		file_out.write("# %s intervals\n\n# k-mer\tZ-score\n" % (self.total_intervals))
		for (motifs,score) in sortbyvalue(self.z_scores)[0:max_motifs]:
			file_out.write("%s\t%0.2f\n" % (motifs,score))
		file_out.close()

	def printMotifGTFfile(self,output_file=None,max_motifs=1000):
		""" Prints a list of k-mers found in reads mapped to genes in GTF format"""
		assert self.__motif_count, "\n\nYou need to run the extractMotifs method first before you can print the GTF output file\n"
		list_of_tuples = defaultdict(list)
		if output_file:
			self.file_name = output_file
		if not self.z_scores:
			self.calcMotifZscores()
		topkmers  = sortbyvalue(self.z_scores)[0:max_motifs]
		file_name = None
		file_type = "top_k-mers_in_features"
		file_extension = "gtf"
		if output_file: file_name = output_file
		file_name = self.__createFileHandles(file_type,file_extension)
		file_out = NGSFileWriter(file_name)
		file_out.write("##gff-version 2\n")
		file_out.write("# %s\n# %s\n" %(' '.join(sys.argv),time.ctime()))
		file_out.write("# k-mer lengths:\n#\tmin: %s\n#\tmax: %s\n" % (self.__k_length_range[0],self.__k_length_range[-1]))
		file_out.write("# total number of unique k-mers reported:\t%s\n" % (max_motifs))
		file_out.write("# total number of mapped intervals:\t%s\n" % self.total_intervals)
		file_out.write("# chromosome\tsource\tsequence\tstart\tend\tZ-score\tstrand\t.\tattributes\n")
		for motif,value in topkmers:
			for interval in sorted(self.__motif_dict[motif]):
				chromosome,strand,motif_start = interval
				motif_length = len(motif)
				motif_end	 = motif_start+motif_length
				if chromosome not in list_of_tuples:
					try:
						list_of_tuples[chromosome] = self.__gtf.chromosomeGeneCoordIterator(chromosome,numpy=True)
					except AssertionError:
						continue
				genes = numpy_overlap(list_of_tuples[chromosome],motif_start,motif_end-1,overlap=1)
				if genes:
					gene_name = ",".join(genes)
					gene_id = ",".join([self.__gtf.gene2orf(gene) for gene in genes])
				else:
					gene_name = "no_matches"
					gene_id = "no_matches"
				file_out.writeGTF(chromosome,"motif",motif,motif_start,motif_end,value,strand=strand,gene_name=gene_name,gene_id=gene_id)
		file_out.close()