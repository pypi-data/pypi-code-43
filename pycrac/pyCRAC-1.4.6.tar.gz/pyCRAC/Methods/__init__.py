#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2018"
__version__		= "0.3.4"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@staffmail.ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	Methods
#
#	CONTAINS USEFUL BITS OF CODE FOR NGS DATA PROCESSING
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

import numpy as np
import sys
import os
import io
import re
import six
import array

try:
	file_types = (file, io.IOBase)

except NameError:
	file_types = (io.IOBase,)

#------------------------------------------------------------------------------------------------------------
# Numpy array conversion methods
#------------------------------------------------------------------------------------------------------------

def contigousarray2Intervals(a):
	""" Converts lists and numpy arrays containing consecutive numbers to intervals.
	For example: 
	>>> a = np.array([1,3,4,5,6,7,8,10,11,12,13,14,17,18,19])
	>>> intervallist = contigousarray2Intervals(a)
	>>> print(intervallist)
	[(1, 1),(3, 8), (10, 14), (17, 19)]
	
	"""
	start = None
	end	  = None
	intervallist = list()
	for nr,i in enumerate(list(a)):
		if not start:
			start = i
		try:
			if a[nr+1] == i + 1:
				continue
			elif a[nr+1] > i+1:
				end = i
				intervallist.append((start,end))
				start = a[nr+1]
		except IndexError:
			if start:
				end = i
				intervallist.append((start,end))
			break
	return intervallist

def steparray2Intervals(a):
	""" Converts step arrays into a list containing tuples of intervals and coverage.
	Useful for making bed or bedGraph files. The first two values of the tuple are genomic start and end positions, respectively.
	The third value in the tuple is the total number of reads covering the start and end positions.
	
	For example:
	>>> a = np.array([0,0,0,0,1,1,2,2,3,3,3,4,3,3,3,2,1,1,1,0,0,0,0,1,1,1,1,2,2,2,3,3,3,4,5,6,4,4,4,4,4,4,3,3,3,3,2,2,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0]) 
	>>> intervallist = steparray2Intervals(a)
	>>> print(intervallist)
	[(4, 5, 1), (6, 7, 2), (8, 10, 3), (11, 11, 4), (12, 14, 3), (15, 15, 2), (16, 18, 1), (19, 22, 0), (23, 26, 1), (27, 29, 2),
	(30, 32, 3), (33, 33, 4), (34, 34, 5), (35, 35, 6), (36, 41, 4), (42, 45, 3), (46, 47, 2), (48, 50, 1), (51, 55, 0), (56, 58, 1)]
	
	Bedgraph files are zero-based so the first coordinate should always start with a zero.
	"""
	start = 0
	intervallist = list()
	for i in np.where(np.diff(a)!=0)[0]:
		if not start:
			start = i
		else:
			intervallist.append((start,i,int(a[i])))
			start = i
	return intervallist

def mergeShortIntervals(intervals,mindistance=5):
	""" Merges intervals very close to each other with their neighbors.
	[(62352.0, 62450.0),(62452.0, 62491.0),(71760.0, 71806.0),(71808.0, 71820.0)]
	should become:
	(62352.0, 62491.0),(71760.0, 71820.0)
	
	"""
	newintervals = list()
	while intervals:
		first = intervals.pop(0)
		try:
			second = intervals.pop(0)
		except:
			break
		if second[0]-first[1]<= mindistance:
			intervals.insert(0,(first[0],second[1]))
		else:
			newintervals.append(first) # only put the first interval
			intervals.insert(0,second) # put the second back and start again
	return newintervals

def flattenListofArrays(array):
	""" Takes a list of arrays or tuples and flattens them into a single list """
	return [item for sublist in array for item in sublist]

