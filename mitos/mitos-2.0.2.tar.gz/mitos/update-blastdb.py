'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

Generate the files needed for blasting
'''

from update import prepareFiles

import argparse
import glob
import logging
import os.path
import sys

import bedfile
import gb

usage = "generate blast data bases from the genbank files in a directory"

parser = argparse.ArgumentParser(description=usage)

parser.add_argument("--indir", action="append",
                    required=True, metavar="DIR", help="input directory")
parser.add_argument("--beddir", action="append",
                    required=False, metavar="DIR", help="input bed directory")

parser.add_argument("--outdir", action="store",
                    required=True, metavar="DIR", help="output directory")
parser.add_argument("--codss", action="store", type=float, metavar="FRACTION", default=0.01,
                    help="minimum fraction of appearances of a codon (per gene and code) as start/stop to be accepted as start/stop")
parser.add_argument("--codin", action="store", type=float, metavar="FRACTION", default=0.001,
                    help="maximum fraction of appearances of a codon (per gene and code) as inner codon to be accepted as stop")
parser.add_argument("--keepin", action="store_true", default=False,
                    help="keep statistics on inner codons in dumped data")


args = parser.parse_args()

logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)


gbfiles = []
bedfiles = []

for id in args.indir:
    gbfiles += glob.glob('%s/*.gb' % (id))
if args.beddir:
    for id in args.beddir:
        bedfiles += glob.glob('%s/*.bed' % (id))

data = []
for gbfile in gbfiles:
    data.append(gb.gbfromfile(gbfile))

    if args.beddir == None:
        continue

    b = os.path.splitext(os.path.basename(gbfile))[0]
    bed = None
    for bedf in bedfiles:
        if b in bedf:
            bed = bedf
            break
    if bed == None:
        sys.stderr.write("no bed found for %s" % b)
        sys.exit()
    beddata = bedfile.bedfromfile(bed)
    data[-1].features = beddata.features

prepareFiles(data, args.outdir, args.codss, args.codin, args.keepin)
