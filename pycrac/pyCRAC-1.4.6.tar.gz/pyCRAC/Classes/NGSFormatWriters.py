#!/usr/bin/python

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2018"
__version__     = "0.0.4"
__credits__     = ["Sander Granneman"]
__maintainer__  = "Sander Granneman"
__email__       = "sgrannem@staffmail.ed.ac.uk"
__status__      = "Production"

##################################################################################
#
#   pyCRAC NGSFormatWriters.py
#
#
#   Copyright (c) Sander Granneman 2019
#   
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#
##################################################################################

import sys
from pyCRAC.Classes.Exceptions import *

class NGSFileWriter():
    """ Converts transposed numpy arrays in to various NGS output formats """
    def __init__(self,outfile=None):
        self.attributestring = str()
        if not outfile:
            self.outfile = sys.stdout
        elif hasattr(outfile,'read'):
            self.outfile = outfile
        else:
            self.outfile = open(outfile,"w")
                    
    def rgbColorCodes(self,color):
        """ returns the RGB code for the color of interest. More or less randomly picked colors from a website """
        colorcode = {
                "white" : "255,255,255",
                "black" : "0,0,0",
                "gray"  : "190,190,190",
                "blue"  : "0,0,255",
                "cyan"  : "0,255,255",
                "aquamarine" : "127,255,170",
                "green" : "0,100,0",
                "yellow": "255,255,0",
                "gold"  : "218,165,32",
                "brown" : "139,69,19",
                "beige" : "245,245,220",
                "wheat" : "245,222,179",
                "chocolate" : "210,105,30",
                "salmon": "233,150,122",
                "orange": "255,165,0",
                "tomato": "255,99,71",
                "red"   : "255,0,0",
                "pink"  : "255,20,147",
                "plum"  : "221,160,221",
                "violet": "238,130,238",
                "purple": "160,32,240"
        }
        if color in colorcode:
            return colorcode[color]
        else:
            raise LookupError("\ncould not find the color in the colorcode dictionary.\nPlease choose from the following:\n%s\n" % "\n".join(colorcode.keys()))

    def write(self,string):
        """ writes any string to the output file """
        self.outfile.write(string)
    
    def close(self):
        """ closes the output file """
        self.outfile.close()

    def writeTrackLine(self,track_type="bed",name="User_supplied",description="User_supplied",colorbystrand="red,blue",color="black"):
        """ writes a track line for the UCSC genome browser. Note that UCSC has poor support for the sgr format. The colorbystrand 
        variable indicates the colors for each strand. "red,blue" means that features located on the '+' strand will be colored
        red and features on the '-' strand will be colored blue.
        Example: track type=bed name='User_supplied_track' description='User_supplied_track' colorByStrand='225,0,0 0,0,225'"""
        types = ["bed","bedGraph","gtf","gff"]
        color = self.rgbColorCodes(color)
        twocolors     = colorbystrand.split(",")
        colorbystrand = "%s %s" % (self.rgbColorCodes(twocolors[0]),self.rgbColorCodes(twocolors[1]))
        if track_type not in types:
            raise LookupError("\ncould not find %s in the types array.\nPlease choose from the following:\n%s\n" % (track_type,", ".join(types)))
        self.outfile.write("track type=%s name='%s' description='%s' color='%s' colorByStrand='%s'\n" % (track_type,name,description,color,colorbystrand))             
                    
    def writeBedgraph(self,chromosome,start,end,hits):
        """ writes a bedgraph output string to a file. Note that these are 1-based coordinates."""
        self.outfile.write("%s\t%s\t%s\t%s\n" % (chromosome,start+1,end+1,hits))
            
    def writeBed(self,chromosome,start,end,strand,name=".",score="."):
        """ writes a bed output string to a file. Note that these are 0-based coordinates."""
        self.outfile.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (chromosome,start,end,name,score,strand))

    def writeSgr(self,chromosome,position,hits):
        """ takes data in transposed numpy arrays and writes it in sgr format to a specified output file. Only allows data from one chromosome and strand.
        Note that these are 1-based coordinates."""
        self.outfile.write("%s\t%s\t%s\n" % (chromosome,position+1,hits)) 

    def writeGTF(self,seqname,source,feature,start,end,score=".",strand=".",frame=".",gene_name=None,transcript_name=None,gene_id=None,transcript_id=None,exon_number=None,comments=None):  
        """method to feed the individual features of the GTF file to the writer, which prints the variables into a string. Note that these are 1-based coordinates."""
        self.attributestring = str()
        #for i in [start,end]:
        #    if not isinstance(i,int) or not isinstance(i,float):
        #    	sys.stderr.write("seqname:\t%s\nsource:\t%s\nstart:\t%s\nend:\t%s\nscore:\t%s\n" % (seqname,source,start,end,score))
        #        raise TypeError("\n%s position needs to be an integer or a float\n" % i)
        if gene_id:         self.attributestring += "gene_id \"%s\"; " % gene_id
        if gene_name:       self.attributestring += "gene_name \"%s\"; " % gene_name
        if transcript_id:   self.attributestring += "transcript_id \"%s\"; " % transcript_id
        if transcript_name: self.attributestring += "transcript_name \"%s\"; " % transcript_name
        if exon_number:     self.attributestring += "\"%s\"; " % exon_number
        if comments:        self.attributestring += "# %s;" % comments
        if not self.attributestring: self.attributestring = "."
        self.outfile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (seqname,source,feature,start+1,end,score,strand,frame,self.attributestring))

    def writeGFF(self,seqname,source,feature,start,end,score=".",strand=".",frame=".",gene_name=None,transcript_name=None,gene_id=None,transcript_id=None,exon_number=None):  
        """method to feed the individual features of the GTF file to the writer, which prints the variables into a string. Note that these are 1-based coordinates."""
        self.attributestring = str()
        #for i in [start,end]:
        #    if not isinstance(i,int) or not isinstance(i,float):
        #    	sys.stderr.write("seqname:\t%s\nsource:\t%s\nstart:\t%s\nend:\t%s\nscore:\t%s\n" % (seqname,source,start,end,score))
        #        raise TypeError("\n%s position needs to be an integer or a float\n" % i)
        if gene_id:         self.attributestring += "ID=\"%s\"; " % gene_id
        if gene_name:       self.attributestring += "name=\"%s\"; " % gene_name
        if transcript_id:   self.attributestring += "Alias=\"%s\"; " % transcript_id
        if not self.attributestring: self.attributestring = "."
        self.outfile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (seqname,source,feature,start+1,end,score,strand,frame,self.attributestring))