def mergeIntervalCoordinates(a,b):
	""" merges overlapping interval coordinates. Example:
	a = [(3218948, 3219354),(3215871, 3217986)]
	b = [(3218953, 3219006),(3219170, 3219216)]

	mergeIntervalCoordinates(a,b) returns:

	[(3215871, 3217986),(3218948, 3218952),(3219007, 3219169),(3219217, 3219354)]

	"""
	newcoord = list()
	for i in a:
		if i:
			coords = np.arange(i[0],i[1]+1)
			for j in b:
				index = np.where(np.in1d(coords,np.arange(j[0],j[1]+1)))[0]
				coords = np.delete(coords,index)
			newcoord.extend(contigousarray2Intervals(coords))
	newcoord.sort()
	return newcoord

#------------------------------------------------------------------------------------------------------------
# file indexing tools
#------------------------------------------------------------------------------------------------------------

"""
	How to use these indexing tools. Example:
	>>> # make an index file:
	>>> makeBinaryIndexFile(fn)
	>>> findex = readFileIndex(fn)	# this assumes an index file already exists, otherwise it will make it
	>>> f = open(fn, 'rb')
	>>> position = 3				# position in file you want to go to is line 3
	>>> print(readline(position, f, findex)) # prints line 3
	2-micron	reads	exon	2903	2941	8	+	.	gene_id "INT_0_3,R0020C"; gene_name "INT_0_3,REP1";
	>>> seek(position,f,index)		# does the same
	>>> print(next(f)
	2-micron	reads	exon	2903	2941	8	+	.	gene_id "INT_0_3,R0020C"; gene_name "INT_0_3,REP1";
	
"""
def reader(f):
	""" function that reads the file in order to make an index """
	blocksize = 1024 * 1024
	blockstart = 0
	while True:
		block = f.read(blocksize)
		if not block: break
		inblock = 0
		while True:
			nextnl = block.find(b'\n', inblock)
			if nextnl < 0:
				blockstart += len(block)
				break
			yield nextnl + blockstart
			inblock = nextnl + 1

def makeBinaryIndexFile(fn):
	""" makes a binary index of a file """
	with open(fn, 'rb') as f:
		# result format: x[0] is tot # of lines,
		# x[N] is byte offset of END of line N (1+)
		result = array.array('L', [0])
		result.extend(reader(f))
		result[0] = len(result) - 1
	with open(fn + '.indx', 'wb') as p:
		result.tofile(p)

def readline(n,f,findex):
	""" seeks to a beginning of a line at 'n' in file 'f' using index 'findex' and returns the line """
	f.seek(findex[n] + 1)
	bytes = f.read(findex[n+1] - findex[n])
	return bytes.decode('utf8')

def seek(linenumber,file,index):
	""" jumps to position in file at linenumber using index """
	file.seek(index[linenumber])
	six.next(file)

def readFileIndex(indexfile):
	""" reads the file index and stores it into an object """
	with open("%s.indx" % indexfile,'rb') as file:
		findex = array.array('l')
		findex.fromfile(file, 1)
		findex.fromfile(file, findex[0])
		findex[0] = -1
	return findex

#------------------------------------------------------------------------------------------------------------

def processChromFile(file,ignore=[]):
	""" Takes a file containing chromosome names and chromosome lengths and returns it as a dictionary.
	The keys in the dictionary are the chromosome names, the values are the chromosome lengths.
	The chromosome info file should be a tab delimited file formatted as follows:
	#chromosome length
	chrI	23452453
	chrII	34244244
	etc...
	"""
	chromdict = dict()
	for line in file:
		if line.startswith("#"): continue
		Fld = line.strip().split()
		chromosome = Fld[0]
		if ignore and chromosome in ignore:
			continue
		else:
			chromdict[Fld[0]] = int(Fld[1])
	return chromdict

