#!/usr/bin/python

__author__		= 'Sander Granneman'
__copyright__	= 'Copyright 2019'
__version__		= '3.3'
__credits__		= ['Sander Granneman','Hywel Dunn-Davies','Grzegorz Kudla']
__maintainer__	= 'Sander Granneman'
__email__		= 'sgrannem@staffmail.ed.ac.uk'
__status__		= 'Production'

##################################################################################
#
#	Barcodes
#
#
#	Copyright (c) Sander Granneman 2019
#	
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the 'Software'), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#	
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#	
#	THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#	THE SOFTWARE.
#
##################################################################################

import time
import sys
import re
import six
import itertools
import gzip
from collections import defaultdict
from pyCRAC.Methods import sortbyvalue,getfilename
from pyCRAC.Classes.Exceptions import *


def allPossibleCombinations(barcode):
	''' returns a list of all possible combinations of a barcode with one mismatch'''
	combinations = list()
	for i in range(len(barcode)):
		newbarcode = list(barcode)
		newbarcode[i] = 'N'
		combinations.append(''.join(newbarcode))
	return combinations
	
def Npermutations(sequence):
	seq_dict		 = {'N':['A','C','G','T','N']}
	actsequence		 = [seq_dict.get(base, [base]) for base in sequence]
	all_combinations = list(map(''.join, itertools.product(*actsequence)))
	return all_combinations
	
def allPossibleNucleotideCombinations(length):
	nucleotides		= ['A','T','C','G','N']
	allcombinations = nucleotides 
	count			= 0
	while count <= length-2:
		count += 1
		allcombinations = [i+nucleotides[j] for j in range(len(nucleotides)) for i in allcombinations]
	return allcombinations
			
