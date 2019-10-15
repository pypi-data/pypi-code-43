#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "0.0.5"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "Production"

##################################################################################
#
#	pyGTF2bed.py
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
from optparse import *
from pyCRAC.Classes.NGSFormatWriters import NGSFileWriter
from pyCRAC.Classes.NGSFormatReaders import NGSFileReader

def gtf2bed(gtf_file,outfile,name=None,description=None,color="black",colorbystrand="red,blue"):
	""" converts gtf files to bed6 files the way I like it """
	gtfreader = NGSFileReader(gtf_file)		# gtf reader object
	bedwriter = NGSFileWriter(outfile)		# bed writer object
	if name or description:
		if not name: name = "User_Supplied_Track"
		if not description: description = "User_Supplied_Track" 
		bedwriter.writeTrackLine("bed",name,description,colorbystrand)	# write trackline information for visualization in the UCSC genome browser
	while gtfreader.readGTFLine():
		names = list()
		if gtfreader.gene_name:
			names.append(gtfreader.gene_name)
		elif gtfreader.gene_id:
			names.append(gtfreader.gene_id)
		if gtfreader.transcript_name:
			names.append(gtfreader.transcript_name)
		elif gtfreader.transcript_id:
			names.append(gtfreader.transcript_id)
		if names:
			names = list(set(names))	# remove any duplicates, for example if the gene_name and transcript_name are identical
		else:
			names = [name]			# if it can't find any attributes, just print the name of the experiment in the output file
		# write to output file:

		bedwriter.writeBed(gtfreader.chromosome,gtfreader.start,gtfreader.end-1,gtfreader.strand,",".join(names),gtfreader.score)
		
def main():
	parser = OptionParser(usage="usage: %prog [options] --gtf=gtf_file.gtf", version="%s" % __version__)
	files = OptionGroup(parser, "File input options")
	files.add_option("--gtf",dest="gtf_file",metavar="Yourfavoritegtf.gtf",help="type the path to the gtf file that you want to convert. Default is standard input",default=None)
	files.add_option("-o","--outfile",dest="outfile",help="type the name and path of the file you want to write the output to. Default is standard output",default=None)
	ucsc = OptionGroup(parser, "These options can be used to add and modify a track line for the UCSC genome browser")
	ucsc.add_option("-n","--name",dest="name",help="For the USCS track line: provide a track name. Default is none ",default=None)
	ucsc.add_option("-d","--description",dest="description",help="For the USCS track line: provide a track description. Default is none ",default=None)
	ucsc.add_option("--color",dest="color",help="select the track color. Default = black",default="black")
	ucsc.add_option("-s","--colorstrands",dest="strands",help="select the colors for each strand. Default = 'red,blue'",default="red,blue")
	parser.add_option_group(ucsc)
	parser.add_option_group(files)
	(options, args) = parser.parse_args()
	data = sys.stdin
	out	 = sys.stdout
	
	if options.gtf_file: data = open(options.gtf_file,"r")
	if options.outfile : out = open(options.outfile,"w")
	
	gtf2bed(data,out,name=options.name,description=options.description,color=options.color,colorbystrand=options.strands)
	
if __name__ == "__main__":
	main()