def splitData(datafile, directory="./", max_open_filehandles=100):
	""" generates a tmp file for each chromosome in the data using the tempfile module. NOTE that these need to be removed manually by using the unlink function.
	for example:
	temp = tempfile.NamedTemporaryFile(prefix='%s_' % chr,dir='./',suffix='.tmp', delete=False)
	temp.unlink(temp.name)

	By attaching a path to the directory variable you can direct the files to a specific directory.
	Returns a dictionary where the keys are the chromosome names and the values are the file names.
	"""
	import tempfile
	from collections import deque

	# This dictionary contains the complete map of chromosome names to temp file handles (open or closed)
	chromosomes = dict()

	# This dictionary contains a map of chromosome names to open file handles only
	open_tempfiles = dict()

	# This deque represents a FIFO queue to keep track of the order in which temp files were opened. When the maximum
	# number of open filehandles is reached, the oldest file is closed
	open_chromosome_queue = deque()

	with open(datafile, "r") as data:		 # going through the data line by line
		for line in data:
			if line.startswith("track"):
				continue
			if line.startswith("#"):
				continue
			chr = line.strip().split("\t")[0]
			if chr not in open_tempfiles and chr in chromosomes:
				# open a new filehandle using an existing tempfile, closing an old filehandle if necessary
				open_chromosome_queue.append(chr)
				if len(open_chromosome_queue) > max_open_filehandles:
					chromosome_file_to_close = open_chromosome_queue.popleft()
					open_tempfiles[chromosome_file_to_close].close()
					del open_tempfiles[chromosome_file_to_close]
				temp_filepath = os.path.join(directory, chromosomes[chr].name)
				open_tempfiles[chr] = open(temp_filepath, 'w')

			elif chr not in open_tempfiles and chr not in chromosomes:
				# create a new filehandle with a new tempfile, closing an old filehandle if necessary
				temp = tempfile.NamedTemporaryFile(mode='w',prefix='%s_' % chr, dir=directory, suffix='.tmp', delete=False)
				chromosomes[chr] = temp
				open_chromosome_queue.append(chr)
				if len(open_chromosome_queue) > max_open_filehandles:
					chromosome_file_to_close = open_chromosome_queue.popleft()
					open_tempfiles[chromosome_file_to_close].close()
					del open_tempfiles[chromosome_file_to_close]
				open_tempfiles[chr] = temp

			open_tempfiles[chr].write(line)

			# optional sanity check
			if (set(open_chromosome_queue) != set(open_tempfiles.keys())):
				print(list(set(open_chromosome_queue)))
				print(open_tempfiles.keys())
				raise Exception('There is a mismatch between the the open chromosome queue and the dictionary of open filehandles')

	for i in open_tempfiles:  # closing all the output files
		open_tempfiles[i].close()
	return chromosomes		  # this returns all the chromosome names and temp output file names so that one can keep track of how many tmp files there are and what the file names are.

def splitString(string,step=50):
	""" splits a string in blocks of step. Useful for chopping up sequences into smaller pieces """
	return "\n".join([string[i:i+step] for i in range(0,len(string),step)])

#------------------------------------------------------------------------------------------------------------
# SAM format functions
# No longer used because of pysam but still useful to have around
#------------------------------------------------------------------------------------------------------------

def flag2Bitstring(flag):
	""" decodes the SAM integer flag in the second column and returns a bit string """
	bitstring = str()
	bitvalues = [1024,512,256,128,64,32,16,8,4,2,1]		# The bitstrings are 11 characters long
	count_ones = 0
	for numbers in bitvalues:
		if flag - numbers < 0:
			bitstring += '0'
			continue
		if flag - numbers > 0:
			bitstring += '1'
			count_ones += 1
			flag = flag - numbers
			continue
		if flag - numbers == 0:
			bitstring += '1'
			count_ones += 1
			flag = flag - numbers
			continue
		if flag == 0:
			bitstring += '0'

	if count_ones > 0:
		return bitstring
	else:
		return None

