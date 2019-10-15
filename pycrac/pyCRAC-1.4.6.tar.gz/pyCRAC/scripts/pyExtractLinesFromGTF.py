#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2018"
__version__		= "0.0.3"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyExtractLinesFromGTF.py
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

def getGenes(line,attribute="gene_name"):
	"""Looks for the gene_name in attributes and returns associated gene names, if any"""
	gene_regex	   = re.compile("\"(.*)\"")
	attributefield = list()
	genes		   = list()
	try:
		attributefield = line.split("\t")[8]
	except IndexError:
		return []
	attribute_list = attributefield.split(";")
	for i in attribute_list:
		if re.search("\\b%s\\b" % attribute,i):	# only attributes with the whole word "gene_name" or "gene_id" will be selected!
			genes = gene_regex.findall(i)
			if genes:
				return genes[0].split(",")
	if not genes:
		for i in attribute_list:
			if re.search("gene_id",i):
				genes = gene_regex.findall(i)
				if genes:
					return genes[0].split(",")
	else:
		return []

def grep(input_file,output_file,genes_list,remove=False):
	gene_line_dict = dict()
	genes_list = set(genes_list)
	genes = set()
	output_file.write("##gff-version 2\n# %s\n" % " ".join(sys.argv))
	for line in input_file:
		if line[0] == "#":
			continue
		genes = set(getGenes(line))
		if remove:
			if genes_list & genes:
				continue
			else:
				output_file.write(line)
		else:
			if genes_list & genes:
				output_file.write(line)

def extractGenesFromGTF(genes_list,inputfile,outputfile,remove=False):
	genes = list()
	with open(genes_list, "r") as genes_list:
		for line in genes_list:
			genes.append(line.strip())
	grep(inputfile,outputfile,genes,remove=remove)

def main():
	parser = OptionParser(usage="usage: %prog --gtf gtf_file -g genes.list", version="%prog "+__version__)
	parser.add_option("--gtf",dest="gtf_file",metavar="Yourfavoritegtf.gtf",help="type the path to the gtf file that you want to use. By default it expects data from the standard input.",default=None)
	parser.add_option("-g", "--genes_file", dest="genes",help="name of your gene list or annotations list file (1 column)", metavar="FILE",default=None)
	parser.add_option("-o","--outfile",dest="outfile",help="type the name and path of the file you want to write the output to. Default is standard output",default=None)
	parser.add_option("-a","--attribute", dest="attribute",choices=["gene_name","gene_id","transcript_name","transcript_id"], help="from which attribute do you want to extract names? Choices: gene_name, gene_id, transcript_name, transcript_id", default="gene_name")
	parser.add_option("-v", dest="remove",action="store_true",help="similar to grep -v option. Remove the genes from the GTF that are in the gene list",default=False)
	(options, args) = parser.parse_args()
	data = sys.stdin
	out	 = sys.stdout
	if options.outfile:
		out = open(options.outfile,"w")
	if options.gtf_file:
		data = open(options.gtf_file,"r")
	extractGenesFromGTF(options.genes,data,out,remove=options.remove)

if __name__ == "__main__":
	main()