class BarcodeSplitter:
	''' splits fastq data based on barcode information in the 5' (!!!) adapter sequence. 
	Can also process random barcodes'''

	def __init__(self,file_type,forward,reverse,barcodefile,allowedmismatches=0,gzip=False,keepbarcode=False,search='forward'):
		self.spacer						 = '##'		# this is the character(s) that separate the header from the random barcode sequence that 
		self.randombarcodelenghts 	     = list()
		self.keepbarcode			     = keepbarcode  # in case you want to keep the barcodes in the sequencing reeds
		self.shortest_bc_length			 = int()
		self.longest_bc_length			 = int()
		self.search 					 = search
		self.total_reads				 = int()
		self.allowedmismatches			 = allowedmismatches
		self.allbarcodes				 = list()
		self.barcode_nonrandom_fragments = list()
		self.barcode_nonrandom_lengths	 = dict()
		self.barcodename				 = dict()
		self.barcode2fname				 = dict()
		self.read2barcode				 = defaultdict(str)
		self.rand_barcode_counter		 = defaultdict(int)
		self.barcode_counter			 = defaultdict(int)
		self.handles					 = dict()
		self.barcodefile				 = barcodefile
		self.forward_input				 = forward
		self.reverse_input				 = reverse
		self.fastq_f					 = None
		self.fastq_r					 = None
		self.randombarcodelengths		 = list()
		self.__filename					 = getfilename(forward)
		self.__filename_paired			 = getfilename(reverse) if reverse else None
		self.__compressoutput			 = False
		self.__allowedfiletypes			 = ['fastq','fasta','fastq.gz','fasta.gz']
		self.__outtype					 = str()
		self.filetype					 = file_type
		if self.filetype not in self.__allowedfiletypes:
			raise FormatError('\n\nCould not interpret the %s format. Please use fastq, fastq formats or gzipped fastq and fasta files	(fastq.gz or fasta.gz).\n')
		self.__processFileHandles()		# processing all the input files
		self.__processBarcodeList()		# processing the barcode names. This has to be done before creating file handles (i.e. self.__createFileHandles())
		self.__createFileHandles()		# preparing all the output files

	def __checkRandBarcodeLengths(self,firstrandombarcodes,secondrandombarcodes):
		self.randombarcodelenghts = list()
		for data in [firstrandombarcodes,secondrandombarcodes]:
			barcodelengths = set([len(i) for i in data])
			self.randombarcodelenghts.append(list(barcodelengths)[0])

	def __processFileHandles(self):
		''' Does what it says. The gzip option offers the possibility to read gzipped files '''
		if self.reverse_input:
			if self.filetype in self.__allowedfiletypes[2:]:
				self.fastq_f = gzip.open(self.forward_input,'rb')
				self.fastq_r = gzip.open(self.reverse_input,'rb')
			elif self.filetype in self.__allowedfiletypes[:2]:
				self.fastq_f = open(self.forward_input,'r')
				self.fastq_r = open(self.reverse_input,'r')
			else:
				raise FormatError('\n\nCould not interpret the %s format. Please use fastq, fastq formats or gzipped fastq and fasta files	(fastq.gz or fasta.gz).\n')
			self.handles['fastq_f'] = self.fastq_f
			self.handles['fastq_r'] = self.fastq_r
		else:
			if self.filetype in self.__allowedfiletypes[2:]:
				self.fastq_f = gzip.open(self.forward_input,'rb')
			elif self.filetype in self.__allowedfiletypes[:2]:
				self.fastq_f = open(self.forward_input,'r')
			else:
				raise FormatError('\n\nCould not interpret the %s format. Please use fastq, fastq formats or gzipped fastq and fasta files	(fastq.gz or fasta.gz).\n')
			self.handles['fastq_f'] = self.fastq_f
		
		if self.filetype == 'fasta' or self.filetype == 'fastq':
			self.__outtype = self.filetype
		else:
			self.__outtype = self.filetype[:-3]		   # removes the .gz extension
		
		if self.__compressoutput: 
			self.__outtype += '.gz'	  # add a gz extension if compressing the output files.
			
	def __createFileHandles(self):
		''' Does what it says '''
		if self.barcode_nonrandom_fragments:
			if self.__compressoutput:
				if self.reverse_input:
					self.handles['others'] = [gzip.open('%s_others.%s' % (self.__filename,self.__outtype),'wb'), gzip.open('%s_others.%s' % (self.__filename_paired,self.__outtype),'wb')]
				else:
					self.handles['others'] = gzip.open('%s_others.%s' % (self.__filename,self.__outtype),'wb')
				for names in self.allbarcodes:
					if self.reverse_input:
						self.handles[names] = [gzip.open('%s_%s_%s.%s' % (self.__filename,names,self.barcodename[names],self.__outtype), 'wb'),gzip.open('%s_%s_%s.%s' % (self.__filename_paired,names,self.barcodename[names],self.__outtype), 'wb')]
					else:
						self.handles[names] = gzip.open('%s_%s_%s.%s' % (self.__filename,names,self.barcodename[names],self.__outtype), 'wb')
			else:
				if self.reverse_input:
					self.handles['others'] = [open('%s_others.%s' % (self.__filename,self.__outtype),'w'), open('%s_others.%s' % (self.__filename_paired,self.__outtype),'w')]
				else:
					self.handles['others'] = open('%s_others.%s' % (self.__filename,self.__outtype),'w')
				for names in self.allbarcodes:
					if self.reverse_input:
						self.handles[names] = [open('%s_%s_%s.%s' % (self.__filename,names,self.barcodename[names],self.__outtype), 'w'),open('%s_%s_%s.%s' % (self.__filename_paired,names,self.barcodename[names],self.__outtype), 'w')]
					else:
						self.handles[names] = open('%s_%s_%s.%s' % (self.__filename,names,self.barcodename[names],self.__outtype), 'w')
		else:
			raise ProcessingError('\n\nYou need to process the barcode file first before creating file handles\n')
			
	def __allSeqPermutations(self,barcode):
		''' determines the number of permutations for a sequence with or without random mismatches '''
		Ncombinations	 = allPossibleCombinations(barcode)
		all_combinations = list()
		for i in Ncombinations:
			all_combinations.extend(Npermutations(i))
		return all_combinations
	
	def __nucleotideMismatches(self,fragment,trailing_nucleotides=None,mismatches=0):
		''' returns a list of all posible combinations of the barcode containing one mismatch '''
		starts		 = list()
		ends		 = list()
		combinations = list()
		if mismatches == 1:
			starts	= self.__allSeqPermutations(fragment)
		elif mismatches > 1:
			raise InputError('\n\nthis version only allows one mismatch in barcodes\n')
		else:
			starts.append(fragment)
				
		if trailing_nucleotides:
			ends.extend([''.join(i) for i in allPossibleNucleotideCombinations(trailing_nucleotides)])
		else:
			ends.append('')
		for start in starts:
			for end in ends:
				combinations.append('%s%s' % (start,end))
		return combinations
			
	def __processBarcodeList(self):
		'''processes the barcode list file and stores the information in a list'''
		randomnucs = re.compile('(N+)?([ATGC]+)+(N+)?')
		firstrandombarcodes  = list()
		secondrandombarcodes = list()
		with open(self.barcodefile, 'r') as barcode_list:
			for line in barcode_list:
				try:
					Fld = line.strip().split()		# split by anything, space or tab. In case there are spaces in the file.
					barcodeseq = Fld[0]
					samplename = Fld[1]
					self.barcodename[barcodeseq] = samplename
				except IndexError:
					continue	# in case the barcode list file has empty lines
				firstrandombarcode,index,secondrandombarcode = randomnucs.findall(barcodeseq)[0]
				firstrandombarcodes.append(firstrandombarcode)
				secondrandombarcodes.append(secondrandombarcode)
				self.barcode2fname[index] = barcodeseq
				self.allbarcodes.append(barcodeseq)
				self.barcode_nonrandom_fragments.append(index)
				self.barcode_nonrandom_lengths[barcodeseq] = len(index)
		self.__checkRandBarcodeLengths(firstrandombarcodes,secondrandombarcodes)
		self.shortest_bc_length = min([len(i) for i in self.allbarcodes])
		self.longest_bc_length	= max([len(i) for i in self.allbarcodes])
		self.barcode_nonrandom_fragments.reverse()
		for nonrandom_fragment in self.barcode_nonrandom_fragments:
			trailing_nucleotides = self.longest_bc_length - len(nonrandom_fragment) - sum(self.randombarcodelenghts)
			for sequence in self.__nucleotideMismatches(nonrandom_fragment,trailing_nucleotides,mismatches=self.allowedmismatches):
				self.read2barcode[sequence] = self.barcode2fname[nonrandom_fragment]												
	
	def processFastQFile(self):
		'''processes the fastq file'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		firstrandbarcodelength  = 0
		secondrandbarcodelength = 0
		if sum(self.randombarcodelenghts) > 0:
			firstrandbarcodelength,secondrandbarcodelength = self.randombarcodelenghts
		while True:
			try:
				name	 = str(six.next(self.fastq_f).strip())
				sequence = str(six.next(self.fastq_f).strip())
				plus	 = str(six.next(self.fastq_f).strip())
				quality	 = str(six.next(self.fastq_f).strip())
				randombarcode = str()
				self.total_reads += 1
				if self.total_reads == 1 and name[0] == '>':
					raise FileTypeError('\n\nThe file is a fasta file but the selected file type is fastq. Use the flag --file_type=fasta to process fasta files\n')
				current_frag	= sequence[firstrandbarcodelength:self.longest_bc_length-secondrandbarcodelength]
				current_barcode = self.read2barcode[current_frag]
				if current_barcode in self.handles:
					if self.keepbarcode:
						length = 0
					else:
						length = firstrandbarcodelength + self.barcode_nonrandom_lengths[current_barcode] + secondrandbarcodelength 
						if firstrandbarcodelength:
							randombarcode += sequence[:firstrandbarcodelength]
						if secondrandbarcodelength:
							randombarcode += sequence[length-secondrandbarcodelength:length]
					name = '%s%s%s' % (name,self.spacer,randombarcode)
					if self.__compressoutput:
						self.handles[current_barcode].write(b'%s\n%s\n%s\n%s\n' % (name, sequence[length:], plus, quality[length:]))
					else:
						self.handles[current_barcode].write('%s\n%s\n%s\n%s\n' % (name, sequence[length:], plus, quality[length:]))
					self.barcode_counter[current_barcode] += 1
					if randombarcode:
						self.rand_barcode_counter[randombarcode] += 1
				else:
					if self.__compressoutput:
						self.handles['others'].write(b'%s\n%s\n%s\n%s\n' % (name,sequence,plus,quality))
					else:
						self.handles['others'].write('%s\n%s\n%s\n%s\n' % (name,sequence,plus,quality))
					self.barcode_counter['no_barcode'] += 1
			except StopIteration:
				for files in self.handles:
					self.handles[files].close()
				return True
	
	def processPairedEndFastQFiles(self):
		'''processes two fastq files with paired-end data. Only works with barcodes in the forward read! Forward reaction show go as first argument!!!!!'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		assert self.fastq_r,'\n\nYou need to provide the name of the file containing the reverse sequencing data\n'
		firstrandbarcodelength  = 0
		secondrandbarcodelength = 0
		if sum(self.randombarcodelenghts) > 0:
			firstrandbarcodelength,secondrandbarcodelength = self.randombarcodelenghts
		while True:
			try:
				line_f = str()
				line_r = str()
				name_f, name_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				seq_f,	seq_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				plus_f, plus_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				qual_f, qual_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				randombarcode = str()
				self.total_reads += 1

				if self.search == 'reverse':
					current_frag	= seq_r[firstrandbarcodelength:self.longest_bc_length-secondrandbarcodelength]
					current_barcode = self.read2barcode[current_frag]
					if current_barcode in self.handles:
						if self.keepbarcode:
							length = 0
						else:
							length = firstrandbarcodelength + self.barcode_nonrandom_lengths[current_barcode] + secondrandbarcodelength
							if firstrandbarcodelength:
								randombarcode += seq_r[:firstrandbarcodelength]
							if secondrandbarcodelength:
								randombarcode += seq_r[length-secondrandbarcodelength:length]
						name_f = '%s%s%s' % (name_f,self.spacer,randombarcode)
						line_f = '%s\n%s\n%s\n%s\n' % (name_f,seq_f,plus_f,qual_f)
						line_r = '%s\n%s\n%s\n%s\n' % (name_r,seq_r[length:],plus_r,qual_r[length:])

						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles[current_barcode][0].write(line_f)
						self.handles[current_barcode][1].write(line_r)
						self.barcode_counter[current_barcode] += 1
						if randombarcode:
							self.rand_barcode_counter[randombarcode] += 1
					else:
						line_f = '%s\n%s\n%s\n%s\n' % (name_f, seq_f, plus_f, qual_f)
						line_r = '%s\n%s\n%s\n%s\n' % (name_r, seq_r, plus_r, qual_r)

						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles['others'][0].write(line_f)
						self.handles['others'][1].write(line_r)
						self.barcode_counter['no_barcode'] += 1

				elif self.search == 'forward':
					current_frag	= seq_f[firstrandbarcodelength:self.longest_bc_length-secondrandbarcodelength]
					current_barcode = self.read2barcode[current_frag]
					if current_barcode in self.handles:
						if self.keepbarcode:
							length = 0
						else:
							length = firstrandbarcodelength + self.barcode_nonrandom_lengths[current_barcode] + secondrandbarcodelength
							if firstrandbarcodelength:
								randombarcode += seq_f[:firstrandbarcodelength]
							if secondrandbarcodelength:
								randombarcode += seq_f[length-secondrandbarcodelength:length]
						name_f = '%s%s%s' % (name_f,self.spacer,randombarcode)
						line_f = '%s\n%s\n%s\n%s\n' % (name_f, seq_f[length:], plus_f, qual_f[length:])
						line_r = '%s\n%s\n%s\n%s\n' % (name_r, seq_r, plus_r, qual_r)
						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles[current_barcode][0].write(line_f)
						self.handles[current_barcode][1].write(line_r)
						self.barcode_counter[current_barcode] += 1

						if randombarcode:
							self.rand_barcode_counter[randombarcode] += 1
					else:
						line_f = '%s\n%s\n%s\n%s\n' % (name_f,seq_f,plus_f,qual_f)
						line_r = '%s\n%s\n%s\n%s\n' % (name_r,seq_r,plus_r,qual_r)
						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles['others'][0].write(line_f)
						self.handles['others'][1].write(line_r)
						self.barcode_counter['no_barcode'] += 1

			except StopIteration:
				for files in self.handles:
					if type(self.handles[files]) == list:
						for i in self.handles[files]:
							i.close()
					else:
						self.handles[files].close()
				return True
							
	def processFastAFile(self):
		'''processes a fasta file'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		firstrandbarcodelength  = 0
		secondrandbarcodelength = 0
		if sum(self.randombarcodelenghts) > 0:
			firstrandbarcodelength,secondrandbarcodelength = self.randombarcodelenghts
		while True:
			try:
				line = str()
				name	 = str(six.next(self.fastq_f).strip())
				sequence = str(six.next(self.fastq_f).strip())
				if name[0] != '>':
					raise FormatError('\n\nthe sequence name should start with an '>'\nDid not recognize the file as fasta file\n')
				randombarcode = str()
				self.total_reads += 1
				current_frag	= sequence[firstrandbarcodelength:self.longest_bc_length-secondrandbarcodelength]
				current_barcode = self.read2barcode[current_frag]
				if current_barcode in self.handles:
					if self.keepbarcode:
						length = 0
					else:
						length = firstrandbarcodelength + self.barcode_nonrandom_lengths[current_barcode] + secondrandbarcodelength 
						if firstrandbarcodelength:
							randombarcode += sequence[:firstrandbarcodelength]
						if secondrandbarcodelength:
							randombarcode += sequence[length-secondrandbarcodelength:length]
					name = '%s%s%s' % (name,self.spacer,randombarcode)
					line = '%s\n%s\n' % (name, sequence[length:])
					if self.__compressoutput:
						line = line.encode()

					self.handles[current_barcode].write(line)
					self.barcode_counter[current_barcode] += 1

					if randombarcode:
						self.rand_barcode_counter[randombarcode] += 1
				else:
					line = '%s\n%s\n' % (name,sequence)
					if self.__compressoutput:
						line = line.encode()

					self.handles['others'].write(line)
					self.barcode_counter['no_barcode'] += 1

			except StopIteration:
				for files in self.handles:
					self.handles[files].close()
				return True

	def processPairedEndFastAFiles(self):
		'''processes two fastq files with paired-end data. Only works with barcodes in the forward read! Forward reaction show go as first argument!!!!!'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		assert self.fastq_r,'\n\nYou need to provide the name of the file containing the reverse sequencing data\n'
		firstrandbarcodelength  = 0
		secondrandbarcodelength = 0
		if sum(self.randombarcodelenghts) > 0:
			firstrandbarcodelength,secondrandbarcodelength = self.randombarcodelenghts
		while True:
			try:
				line_f = str()
				line_r = str()
				name_f, name_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				seq_f,	seq_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				if name_f[0] != '>' or name_r[0] != '>':
					raise FormatError('\n\nthe sequence name should start with an '>'\nIs the file really a fasta file?\n')
				randombarcode = str()
				self.total_reads += 1
				if self.search == 'reverse':
					current_frag	= seq_r[firstrandbarcodelength:self.longest_bc_length-secondrandbarcodelength]
					current_barcode = self.read2barcode[current_frag]
					if current_barcode in self.handles:
						if self.keepbarcode:
							length = 0
						else:
							length = firstrandbarcodelength + self.barcode_nonrandom_lengths[current_barcode] + secondrandbarcodelength
							if firstrandbarcodelength:
								randombarcode += seq_r[:firstrandbarcodelength]
							if secondrandbarcodelength:
								randombarcode += seq_r[length-secondrandbarcodelength:length]
						name_f = '%s%s%s' % (name_f,self.spacer,randombarcode)
						line_f = '%s\n%s\n' % (name_f,seq_f)
						line_r = '%s\n%s\n' % (name_r,seq_r[length:])

						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles[current_barcode][0].write(line_f)
						self.handles[current_barcode][1].write(line_r)
						self.barcode_counter[current_barcode] += 1

						if randombarcode:
							self.rand_barcode_counter[randombarcode] += 1
					else:
						line_f = '%s\n%s\n' % (name_f,seq_f)
						line_r = '%s\n%s\n' % (name_r,seq_r)

						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles['others'][0].write(line_f)
						self.handles['others'][1].write(line_r)
						self.barcode_counter['no_barcode'] += 1

				elif self.search == 'forward':
					current_frag	= seq_f[firstrandbarcodelength:self.longest_bc_length-secondrandbarcodelength]
					current_barcode = self.read2barcode[current_frag]
					if current_barcode in self.handles:
						if self.keepbarcode:
							length = 0
						else:
							length = firstrandbarcodelength + self.barcode_nonrandom_lengths[current_barcode] + secondrandbarcodelength
							if firstrandbarcodelength:
								randombarcode += seq_f[:firstrandbarcodelength]
							if secondrandbarcodelength:
								randombarcode += seq_f[length-secondrandbarcodelength:length]
						name_f = '%s%s%s' % (name_f,self.spacer,randombarcode)
						line_f = '%s\n%s\n' % (name_f,seq_f[length:])
						line_r = '%s\n%s\n' % (name_r,seq_r)

						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles[current_barcode][0].write(line_f)
						self.handles[current_barcode][1].write(line_r)
						self.barcode_counter[current_barcode] += 1

						if randombarcode:
							self.rand_barcode_counter[randombarcode] += 1
					else:
						line_f = '%s\n%s\n' % (name_f,seq_f)
						line_r = '%s\n%s\n' % (name_r,seq_r)

						if self.__compressoutput:
							line_f = line_f.encode()
							line_r = line_r.encode()

						self.handles['others'][0].write(line_f)
						self.handles['others'][1].write(line_r)
						self.barcode_counter['no_barcode'] += 1

			except StopIteration:
				for files in self.handles:
					if type(self.handles[files]) == list:
						for i in self.handles[files]:
							i.close()
					else:
						self.handles[files].close()
				return True
			
	def printRandBarcodeStats(self):
		''' generates a file with random barcode statistics. '''
		if self.rand_barcode_counter:
			forwardfilename = getfilename(self.forward_input)
			random = open('%s_random_nucleotide_statistics.txt' % forwardfilename, 'w')
			random.write('# generated by Barcodes version %s, %s\n' % (__version__,time.ctime()))
			random.write('# %s\n' %(' '.join(sys.argv)) )				  
			for randseqs,value in sortbyvalue(self.rand_barcode_counter):
				random.write('%s\t%d\n' %(randseqs,value))
			random.close()
					
	def printBarcodeStats(self):
		''' generates a file with barcode statistics. '''
		if self.barcode_counter:
			forwardfilename = getfilename(self.forward_input)
			stats = open('%s_barcode_statistics.txt' % forwardfilename, 'w')
			stats.write('# generated by Barcodes version %s, %s\n' % (__version__,time.ctime()))
			stats.write('# %s\n' %(' '.join(sys.argv)) )	
			for seqs,value in sortbyvalue(self.barcode_counter):
				percentage = (float(value)/float(self.total_reads)) * 100
				stats.write('%s\t%0.2f\n' %(seqs,percentage))

							