def decodeBitstring(bitstring):
	""" decodes bitstrings generated by the flag2bitstring method """
	dictionary = {
		'PAIRED'	   : False,
		'PROPER_PAIR'  : False,
		'MAPPED_QUERY' : True,
		'MAPPED_MATE'  : True,
		'STRAND_QUERY' : "F",
		'STRAND_MATE'  : "R",
		'READ_TYPE'	   : "S",
		'HIT_REPEAT'   : "U",
		'READ_QUAL_CHECK' : True,
		'PCR_DUPLICATE': False
	}

	if bitstring is None:
		return None
	if bitstring[-1] == '1':	# The read is paired in sequencing no matter whether it is mapped in a paired
		dictionary['PAIRED'] = True
		# then if the read is indeed paired the following needs to be tested:
		if bitstring[-2] == '0':	# The read is mapped in a proper pair (depends on the protocol, normally inferred during alignment)
			dictionary['PROPER_PAIR'] = True
		if bitstring[-3] == '1':	# The query sequence itself is unmapped
			dictionary['MAPPED_QUERY'] = False
		if bitstring[-4] == '1':	# The mate sequence is unmapped
			dictionary['MAPPED_MATE'] = False
		if bitstring[-6] == '0':	# The strand of the mate
			dictionary['STRAND_MATE'] = "F"
		if bitstring[-7] == '1':	# The read is the first read in the paired
			dictionary['READ_TYPE'] = "L"
		if bitstring[-8] == '1':	# The read is the second read in the paired
			dictionary['READ_TYPE'] = "R"
	if bitstring[-5] == '1':	# The strand of the query
		dictionary['STRAND_QUERY'] = "R"
	if bitstring[-9] == '1':	# The read has multiple alignment locations in the genome
		dictionary['HIT_REPEAT'] = "R"
	if bitstring[-10] == '1':	# The read read fails vendor quality check
		dictionary['READ_QUAL_CHECK'] = False
	if bitstring[-11] == '1':	# The read read is a PCR or an optical duplicate
		dictionary['PCR_DUPLICATE'] = True

	return dictionary

#------------------------------------------------------------------------------------------------------------
# DNA and RNA manipulation functions
#------------------------------------------------------------------------------------------------------------

def complement(sequence):
	""" returns the complement of the DNA sequence """
	basecomplement = str()
	complement = {"A":"T","G":"C","C":"G","T":"A","a":"t","c":"g","g":"c","t":"a"}
	letters	 = list(sequence)
	for letter in letters:
		if letter in complement:
			basecomplement += complement[letter]
		else:
			basecomplement += letter
	return basecomplement

def reverse_complement(sequence):
	""" Returns the reverse complement of a DNA string """
	basecomplement = str()
	complement = {"A":"T","G":"C","C":"G","T":"A","a":"t","c":"g","g":"c","t":"a"}
	letters	 = list(sequence)
	for letter in letters:
		if letter in complement:
			basecomplement += complement[letter]
		else:
			basecomplement += letter
	return basecomplement[::-1]

def translate(sequence,type="DNA",frame=1):
	""" Translates a DNA or RNA sequence into a protein sequence. Type variable specifies whether the source is DNA (type='DNA') or RNA (type='RNA') """
	assert type in ["DNA","RNA"], "supported types are 'DNA' or 'RNA'\n"
	protein	 = str()
	codonmap = {"UUU":"F", "UUC":"F", "UUA":"L", "UUG":"L",
				"UCU":"S", "UCC":"S", "UCA":"S", "UCG":"S",
				"UAU":"Y", "UAC":"Y", "UAA":"*", "UAG":"*",
				"UGU":"C", "UGC":"C", "UGA":"*", "UGG":"W",
				"CUU":"L", "CUC":"L", "CUA":"L", "CUG":"L",
				"CCU":"P", "CCC":"P", "CCA":"P", "CCG":"P",
				"CAU":"H", "CAC":"H", "CAA":"Q", "CAG":"Q",
				"CGU":"R", "CGC":"R", "CGA":"R", "CGG":"R",
				"AUU":"I", "AUC":"I", "AUA":"I", "AUG":"M",
				"ACU":"T", "ACC":"T", "ACA":"T", "ACG":"T",
				"AAU":"N", "AAC":"N", "AAA":"K", "AAG":"K",
				"AGU":"S", "AGC":"S", "AGA":"R", "AGG":"R",
				"GUU":"V", "GUC":"V", "GUA":"V", "GUG":"V",
				"GCU":"A", "GCC":"A", "GCA":"A", "GCG":"A",
				"GAU":"D", "GAC":"D", "GAA":"E", "GAG":"E",
				"GGU":"G", "GGC":"G", "GGA":"G", "GGG":"G",}

	sequence = list(sequence.upper())
	if type == "DNA":
		for i,nuc in enumerate(sequence):
			if nuc == "T":
				sequence[i] = "U"
		sequence = "".join(sequence)
	for i in range(frame-1,len(sequence),3):        # find codons in the sequence starting at position 1 in sequence
		codon = sequence[i:i+3]
		if not protein and codonmap[codon] == "M":  # if the start codon has been found
			protein += codonmap[codon]
		elif protein and len(codon) != 3:
			sys.stderr.write("\nWarning! Protein is a truncated sequence\n")
			break
		elif protein and codonmap[codon]:
			protein += codonmap[codon]
		elif protein and codonmap[codon] == "STOP":
			break
	return protein

