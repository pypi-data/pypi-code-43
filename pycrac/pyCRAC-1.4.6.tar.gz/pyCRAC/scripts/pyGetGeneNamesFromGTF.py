#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2018"
__version__		= "0.0.4"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyGetGeneNamesFromGTF.py
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

def getGenes(line,attribute="gene_name"):
	"""Looks for the gene_name in attributes and returns associated gene names, if any"""
	gene_regex	   = re.compile("\"(.*)\"")
	altgene_regex  = re.compile("=(.*)")
	attributefield = list()
	genes		   = list()
	try:
		attributefield = line.split("\t")[8]
	except IndexError:
		return []
	attribute_list = attributefield.split(";")
	for i in attribute_list:
		if re.search("\\b%s\\b" % attribute,i):
			genes = gene_regex.findall(i)
			if not genes:
				genes = altgene_regex.findall(i)
			if genes:
				return genes[0].split(",")
	if not genes:
		for i in attribute_list:
			if re.search("gene_id",i):
				genes = gene_regex.findall(i)
				if not genes:
					genes = altgene_regex.findall(i)
				if genes:
					return genes[0].split(",")
	else:
		return []
						
def returnGenes(data,attribute="gene_name",totalcount=False):
	"""Returns a list with gene names"""
	genelist	 = set()
	gene_counter = defaultdict(int)
	for line in data:
		if line[0] is not "#":
			genes = getGenes(line,attribute)
			if genes:
				for i in genes:
					if totalcount:
						gene_counter[i] += int(line.strip().split("\t")[5])
					else:
						gene_counter[i] += 1
					genelist.add(i)
			else:
				sys.stdout.write("No genes found in line:\n%s" % line)
	if not genelist:
		sys.stderr.write("could not find any %s attributes.\nPlease choose a different attribute\n" % (attribute))
	
	return genelist,gene_counter
		
def main():
	parser = OptionParser(usage="usage: %prog [options] --gtf=myfavgtf --count", version="%s" % __version__)
	parser.add_option("--gtf",dest="gtf_file",metavar="Yourfavoritegtf.gtf",help="type the path to the gtf file that you want to use. By default it expects data from the standard input.",default=None)
	parser.add_option("-o","--outfile",dest="outfile",help="type the name and path of the file you want to write the output to. Default is standard output",default=None)		
	parser.add_option("-a","--attribute", dest="attribute",choices=["gene_name","gene_id","transcript_name","transcript_id"], help="from which attribute do you want to extract names? Choices: gene_name, gene_id, transcript_name, transcript_id", default="gene_name")
	parser.add_option("--count",dest="count",action="store_true",help="To count the occurence for each source/annotation in the gtf file",default=False)
	parser.add_option("--totalcount",dest="total",action="store_true",help="To count the occurence for each source/annotation in the gtf file including the total number of intervals mapped to that feature ",default=False)
	(options, args) = parser.parse_args()
	data = sys.stdin
	out	 = sys.stdout
	getcounts = False
	if options.outfile:
		out = open(options.outfile,"w")
	if options.gtf_file:
		data = open(options.gtf_file,"r")
	if options.count or options.total:
		getcounts = True
	genes,counter = returnGenes(data,options.attribute,totalcount=options.total)
	if genes:
		if getcounts:
			for name in sorted(genes):
				out.write("%s\t%s\n" % (name,counter[name]))
		else:
			for name in sorted(genes):
				out.write("%s\n" % name)

if __name__ == "__main__":
	main()