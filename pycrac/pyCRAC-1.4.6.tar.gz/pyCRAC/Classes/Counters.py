#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "1.4.4"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "production"

##################################################################################
#
#	Counters.py
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

import time
from pyCRAC.Parsers.ParseAlignments import *
from pyCRAC.Methods import strand_converter, overlap, numpy_overlap, getfilename
from pyCRAC.Classes.Exceptions import *
from pyCRAC.Classes.NGSFormatWriters import NGSFileWriter

class PyCounters(ParseAlignmentFile,ParseCountersOutput):
	def __init__(self,file_in,gtfobject,file_type="novo",ranges=0,ignorestrand=False,debug=None):
		"""Initializing the class attributes"""
		file_types = ["novo","sam","gtf"]
		if file_type in file_types[:2]:
			ParseAlignmentFile.__init__(self,file_in,file_type,debug=debug)
		elif file_type == file_types[2]:
			ParseCountersOutput.__init__(self,file_in)
		self.gtf				   = gtfobject
		self.file_name			   = getfilename(file_in)
		self.datadictionary		   = defaultdict(lambda: defaultdict(lambda: [0,0]))	# annotation is first key, then gene, then the values is sense and anti_sense counts
		self.gene_hits			   = defaultdict(int)
		self.cDNA_count			   = defaultdict(int)
		self.annotations_count	   = defaultdict(int)
		self.hits_count			   = int()
		self.no_matches			   = int()
		self.sense_hits_count	   = int()
		self.anti_sense_hits_count = int()
		self.file_list			   = list()
		self.sequence              = "genomic"
		self.densities             = False
		self.__ignorestrand		   = ignorestrand

	def countGeneHits(self,min_overlap=1,sense=True,anti_sense=True,sequence="genomic"):
		"""Calculates the number of hits for genes in the dataset. It does NOT count transcripts! To map cDNAs/clusters to individual
		transcripts you can run the countGeneFeaturesOverlap after running the countGeneHits method. The program first determines to which
		genes hits were found and then with the countGeneFeaturesOverlap you can calculate overlap for individual gene transcripts and
		transcript features such as intron,UTR, exon and CDS. This saves a tremendous number of iterations.
		The GTF2 module calculates start and end positions for each gene based exon coordinate and include introns and UTRs if present.
		This makes the iteration step significantly faster, as in higher eukaryotes each gene can code for many transcripts"""
		list_of_tuples = defaultdict(list)
		self.sequence = sequence
		for interval in self.count:
			selectedgenes = list()
			chromosome,strand,read_start,read_end,substitutions,deletions = interval
			coverage = self.count[interval]["coverage"]
			strand = strand_converter(strand)
			if not self.count[interval]["features"]:
				search_results = list()
				try:
					if chromosome not in list_of_tuples:
						list_of_tuples[chromosome] = self.gtf.chromosomeGeneCoordIterator(chromosome,numpy=True,sequence=sequence)
					if len(list_of_tuples[chromosome]) > 0:
						search_results = numpy_overlap(list_of_tuples[chromosome],read_start,read_end-1,overlap=min_overlap)
					else:
						continue
				except AssertionError:			# in case you want to run pyReadCounters with a smaller GTF. This should ignore any errors
					#sys.stderr.write("AssertionError @ %s\t%s\t%s\t%s\n" % (chromosome,strand,read_start,read_end))
					pass
				if search_results:
					self.count[interval]["features"] = search_results
			if self.count[interval]["features"]:
				for gene in self.count[interval]["features"]:
					try:
						if sense and strand == self.gtf.strand(gene):
							for i in self.gtf.annotations(gene):
								self.annotations_count[i] += coverage
								self.datadictionary[i][gene][0] += coverage
							self.gene_hits[gene] += coverage
							self.hits_count += coverage
							self.sense_hits_count += coverage
							self.cDNA_count[gene] += 1
							selectedgenes.append(gene)
						if anti_sense and strand != self.gtf.strand(gene):
							for i in self.gtf.annotations(gene):
								self.annotations_count[i] += coverage
								self.datadictionary[i][gene][1] += coverage
							self.gene_hits[gene] += coverage
							self.hits_count += coverage
							self.anti_sense_hits_count += coverage
							self.cDNA_count[gene] += 1
							selectedgenes.append(gene)
					except LookupError:
						#sys.stderr.write('could not finde gene %s in the gtf file\n')
						continue
			self.count[interval]["features"] = selectedgenes

	def countNucleotideDensities(self,min_overlap=1,sense=True,anti_sense=True,sequence="genomic"):
			"""Calculates the number of nucleotides that overlap with features in genes """
			list_of_tuples = defaultdict(list)
			self.sequence = sequence
			self.densities = True
			for interval in self.count:
				selectedgenes = list()
				chromosome,strand,read_start,read_end,substitutions,deletions = interval
				coverage = self.count[interval]["coverage"]
				strand = strand_converter(strand)
				search_results = list()
				try:
					if chromosome not in list_of_tuples:
						list_of_tuples[chromosome] = self.gtf.chromosomeGeneCoordIterator(chromosome,numpy=True,sequence=sequence)
					if len(list_of_tuples[chromosome]) > 0:
						search_results = numpy_overlap(list_of_tuples[chromosome],read_start,read_end-1,overlap=min_overlap,returnall=True)
					else:
						continue
				except AssertionError:			# in case you want to run pyReadCounters with a smaller GTF. This should ignore any errors
					#sys.stderr.write("AssertionError @ %s\t%s\t%s\t%s\n" % (chromosome,strand,read_start,read_end))
					pass
				if search_results:
					for result in search_results:
						gene_start,gene_end,gene = result
						#print "gene start: %s\tgene end: %s\t gene: %s" % (gene_start,gene_end,gene)
						coordinates = np.arange(read_start,read_end)
						#print "read_start: %s\tread_end: %s" % (read_start,read_end)
						#print "coordinate length = %s" % len(coordinates)
						nucleotides = len(coordinates[(coordinates <= gene_end) & (coordinates >= gene_start)])
						#print "overlap = %s" % nucleotides
						try:
							if sense and strand == self.gtf.strand(gene):
								for i in self.gtf.annotations(gene):
									self.annotations_count[i] += nucleotides
									self.datadictionary[i][gene][0] += nucleotides
								self.gene_hits[gene] += nucleotides
								self.hits_count += coverage
								self.sense_hits_count += nucleotides
								self.cDNA_count[gene] += 1
								selectedgenes.append(gene)
							if anti_sense and strand != self.gtf.strand(gene):
								for i in self.gtf.annotations(gene):
									self.annotations_count[i] += nucleotides
									self.datadictionary[i][gene][1] += nucleotides
								self.gene_hits[gene] += nucleotides
								self.hits_count += coverage
								self.anti_sense_hits_count += nucleotides
								self.cDNA_count[gene] += 1
								selectedgenes.append(gene)
						except LookupError:
							continue
				self.count[interval]["features"] = selectedgenes


	def printHitTable(self,out_file=None,rpkm=False):
		"""Does what it says. You have to run at least countReads and countGeneHits methods first before you can use the printHitTable method. You can manually set
		the name of the output file using the 'out_file' argument. Note that once you have used this method the dictionary that stores all the gene information will be destroyed.
		This is done to preserve memory."""
		assert self.hits_count, "\n\nYou need to run the countGeneHits method first before you can use the printHitTable method.\n"
		self.__setInsertVariables()
		file_type = "hittable"
		if out_file:
			self.file_name = out_file
		file_name = self.__createFileHandles(file_type)
		file_out  = open(file_name, "w")
		file_out.write("# generated by Counters version %s, %s\n" % (__version__,time.ctime()))
		file_out.write("# %s\n" %(' '.join(sys.argv)))
		file_out.write("# total number of reads\t%d\n" % self.total_reads)
		file_out.write("# total number of mapped %s:\t%d\n" % (self.__insert,self.__insert2))
		file_out.write("# total number of paired reads\t%d\n" % self.paired_reads)
		file_out.write("# total number of single reads\t%d\n" % self.single_reads)
		file_out.write("# total number of %s overlapping genomic features\t%d\n" % (self.__insert3,self.hits_count))
		file_out.write("# \tsense\t%d\n" % (self.sense_hits_count))
		file_out.write("# \tanti-sense\t%d\n" % (self.anti_sense_hits_count))
		if rpkm:
			file_out.write("# feature\tsense_overlap\tsense-RPKM\tanti-sense_overlap\tanti-sense-RPKM\tcDNA count\n")
		else:
			file_out.write("# feature\tsense_overlap\tanti-sense_overlap\tcDNA count\n")		 
		for annotation,count in sorted(list(self.annotations_count.items()), key=lambda k_v: k_v[1],reverse=True):
			total_sense,total_anti_sense = [sum(i) for i in zip(*iter(self.datadictionary[annotation].values()))]
			if rpkm:
				total_sense_rpkm = int()
				total_anti_sense_rpkm = int()
				for gene,(sense,anti_sense) in sorted(self.datadictionary[annotation].items()):
					total_sense_rpkm += self.__calcRPKM(gene,sense)
					total_anti_sense_rpkm += self.__calcRPKM(gene,anti_sense)
				file_out.write("\n## %s\t%s\t%.3f\t%s\t%.3f\n" % (annotation,total_sense,total_sense_rpkm,total_anti_sense,total_anti_sense_rpkm))
			else:
				file_out.write("\n## %s\t%s\t%s\n" % (annotation,total_sense,total_anti_sense))
			for gene,(sense,anti_sense) in sorted(list(self.datadictionary[annotation].items()), key=lambda k_v1_v2: k_v1_v2[1][0],reverse=True):
				if rpkm:
					file_out.write("%s\t%s\t%.3f\t%s\t%.3f\t%s\n" % (gene,sense,self.__calcRPKM(gene,sense),anti_sense,self.__calcRPKM(gene,anti_sense),self.cDNA_count[gene]))
				else:
					file_out.write("%s\t%s\t%s\t%s\n" % (gene,sense,anti_sense,self.cDNA_count[gene]))
		self.sense_gene_hits = defaultdict(int)
		self.anti_sense_gene_hits = defaultdict(int)
		file_out.close()

	def __calcRPKM(self,gene,gene_hits):
		""" calculates the reads per kilobase per million mapped reads for a given gene
		Example:
		No.of mapped reads =3
		lenth of transcript=300 bp
		Total no. of reads =10,000
		rpk = 3/(300/1000) = 3/0.3 = 10
		rpkm = 10 / (10,000/1,000,000) = 10/ 0.01 = 1000
		"""
		coordinates = self.gtf.geneIterCoordinates(gene,coordinates=self.sequence,output="list")         # The length of the transcript is calculated using itercoordinates.
		try:
			gene_length = len([item for sublist in coordinates for item in sublist])                     # The reason for this is to make it possible to calculate FPKM/RPKM for features such as introns and exons
		except:
			gene_length = len(coordinates)
		rpk = float(gene_hits)/(gene_length/1000.0)
		rpkm = rpk /(float(self.mapped_reads)/1000000.0)
		return rpkm

	def __mutsAnnotationString(self,substitutions,deletions):
		"""Makes a CIGAR-type string for mutations in cDNAs"""
		mutlist = list()
		for pos in sorted(set(substitutions+deletions)):
			subsstring = str()
			delsstring = str()
			if pos in substitutions : subsstring = "S"
			if pos in deletions		: delsstring = "D"
			mutsstring = "%s%s%s" % (pos+1,subsstring,delsstring)	# add 1 to convert them to 1-based coordinates
			if subsstring or delsstring:
				mutlist.append(mutsstring)
		if mutlist:
			return ",".join(mutlist)
		else:
			return None

	def __setInsertVariables(self):
		"""does what it says"""
		self.__insert	= "reads"
		self.__insert2	= self.mapped_reads
		self.__insert3	= "reads"
		if self.duplicatesremoved:
			self.__insert	= "cDNAs"
			self.__insert3	= "reads"
		if self.readsareclustered:
			self.__insert	= "clusters"
			self.__insert3	= "cDNAs"
		if self.densities:
			self.__insert3	= "nucleotides"

	def __createFileHandles(self,file_type,file_extension="txt"):
		""" does what it says """
		filename = str()
		filename = "%s_%s_%s.%s" % (self.file_name,file_type,self.__insert,file_extension)
		self.file_list.append(filename)
		return filename

	def printIntronUTROverlapToGTF(self,min_overlap=1,out_file=None,extension="gtf"):
		"""Calculates how often a reads that were mapped to a gene overlapped with UTRs,intron or exons. Only does this for sense hits!"""
		assert self.gtf, "\n\nYou need to load a GTF annotation file using the readGTF method before you can use the printIntronUTROverlap method\n"
		assert self.hits_count, "\n\nYou need to run the countGeneHits method first before you can use the printIntronUTROverlap method.\n"
		self.__setInsertVariables()
		feature_counter = defaultdict(int)
		file_type		= "intron_and_UTR_overlap"
		file_extension	= "gtf"
		if out_file:
			self.file_name = out_file
		file_name = self.__createFileHandles(file_type,file_extension)
		file_out = NGSFileWriter(file_name)
		file_out.write("##gff-version 2\n")
		file_out.write("# generated by Counters version %s, %s\n" % (__version__,time.ctime()))
		file_out.write("# %s\n" %(' '.join(sys.argv)) )
		file_out.write("# total number of %s:\t%d\n" % (self.__insert,self.total_reads))
		file_out.write("# total number of mapped %s:\t%d\n" % (self.__insert,self.__insert2))
		file_out.write("# total number of paired reads:\t%d\n" % (self.paired_reads))
		file_out.write("# total number of single reads:\t%d\n" % (self.single_reads))
		file_out.write("# total number of overlapping genomic features\t%d\n" % (self.hits_count))
		file_out.write("# \tsense\t%d\n" % (self.sense_hits_count))
		file_out.write("# \tanti-sense\t%d\n" % (self.anti_sense_hits_count))
		file_out.write("# chromosome\tsource\tfeature\tstart\tend\t%s\tstrand\t.\tattributes\n" % (self.__insert3))
		for interval in sorted(self.count):		# sort by chromsome and start position
			chromosome,strand,start,end,substitutions,deletions = interval
			number_of_reads = self.count[interval]["coverage"]
			for gene in self.count[interval]["features"]:
				if gene != "no_matches":
					[five_UTR,three_UTR] = self.gtf.utrCoordinates(gene)
					if five_UTR:
						if overlap(start,end-1,five_UTR[0],five_UTR[1],overlap=min_overlap):
							mutsstring = self.__mutsAnnotationString(substitutions,deletions)
							feature_counter["5UTR"] += number_of_reads
							file_out.writeGTF(chromosome,self.__insert,"5UTR",start,end,score=number_of_reads,strand=self.gtf.strand(gene),gene_name=gene,gene_id=self.gtf.gene2orf(gene),comments=mutsstring)
					if three_UTR:
						if overlap(start,end-1,three_UTR[0],three_UTR[1],overlap=min_overlap):
							mutsstring = self.__mutsAnnotationString(substitutions,deletions)
							feature_counter["3UTR"] += number_of_reads
							file_out.writeGTF(chromosome,self.__insert,"3UTR",start,end,score=number_of_reads,strand=self.gtf.strand(gene),gene_name=gene,gene_id=self.gtf.gene2orf(gene),comments=mutsstring)
					introns = sorted(self.gtf.intronCoordinates(gene))
					if introns:
						for coord in introns:
							if overlap(start,end-1,coord[0],coord[1],overlap=min_overlap):
								mutsstring = self.__mutsAnnotationString(substitutions,deletions)
								feature_counter["intron"] += number_of_reads
								file_out.writeGTF(chromosome,self.__insert,"intron",start,end,score=number_of_reads,strand=self.gtf.strand(gene),gene_name=gene,gene_id=self.gtf.gene2orf(gene),comments=mutsstring)
		file_out.write("# total number:\n")
		file_out.write("#\t5'UTR:\t%d\n" % (feature_counter["5UTR"]))
		file_out.write("#\t3'UTR:\t%d\n" % (feature_counter["3UTR"]))
		file_out.write("#\tintrons:\t%d\n" % (feature_counter["intron"]))
		feature_counter = None		# empty the counter, no need to keep this into memory
		file_out.close()

	def printCountResultsToGTF(self,out_file=None,extension="gtf"):
		"""Generates a GTF output of the data analyses. If you want the gene names to be included in the GTF output file, add
		genes=True to the option. For this to work you do need to run the countGeneHits method first"""
		assert self.count, "\n\nNo reads found overlapping with genomic features. Potential reasons\n(1) The chromosome names in your GTF file are not identical to the chromosome names in your SAM/BAM or Novo file.\n(2) You have to run at least the countReads method first before you can print your results.\n"
		self.__setInsertVariables()
		file_type = "count_output"
		file_extension = extension
		if out_file:
			self.file_name = out_file
		file_name = self.__createFileHandles(file_type,file_extension)
		file_out = NGSFileWriter(file_name)
		file_out.write("##gff-version 2\n")
		file_out.write("# generated by Counters version %s, %s\n" % (__version__,time.ctime()))
		file_out.write("# %s\n" %(' '.join(sys.argv)) )
		file_out.write("# total number of %s:\t%d\n" % (self.__insert,self.total_reads))
		file_out.write("# total number of mapped %s:\t%d\n" % (self.__insert,self.__insert2))
		file_out.write("# total number of paired reads:\t%d\n" % (self.paired_reads))
		file_out.write("# total number of single reads:\t%d\n" % (self.single_reads))
		file_out.write("# total number of overlapping genomic features:\t%d\n" % (self.sense_hits_count+self.anti_sense_hits_count))
		file_out.write("#\tsense:\t%d\n" % (self.sense_hits_count))
		file_out.write("#\tanti-sense:\t%d\n" % (self.anti_sense_hits_count))
		file_out.write("# chromosome\tsource\tfeature\tstart\tend\t%s\tstrand\t.\tattributes\n" % (self.__insert3))
		for interval in sorted(self.count):
			gene_name = str()
			gene_id = str()
			chromosome,strand,read_start,read_end,substitutions,deletions = interval
			number_of_reads = self.count[interval]["coverage"]
			genes = self.count[interval]["features"]
			mutsstring = self.__mutsAnnotationString(substitutions,deletions)
			if genes:
				gene_name = ",".join(genes)
				gene_id = ",".join([self.gtf.gene2orf(gene) for gene in genes])
			else:
				gene_name = "no_matches"
				gene_id = "no_matches"
			file_out.writeGTF(chromosome,self.__insert,"interval",read_start,read_end,score=number_of_reads,strand=strand_converter(strand),gene_name=gene_name,gene_id=gene_id,comments=mutsstring)
		file_out.close()

	def printFileStats(self,out_file=None):
		"""Prints alignment file_stats to a file. User can supply its own output file name, which overrides default output"""
		assert self.count, "\n\nNo reads found overlapping with genomic features. Potential reasons\n(1) The chromosome names in your GTF file are not identical to the chromosome names in your SAM/BAM or Novo file.\n(2) You have to run at least the countReads method first before you can print your results.\n"
		self.__setInsertVariables()
		file_type = "file_statistics"
		if out_file:
			self.file_name = out_file
		file_name = self.__createFileHandles(file_type)
		file_out = open(file_name, "w")
		cumulative_hits = 0
		file_out.write("# generated by Counters version %s, %s\n" % (__version__,time.ctime()))
		file_out.write("# %s\n" %(' '.join(sys.argv)) )
		file_out.write("# total number of %s\t%d\n" % (self.__insert,self.total_reads))
		file_out.write("# total number of mapped %s:\t%d\n" % (self.__insert,self.__insert2))
		file_out.write("# total number of paired reads\t%d\n" % (self.paired_reads))
		file_out.write("# total number of single reads\t%d\n" % (self.single_reads))
		file_out.write("#\n# cDNA\tCumulative number of reads\n")
		self.file_list.append(file_name)
		for read_nr,key in enumerate(sorted(self.count),start=1):
			cumulative_hits += self.count[key]["coverage"]
			file_out.write("%d\t%d\n" % (read_nr,cumulative_hits))
		file_out.close()