#------------------------------------------------------------------------------------------------------------

def basequality(letter,ftype="L"):
	""" Returns a phred or solexa base quality from a character. The ftype indicates 'sanger' or 'solexa' or 'illumina'
	S - Sanger		  Phred+33,	 raw reads typically (0, 40)
	X - Solexa		  Solexa+64, raw reads typically (-5, 40)
	I - Illumina 1.3+ Phred+64,	 raw reads typically (0, 40)
	J - Illumina 1.5+ Phred+64,	 raw reads typically (3, 40) with 0=unused, 1=unused, 2=Read Segment Quality Control Indicator (bold)
	L - Illumina 1.8+ Phred+33,	 raw reads typically (0, 41)
	Default = L"""
	setone = ["L","S"]
	settwo = ["X","J","I"]
	if ftype in setone:
		return ord(letter) - 33
	elif ftype in settwo:
		return ord(letter) - 64
	else:
		raise RuntimeError("could not correctly interpret the file type of the raw dataset\nPlease use phred,solexa or illumina\n")

def getfilename(filepath):
	""" Returns the file name without path and extension"""
	if isinstance(filepath,file_types):
		return "standard_input"
	else:
		return os.path.splitext(os.path.basename(filepath))[0]

def splitter(line):
	""" This function splits the line at double quotes and returns the second object in the array"""
	line = line.replace('\"',"")
	return line.split()[1]

def check_list(list_input,key): # Initially I thought of using the builtin python 'set' module and its add() method but the check_list runs significantly faster when used with lists!
	""" This function checks whether a key already exists in a list.  is often used in this module to make sure that lists do not contain duplicate gene or ORF"""
	if key not in list_input:
		list_input.append(key)
		return True
	else:
		return False

def find_key(dic, val):
	""" Return the key of dictionary dic given the value"""
	return [k for k, v in six.iteritems(dic) if v == val][0]

def readisDuplicate(chromosome,tuple_input,tracker_dict,activate=False):
	""" Takes a set() list and checks whether tuples with read_coordinates are already present
	in the set. If not, it will add the coordinates to the list, else it will return False.
	The reason for using sets is because membership tests are much faster than regular python lists and 
	the list doesn't need to be ordered."""
	input = str(tuple_input)  # making a string out of the input coordinates makes comparison a lot easier/faster
	if activate is False:
		return False
	elif input in tracker_dict[chromosome]:
		return True
	else:
		tracker_dict[chromosome].add(input)
		return False

#------------------------------------------------------------------------------------------------------------
# STRAND MANIPULATION FUNCTIONS
#------------------------------------------------------------------------------------------------------------

def orientation(read_strand,gene_strand):
	""" returns sense if read and gene strand are the same. If not it returns anti-sense.
	if the interval has no strand (i.e. '.') then it returns sense. """
	if read_strand == "F": read_strand = "+"
	if read_strand == "R": read_strand = "-"
	if read_strand == "." or gene_strand == ".":
		return "sense"
	elif read_strand == gene_strand:
		return "sense"
	else:
		return "anti-sense"

def strand_converter(strand):
	""" Converts the novoalign strand characters to GTF strand characters (i.e. 'F' to '+' and 'R' to '-')"""
	if not strand:
		return None
	elif strand == "F":
		return "+"
	elif strand == "R":
		return "-"
	# just in case the strand is already + or -, then return the strand itself:
	elif strand == "-" or strand == "+":
		return strand
	else:
		raise TypeError("\nThe strand information could not be interpreted.\nPlease verify your input\n")

