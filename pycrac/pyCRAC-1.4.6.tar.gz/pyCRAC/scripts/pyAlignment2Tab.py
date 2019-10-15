#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2018"
__version__		= "1.2.1"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyAlignment2Tab.py
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
from optparse import *
from collections import defaultdict
from pyCRAC.Methods import getfilename

def color(string):
	"""GREY, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
	NONE, BOLD, FAINT, ITALIC, UNDERLINE, BLINK, FAST, REVERSE, CONCEALED = range(8)
	#The background is set with 40 plus the number of the color, and the foreground with 30
	#These are the sequences need to get colored ouput
	RESET_SEQ = "\033[0m"
	COLOR_SEQ = "\033[1;%dm"
	BOLD_SEQ = "\033[1m"
	"""
	if re.search("H",string):
		return string
	else:
		a = list(string)
		for nr,i in enumerate(a):
			if i.islower(): # bold
				a[nr] = '\033[1m%s\033[0m' % i
			if i == "A":	# bold letters on a red background
				a[nr] = '\033[1;41;38m%s\033[0m' % i
			if i == "C":	# bold letters on a green background
				a[nr] = '\033[1;42m%s\033[0m' % i
			if i == "G":	# bold letters on a yellow background
				a[nr] = '\033[1;43m%s\033[0m' % i
			if i == "T":	# bold lettters on a green background
				a[nr] = '\033[1;44m%s\033[0m' % i
		return ''.join(a)

def countHeadGaps(string):
	""" counts the number of '-' in the beginning of the string """
	a = re.search(r'[atgcnATGCN]',string)
	return a.start()

def sortByHeadGaps(dictionary):
	""" returns a list of sorted sequences """
	return sorted([(countHeadGaps(dictionary[keys]),keys,dictionary[keys]) for keys in dictionary])
	
def printSeqGaps(sequence):
	""" prints sequence gap characters """
	string = str()
	for i in range(1,len(sequence)+1):
		if i %10 == 0:
			string += "|"
		else:
			string += "."
	return string

def printTab(filein,fileout,limit=90,removeempty=False):
	""" prints the output in the tabular format """
	fasta_dict = dict()
	readid	   = str()
	for line in filein:
		if line.startswith(">"):
			readid = line.strip()
		else:
			fasta_dict[readid] = line.strip()
	sorted_tuple_list = sortByHeadGaps(fasta_dict)
	headerlength = int(max([len(y) for x,y,z in sorted_tuple_list]))
	seq_dots   = printSeqGaps(sorted_tuple_list[0][2])
	seq_length = int(len(sorted_tuple_list[0][2]))
	frag_nr	   = int(seq_length/limit)
	for i in range(frag_nr+1):
		end = int()
		if i == frag_nr:
			end = seq_length
		else:
			end = ((i+1)*limit)
		position = str((i*limit)+1)
		adjustment = headerlength - len(position)
		position = ' ' * adjustment + position
		fragmentlist = list()
		for (nr,header,sequence) in sorted_tuple_list:
			fragment = sequence[i*limit:(i+1)*limit:]
			if re.search("[atcgATCG.]",fragment):
				adjustment = headerlength - len(header)
				header = ' ' * adjustment + header
				if fileout is sys.stdout:
					fragmentlist.append("%s\t%s\n" % (header,color(fragment)))
				else:
					fragmentlist.append("%s\t%s\n" % (header,fragment))	
		if len(fragmentlist) <= 1 and removeempty:
			continue
		fileout.write("%s\t%s %d\n" % (position,seq_dots[i*limit:(i+1)*limit:],end))			
		fileout.write("%s\n" % "".join(fragmentlist))
					
def parseSingleFile(filein):
	""" for the Galaxy server. In case all the alignments were printed to a single file. """
	datadict = defaultdict(str)
	for line in filein:
		if not line.strip():	# if the parser encounters an empty line, continue
			continue
		if line.startswith("###"):
			gene = line.strip()
			datadict[gene] = list()
		else:
			datadict[gene].append(line)
	return datadict
			
					
def main():
	parser = OptionParser(usage="usage: %prog -f myfastafile -o mytabfile --limit=90", version="%s" % __version__)
	parser.add_option("-f",dest="infile",metavar="data.fasta",help="type the path to the fasta file that you want to use. By default it expects data from the standard input.",default=None)
	parser.add_option("-o","--outfile",dest="outfile",metavar="data.tab",help="type the name and path of the file you want to write the output to. Default is standard output",default=None)
	parser.add_option("--limit",dest="limit",metavar="90",type="int",help="Allows the user to set the column width of the alignment. Default=90 characters",default=90)
	parser.add_option("--noempty",dest="noempty",action="store_true",help="only print reference sequences that have reads mapped to it. Default is False",default=False)
	parser.add_option("--singlefile",dest="singlefile",action="store_true",help="include this flag if all your alignments are in a single file, separated by empty lines",default=False)	
	(options, args) = parser.parse_args()
	data = sys.stdin
	out	 = sys.stdout
	if options.outfile:
		out = open(options.outfile,"w")
	if options.infile:
		data = open(options.infile,"r")
	if options.singlefile:
		datadict = parseSingleFile(data)
		for gene in datadict:
			out.write("\n%s\n" % gene)
			printTab(datadict[gene],out,limit=options.limit,removeempty=options.noempty)
	else:
		printTab(data,out,limit=options.limit,removeempty=options.noempty)

if __name__ == "__main__":
	main()