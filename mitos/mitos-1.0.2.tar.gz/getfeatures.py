#!/usr/bin/venv python

'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

create a nice output of genetic codes
'''

from __future__ import print_function
from optparse import OptionParser
from os.path import isfile, isdir
from os import listdir
import sys

from gb import gbfromfile
from bedfile import bedfromfile
from tbl import tblfromfile

usage = "usage: %prog [options] gbfiles"
parser = OptionParser(usage)
parser.add_option("-o", "--outfile", action="store", type="string",
                  metavar="FILE", help="write values to FILE (default: stdout)")

parser.add_option("-p", dest="atype", action="append", type="string",
                  metavar="TYPE", help="allow only features of type TYPE")
parser.add_option("-P", dest="ftype", action="append", type="string",
                  metavar="TYPE", help="forbid all features of type TYPE")

parser.add_option("-n", dest="aname", action="append", type="string",
                  metavar="NAME", help="allow only features with name NAME")
parser.add_option("-N", dest="fname", action="append", type="string",
                  metavar="NAME", help="forbid all features with name NAME")

parser.add_option("-t", dest="atax", action="append", type="string",
                  metavar="TAX", help="allow only entries with TAX in the taxonomy")
parser.add_option("-T", dest="ftax", action="append", type="string",
                  metavar="TAX", help="forbid all entries with TAX in the taxonomy")
parser.add_option("-f", dest="format", action="store", type="string", default="> %strand %a %n\n%s", metavar="FORMAT",
                  help="output format: %name=feature name, %type=feature type, %start=feature start, %stop=feature end, %strand=feature strand, %s=sequence, %a=accession, %n=name")
parser.add_option("--max", action="store_true", default=False,
                  help="consider only max score part per gene")
(options, args) = parser.parse_args()


# TODO if no file is given -> take from db
# check arguments
# no input files / dirs given?
if len(args) == 0:
    print("no input file given")
    print(usage)
    sys.exit(1)

# outfile and outdir given ?
if options.outfile == None:
    ohandle = sys.stdout
else:
    ohandle = open(options.outfile, "w")

files = []  # input files
for arg in args:
    if isfile(arg):
        files.append(arg)
    elif isdir(arg):
        for f in listdir(arg):
            if isfile(arg + "/" + f) and (f.endswith(".gb") or f.endswith(".bed") or f.endswith(".tbl")):
                files.append(arg + "/" + f)
    else:
        sys.stderr.write("no such file or directory %s -> skipping\n" % arg)

# contruct data and gene orders
for file in files:

    if file.endswith(".bed"):
        gb = bedfromfile(file)
    elif file.endswith(".tbl"):
        gb = tblfromfile(file)
    else:
        gb = gbfromfile(file)

    if not gb.is_allowed(options.atax, options.ftax):
        continue

    if options.max:
        gb.dellowscoreparts()

    for f in gb.getfeatures(options.aname, options.fname, options.atype, options.ftype):
        out = options.format
        out = out.replace("%feature", str(f))
        out = out.replace("%name", f.name)
        out = out.replace("%type", f.type)
        out = out.replace("%start", str(f.start))
        out = out.replace("%stop", str(f.stop))
        out = out.replace("%len", str(f.length(gb.circular, gb.size)))
        out = out.replace("%strand", str(f.strand))
        out = out.replace("%trans", str(f.translation))
        out = out.replace("%bed", str(f.bedstr(gb.accession)))
        out = out.replace("%gff", str(f.bedstr(gb.accession)))
        # out = out.replace( "%tax", gb.taxonomy[2] )
        out = out.replace("%a", gb.accession)
        out = out.replace("%n", gb.name)
        out = out.replace("%taxid", str(gb.taxid))

        if file.endswith(".gb") or file.endswith(".embl"):
            out = out.replace(
                "%s", str(gb.sequence.subseq(f.start, f.stop, f.strand)))

#        ss = str( gb.sequence.subseq( f.start, f.stop, f.strand ) )
#        out = out.replace( "%s", ss[ 3 * ( len( ss ) / 3 ) :] )

        print(out)