def reverse_strand(strand):
	""" Reverses the strand"""
	if	 strand == "F": return "R"
	elif strand == "R": return "F"
	elif strand == "+": return "-"
	elif strand == "-": return "+"
	else:
		raise TypeError("\nThe strand information could not be interpreted.\nPlease verify your input\n")

def get_sequence(chromosome,strand,upstream,downstream,tab_dict):
	""" Returns the nucleotide sequence from "chromosome" using upstream and downstream coordinates.Usage: get_sequence(chromosome,strand,upstream,downstream,dictionary)"""
	if strand == "+" or strand == "F" and tab_dict[chromosome][upstream:downstream]:
		return tab_dict[chromosome][upstream:downstream]
	elif strand == "-" or strand == "R" and tab_dict[chromosome][upstream:downstream]:
		return reverse_complement(tab_dict[chromosome][upstream:downstream])
	else:
		raise NoSequenceError("\ncould not find a sequence for chromosome %s and coordinates %d-%d, please check your input\n" %(chromosome,upstream,downstream))

#------------------------------------------------------------------------------------------------------------
# OVERLAP FUNCTIONS
#------------------------------------------------------------------------------------------------------------

def calc_list_overlap(coordinates,gene_iter_coordinates,list_type="read"):
	""" Returns a numpy array containing zeros and ones, ones indicate the position in the gene where reads were found to overlap with 
	locations of mutations. List_type 'read' indicates that the coordinates array contains read coordinates, wherease list_type 'muts'
	indicates an array with genomic locations of mutations, such as deletions or substitutions"""
	if isinstance(gene_iter_coordinates,np.ndarray):
		if list_type == "read":
			return np.where((gene_iter_coordinates >= coordinates[0]) & (gene_iter_coordinates <= coordinates[1]),1,0)
		elif list_type == "muts":
			array = np.zeros(len(gene_iter_coordinates),dtype=int)
			for position in coordinates:
				array += np.where((gene_iter_coordinates == position),1,0)
			return array
		else:
			raise TypeError("please specify whether the first array contains read coordinates (i.e. list_type='read') or a list of mutations (i.e. list_type='muts')\n")
	else:
		raise TypeError("your gene range coordinates are not numpy arrays! Please double check your input\n")

def intron_overlap(read_start,read_end,intron_coordinates,sequence):
	""" Determines whether a read overlaps introns"""
	overlap = False
	if sequence == "genomic":
		overlap = False
	if sequence == "coding" and intron_coordinates:
		copy_b = list()
		copy_b.extend(intron_coordinates)
		while copy_b:
			intron_coord = copy_b.pop()
			intron_down = intron_coord[1]
			intron_up = intron_coord[0]
			if read_end <= intron_down and read_start >= intron_up:
				overlap = True
			if read_end >= intron_down and read_start <= intron_down:
				overlap = True
			if read_start <= intron_up and read_end >= intron_up:
				overlap = True
	return overlap

def old_overlap(a, b, c, d):	# first overlap function. Slowest of all three
	""" Checks whether there is overlap between read coordinates and chromosomal coordinates.
	a and b are read coordinates, whereas c and d are gene coordinates"""
	if a >= c and  b <= d:
		return True
	elif a < c and b <= d and b >= c:
		return True
	elif a >= c and b > d and a <= d:
		return True
	elif a < c and b >= d:
		return True
	else:
		return False

