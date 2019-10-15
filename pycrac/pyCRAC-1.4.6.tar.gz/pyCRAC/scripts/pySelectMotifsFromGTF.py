#!/usr/bin/python
# coding: utf-8

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2019"
__version__     = "0.0.3"
__credits__     = ["Sander Granneman"]
__maintainer__  = "Sander Granneman"
__email__       = "sgrannem@ed.ac.uk"
__status__      = "Production"

##################################################################################
#
#   pySelectMotifsFromGTF.py
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
import re
from optparse import *

def motif2Regex(motif):
    regex=str()
    degnuc = {
                "R" : "[A,G]",
                "Y" : "[C,T]",
                "S" : "[G,C]",
                "W" : "[A,T]",
                "K" : "[G,T]",
                "M" : "[A,C]",
                "B" : "[C,G,T]",
                "D" : "[A,G,T]",
                "H" : "[A,C,T]",
                "V" : "[A,C,G]",
                "N" : "[A,C,G,T]",
                "A" : "A",
                "T" : "T",
                "U" : "U",
                "G" : "G",
                "C" : "C"
                }
                    
    for nucs in motif:
        regex += str(degnuc[nucs.upper()])
    return regex

def selectMotifs(input_file=None,output_file=None,motif=None,score=0,length=None,mutations=False):
    count_total_lines = 0
    count_found_motifs = 0
    motif = motif2Regex(motif)
    if output_file:
        output = open(output_file, "w")
    else:
        output = sys.stdout
    while True:
        line = input_file.readline()
        if not line:
            break
        if line[0] == "#":
            output.write(line)
        else:
            count_total_lines += 1
            Fld = line.strip().split("\t")
            if length and len(Fld[2]) != length:
                continue
            if re.search(motif,Fld[2],re.I) and float(Fld[5]) >=float(score):
                output.write(line)
                count_found_motifs += 1
                                        
def main():
    parser = OptionParser(usage="usage: %prog [options] --gtf=mymotifdata.gtf -m CTTG -z 5.0 -l 4 -o CTTG.gtf", version="%s" % __version__)
    parser.add_option("--gtf",dest="gtf_file",metavar="Yourfavoritegtf.gtf",help="type the path to the gtf file that you want to use. By default it expects data from the standard input",default=None)
    parser.add_option("-o","--output",dest="output_file",metavar="FILE",help="Optional.Specify the name of the output file. Default is standard output. Make sure it has the .gtf extension!",default=None)
    parser.add_option("-m","--motif",dest="motif",metavar="KBCTTG",help="Specify the motif you want extract from the GTF file",default=None)
    parser.add_option("-z","--Z_score",dest="zscore",metavar="15.0",type="float",help="Set a minimum k-mer Z-score. Default=0",default=0)
    parser.add_option("-l","--length",dest="length",metavar="4",type="int",help="Set a limit for the k-mer length. By default it picks all the k-mer seuences that match the specified sequence/pattern",default=None)
    (options, args) = parser.parse_args()
    data = sys.stdin
    if options.gtf_file:
        data = open(options.gtf_file,"r")          
    if len(sys.argv) < 1:
        parser.error("usage: %prog [options] -f filename. Use -h or --help for options")
    if not options.motif:
        parser.error("\nYou forgot to input your motif sequence\n")
    selectMotifs(input_file=data,output_file=options.output_file,motif=options.motif,score=options.zscore,length=options.length)

if __name__ == "__main__":
    main()