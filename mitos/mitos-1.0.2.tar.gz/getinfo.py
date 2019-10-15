#!/usr/bin/venv python

'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

get infos from a set of gb-files
'''

from __future__ import print_function
from optparse import OptionParser
from os.path import isfile, isdir, exists
# import pickle
from os import listdir
import sys

from gb import gbfromfile

usage = "usage: %prog [options] gbfiles"
parser = OptionParser(usage)
parser.add_option("-o", "--outfile", action="store", type="string",
                  metavar="FILE", help="write values to FILE (default: stdout)")
parser.add_option("-f", dest="format", action="store", type="string", default=">%a\n%g", metavar="FORMAT",
                  help="output format: %n=name, %a=accession, %taxid: taxid, %c: code table, %s: size, %t: taxonomy string")
parser.add_option("-t", dest="atax", action="append", type="string",
                  metavar="TAX", help="allow only entries with TAX in the taxonomy")
parser.add_option("-T", dest="ftax", action="append", type="string",
                  metavar="TAX", help="forbid all entries with TAX in the taxonomy")

(options, args) = parser.parse_args()

# check arguments
# no input files / dirs given?
if len(args) == 0:
    print("no input file given")
    print(usage)
    sys.exit(1)

files = []  # input files
for arg in args:
    if isfile(arg):
        files.append(arg)
    elif isdir(arg):
        for f in listdir(arg):
            if isfile(arg + "/" + f):
                files.append(arg + "/" + f)
    else:
        sys.stderr.write("skipping %s\n" % arg)

if len(files) == 0:
    sys.stderr.write("no files given\n")
    sys.exit()

# outfile and outdir given ?
if options.outfile == None:
    ohandle = sys.stdout
else:
    ohandle = open(options.outfile, "w")


for arg in files:
    if arg.endswith(".gb") or arg.endswith(".embl"):
        gb = gbfromfile(arg)
    else:
        sys.stderr.write("skipping %s\n" % arg)
#    sys.stderr.write( "%s\n" % arg )

    if not gb.is_allowed(options.atax, options.ftax):
        continue

    out = options.format
    out = out.replace("%a", gb.accession)
    out = out.replace("%n", gb.name)
    out = out.replace("%taxid", str(gb.taxid))
    out = out.replace("%c", str(gb.transl_table))
    out = out.replace("%s", str(gb.size))
    out = out.replace("%t", " ".join(gb.taxonomy))
    out = out.replace("%r", "\n".join([str(x) for x in gb.references]))
    ohandle.write("%s\n" % out)

    # for r in gb.references:
    #    print r.authors, r.journal, r.title

# outfile and outdir given ?
if options.outfile != None:
    ohandle.close()