def overlap(a, b, c, d, overlap=1):		# improved overlap function. Marginally faster than the first one
	""" Checks whether there is overlap between read coordinates and chromosomal coordinates.
	a and b are read coordinates, whereas c and d are gene coordinates. The read or cluster can 
	be larger than the gene itself. The result of this function can return zero, which means that two positions are identical.
	This is why the overlap value should always be subtracted by 1.
		
	Possibilities:
	
	   start	   start				   end						   start				  end	   start				   end						 
	 ---|			|----------------------|							|----------------------|		|----------------------|
		|---					<-overlap->								<-overlap->						<-------overlap-------->
	   end	(overlap=0)	   f0					f1		 f0						   f1				 f0							   f1
							|-------------------|		  |------------------------|				  |----------------------------|
		   
	f0					  f1							   f0					   f1	   f0					  f1					  
	 |----------------------|								|----------------------|		|----------------------|
				  <-overlap->								 <-overlap->					 <-------overlap-------->
				 start				 end	 start					  end				 start						  end
				   |------------------|		  |------------------------|				  |----------------------------|
		   
	Won't work for the following:
	
	 f0			   f1			 start			end			start		   end			  f0			f1						 
	 |--------------| <-overlap-> |--------------|			  |-------------| <-overlap-> |-------------| 
						
	"""
	overlap -= 1
	if b - c >= overlap and d - a >= overlap:
		return True
	else:
		return False

def numpy_overlap(numpy_array,start,end,overlap=1,returnall=False):	# much improved overlap function which uses numpy numerical calculations. Three to four times faster than the old ones
	""" Checks whether there is overlap between read coordinates and chromosomal coordinates but uses numpy arrays
	and numpy numerical conversions. Is much faster than regular iterations over lists. The read or cluster can be larger than the
	gene itself. The result of the overlap function can return zero, which means that two positions in the intervals are identical.
	This is why the overlap value should always be subtracted by 1.

	Possibilities:

	   start	   start				   end						   start				  end	   start				   end
	 ---|			|----------------------|							|----------------------|		|----------------------|
		|---					<-overlap->								<-overlap->						<-------overlap-------->
	   end	(overlap=0)	   f0					f1		 f0						   f1				 f0							   f1
							|-------------------|		  |------------------------|				  |----------------------------|

	f0					  f1							   f0					   f1	   f0					  f1
	 |----------------------|								|----------------------|		|----------------------|
				  <-overlap->								 <-overlap->					 <-------overlap-------->
				 start				 end	 start					  end				 start						  end
				   |------------------|		  |------------------------|				  |----------------------------|

	Won't work for the following:

	 f0			   f1			 start			end			start		   end			  f0			f1
	 |--------------| <-overlap-> |--------------|			  |-------------| <-overlap-> |-------------|

	"""
	overlap -= 1
	seqoverlap = (end - numpy_array['f0'] >= overlap) & (numpy_array['f1'] - start >= overlap)	# determines whether there is overlap between a read and gene chromosomal coordinates. Returns a bool index.

	if returnall:
		return list(numpy_array[seqoverlap])
	else:
		return list(numpy_array[seqoverlap]['f2'])		# if overlap was found, then the gene names are stored in the results list, otherwise it returns an empty list

def read_seq_overlap(seq_a,start_a,seq_b,start_b):
	end_a = start_a + len(seq_a)
	end_b = start_b + len(seq_b)
	if start_a >= start_b and start_a <= end_b:
		return ((start_a - start_b), True)
	elif start_a <= start_b and end_a >= start_b:
		return ((start_b - start_a), True)
	elif start_a < start_b and end_a < end_b:
		return ((start_b - end_a), False)
	elif start_a > start_b and end_a > end_b:
		return ((start_a - end_b), False)
	elif start_a == start_b:
		return (0,True)
	else:
		return (None, False)

#------------------------------------------------------------------------------------------------------------

def sortbyvalue(d):
	""" This function takes a dictionary and generates a list in which the keys are sorted by their value"""
	items = [(v, k) for k, v in list(d.items())]
	items.sort()
	items.reverse()				# so largest is first
	items = [(k, v) for v, k in items]
	return items

def sortbylistlength(d):
	""" This function takes a dictionary and generates a list in which the keys are sorted by their value"""
	items = [(len(v), k) for k, v in list(d.items())]
	items.sort()
	items.reverse()				# so largest is first
	items = [(k, v) for v, k in items]
	return items

def is_numeric(obj):
	""" Checks whether a list or numpy array has numbers """
	attrs = ['__add__', '__sub__', '__mul__', '__div__', '__pow__']
	return all(hasattr(obj, attr) for attr in attrs)