class IndexingBarcodeSplitter(BarcodeSplitter):
	''' splits fastq data based on barcode information in the 3' (!!!) adapter sequence. 
	These are the 6-8 nucleotide illumina indexes.'''
	def __init__(self,file_type,forward,reverse,barcodefile,allowedmismatches=0,gzip=False):
		BarcodeSplitter.__init__(self,file_type,forward,reverse,barcodefile,allowedmismatches,gzip)
			
	def processFastqFileIndexes(self):
		'''sorts read data based on the index provided in the header. Example:
		@FC4290FAAXX:4:1:3:84#CAGATC/1
		The tool splits the line using the # and backslash'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		index = str()
		while True:
			try:
				line = str()
				name	 = str(six.next(self.fastq_f).strip())
				sequence = str(six.next(self.fastq_f).strip())
				plus	 = str(six.next(self.fastq_f).strip())
				quality	 = str(six.next(self.fastq_f).strip())
				self.total_reads += 1
				if self.total_reads == 1 and name[0] == '>':
					raise FileTypeError('\n\nThe file is a fasta file but the selected file type is fastq. Use the flag --file_type=fasta to process fasta files\n')
				if self.randombarcode_length:
					randombarcode	= sequence[:self.randombarcode_length]
					name			= '%s%s%s' % (name,self.spacer,randombarcode)
					self.rand_barcode_counter[randombarcode] += 1
				try:
					index = re.findall('[NATGC]{6,}',name)[0]
				except IndexError:
					raise LookupError('Could not find an index for header %s\n' % name)
				current_barcode = self.read2barcode[index]

				line = '%s\n%s\n%s\n%s\n' % (name,sequence,plus,quality)

				if current_barcode in self.handles:
					length = self.randombarcode_length + self.barcode_nonrandom_lengths[current_barcode]
					self.handles[current_barcode].write(line)
					self.barcode_counter[current_barcode] += 1
				else:
					self.handles['others'].write(line)
					self.barcode_counter['no_barcode'] += 1

			except StopIteration:
				for files in self.handles:
					self.handles[files].close()
				return True
	
	def processPairedFastqFileIndexes(self):
		'''sorts paired end read data based on the index provided in the headers'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		assert self.fastq_r,'\n\nYou need to provide the name of the file containing the reverse sequencing data\n'
		index = str()
		while True:
			try:
				line_f = str()
				line_r = str()
				name_f, name_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				seq_f,	seq_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				plus_f, plus_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())	  
				qual_f, qual_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				self.total_reads += 1
				try:
					index = re.findall('[NATGC]{6,}',name_f)[0]
				except IndexError:
					raise LookupError('Could not find an index for header %s\n' % name_f)
				current_barcode = self.read2barcode[index]

				line_f = '%s\n%s\n%s\n%s\n' % (name_f,seq_f,plus_f,qual_f)
				line_r = '%s\n%s\n%s\n%s\n' % (name_r,seq_r,plus_r,qual_r)

				if current_barcode in self.handles:
					self.handles[current_barcode][0].write(line_f)
					self.handles[current_barcode][1].write(line_r)
					self.barcode_counter[current_barcode] += 1
				else:
					self.handles['others'][0].write(line_f)
					self.handles['others'][1].write(line_r)
					self.barcode_counter['no_barcode'] += 1

			except StopIteration:
				for files in self.handles:
					if type(self.handles[files]) == list:
						for i in self.handles[files]:
							i.close()
					else:
						self.handles[files].close()
				return True
							
	def processFastAFileIndexes(self):
		'''processes a fasta file'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		while True:
			try:
				line = str()
				name	 = str(six.next(self.fastq_f).strip())
				sequence = str(six.next(self.fastq_f).strip())
				if name[0] != '>':
					raise FormatError('\n\nthe sequence name should start with an '>'\nDid not recognize the file as fasta file\n')
				self.total_reads += 1
				splitheader = re.split('[#/]',name)
				if len(splitheader) == 3:			# input = @FC4290FAAXX:4:1:3:84#CAGATC/1 Should yield CAGATC
					index = splitheader[-2]		
				elif len(splitheader) == 2:			# input = @FC4290FAAXX:4:1:3:84#CAGATC	 Should yield CAGATC
					index = splitheader[-1]
				else:
					raise LookupError('Could not find an index for header %s\n' % name)								   
				current_barcode = self.read2barcode[index]

				line = '%s\n%s\n' % (name,sequence)

				if current_barcode in self.handles:
					self.handles[current_barcode].write(line)
					self.barcode_counter[current_barcode] += 1
				else:
					self.handles['others'].write(line)
					self.barcode_counter['no_barcode'] += 1

			except StopIteration:
				for files in self.handles:
					self.handles[files].close()
				return True
							
	def processPairedEndFastAFileIndexes(self):
		'''processes two fastq files with paired-end data. Only works with barcodes in the forward read! Forward reaction show go as first argument!!!!!'''
		assert self.allbarcodes, '\n\nYou need to process the barcode file first with processBarcodeList before you can use this method\n'
		while True:
			try:
				line_f = str()
				line_r = str()
				name_f, name_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				seq_f,	seq_r	= str(six.next(self.fastq_f).strip()),str(six.next(self.fastq_r).strip())
				if name_f[0] != '>' or name_r[0] != '>':
					raise FormatError('\n\nthe sequence name should start with an '>'\nDid not recognize the file as fasta file\n')
				self.total_reads += 1
				splitheader = re.split('[#/]',name)
				if len(splitheader) == 3:			# input = @FC4290FAAXX:4:1:3:84#CAGATC/1 Should yield CAGATC
					index = splitheader[-2]		
				elif len(splitheader) == 2:			# input = @FC4290FAAXX:4:1:3:84#CAGATC	 Should yield CAGATC
					index = splitheader[-1]
				else:
					raise LookupError('Could not find an index for header %s\n' % name)								   
				current_barcode = self.read2barcode[index]

				line_f = '%s\n%s\n' % (name_f,seq_f)
				line_r = '%s\n%s\n' % (name_r,seq_r)

				if current_barcode in self.handles:
					self.handles[current_barcode][0].write(line_f)
					self.handles[current_barcode][1].write(line_r)
					self.barcode_counter[current_barcode] += 1
				else:
					self.handles['others'][0].write(line_f)
					self.handles['others'][1].write(line_r)
					self.barcode_counter['no_barcode'] += 1

			except StopIteration:
				for files in self.handles:
					if type(self.handles[files]) == list:
						for i in self.handles[files]:
							i.close()
					else:
						self.handles[files].close()
				return True