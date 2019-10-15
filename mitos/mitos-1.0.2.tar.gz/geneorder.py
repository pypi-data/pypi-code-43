#!/usr/bin/venv python

'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

get gene orders from a set of gb-files
@author: M. Bernt
@todo if no file is given -> take from db
'''

from __future__ import print_function
from optparse import OptionParser
from os.path import isfile, isdir, exists
# import pickle
from os import listdir
import sys

from gb import gbfromfile
from bedfile import bedfromfile
import mito

usage = "usage: %prog [options] gbfiles"
parser = OptionParser(usage)
parser.add_option("-o", "--outfile", action="store", type="string",
                  metavar="FILE", help="write values to FILE (default: stdout)")
parser.add_option("-t", dest="atax", action="append", type="string",
                  metavar="TAX", help="allow only entries with TAX in the taxonomy")
parser.add_option("-T", dest="ftax", action="append", type="string",
                  metavar="TAX", help="forbid all entries with TAX in the taxonomy")
parser.add_option("-f", dest="format", action="store", type="string", default=">%a\n%g",
                  metavar="FORMAT", help="output format: %n=name, %a=accession, %g=gene order")
# parser.add_option( "--improve", action = "store_true", default = False, help = "improve with arwen and tRNAscan from database" )
parser.add_option("--ignore", action="append", type="string",
                  metavar="NAME", help="ignore genes with name NAME")
parser.add_option(
    "--ignoreall", action="store_true", default=False, help="ignore all errors")
parser.add_option(
    "--notrna", action="store_true", default=False, help="ignore tRNAs")

parser.add_option(
    "--mad", action="store_true", default=False, help="merge adjacent duplicates")
parser.add_option("--max", action="store_true", default=False,
                  help="consider only max score part per gene")

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


trna = set(mito.trna)
genes = mito.prot + mito.rrna

if options.notrna:
    if not options.ignore:
        options.ignore = []
    options.ignore += trna

#    options.ignore.append( "trnL" )
#    options.ignore.append( "trnS" )

genes = set(genes + mito.trna)
if options.ignore:
    for i in options.ignore:
        try:
            genes.remove(i)
        except ValueError:
            break


def deltrnafeat_ovlprotrrna(gb, tf, threshold):
    """
    compute a subset of features in tf which have
        - names in trna 
        - cummulative overlap (fraction) with features from gb <= threshold
    return subset array 
    """

    global trna

    for i in range(len(tf.features) - 1, -1, -1):
        if not tf.features[i].name in trna:
            del tf.features[i]
            continue

        capsum = 0.0

        for g in gb.features:
            if g.type != "gene" and g.type != "rRNA":
                continue

            cap, cup = tf.features[i].capcup(g, gb.circular, gb.size)
            capsum += cap

        l = tf.features[i].len(True, gb.size)
        if float(capsum) / float(l) > threshold:
            del tf.features[i]

    return tf


def correct_multiplicity(gb, arwen, trnascan, threshold):
    global trna

    arwenm = {}
    trnascanm = {}
    gbm = {}

    for t in trna:
        gbm[t] = []
        arwenm[t] = []
        trnascanm[t] = []

    for i in range(len(arwen.features)):
        arwenm[arwen.features[i].name].append(i)

    for i in range(len(trnascan.features)):
        trnascanm[trnascan.features[i].name].append(i)

    for i in range(len(gb.features)):
        if not gb.features[i].name in trna:
            continue
        gbm[gb.features[i].name].append(i)

    delete = set()
    for m in gbm:

        if len(gbm[m]) == 1:
            continue
        elif len(gbm[m]) == 0:
            if len(trnascanm[m]) == 1 and len(arwenm[m]) == 0:
                gb.features.append(trnascan.features[trnascanm[m][0]])
                sys.stderr.write(
                    "%s mult 0 %s resolved trnascan\n" % (gb.accession, m))
            elif len(trnascanm[m]) == 0 and len(arwenm[m]) == 1:
                gb.features.append(arwen.features[arwenm[m][0]])
                sys.stderr.write(
                    "%s mult 0 %s resolved arwen\n" % (gb.accession, m))
            elif len(trnascanm[m]) >= 1 and len(arwenm[m]) >= 1:
                pairs = []
                for i in arwenm[m]:
                    for j in trnascanm[m]:
                        if trnascan.features[ j ].overlap( arwen.features[ i ], gb.size ) >= threshold and \
                                trnascan.features[j].name == arwen.features[i].name:
                            pairs.append((i, j))
                if len(pairs) == 1:
                    gb.features.append(trnascan.features[pairs[0][1]])
                    sys.stderr.write(
                        "%s mult 0 %s resolved trnascan+arwen\n" % (gb.accession, m))
                else:
                    sys.stderr.write(
                        "%s mult 0 %s persists\n" % (gb.accession, m))
            else:
                sys.stderr.write("%s mult 0 %s persists\n" % (gb.accession, m))
            # print len(gbm[m]), len(arwenm[m]), len(trnascanm[m])
        else:
            dcnt = 0
            d = set()
            for i in gbm[m]:
                cnt = 0
                for j in arwenm[m]:
                    if gb.features[i].overlap(arwen.features[j], gb.circular, gb.size) >= threshold and gb.features[i].name == arwen.features[j].name:
                        cnt += 1
                for j in trnascanm[m]:
                    if gb.features[i].overlap(trnascan.features[j], gb.circular, gb.size) >= threshold and gb.features[i].name == trnascan.features[j].name:
                        cnt += 1
                if cnt == 0:
                    dcnt += 1
                    d.add(i)
            if len(d) == len(gbm[m]) - 1:
                sys.stderr.write("%s mult %d %s resolved\n" %
                                 (gb.accession, len(gbm[m]), m))
                for i in d:
                    delete.add(i)
            else:
                sys.stderr.write("%s mult %d %s persists\n" %
                                 (gb.accession, len(gbm[m]), m))

    for i in range(len(gb.features) - 1, -1, -1):
        if i in delete:
            del gb.features[i]

    return gb


def correct_names(gb, arwen, trnascan, threshold):
    rename = {}

    for i in range(len(gb.features)):
        maxa = threshold
        maxaf = None

        maxt = threshold
        maxtf = None

        if not gb.features[i].name in trna and gb.features[i].name != "L" and gb.features[i].name != "S":
            continue

        for af in arwen.features:
            o = af.overlap(gb.features[i], gb.circular, gb.size)
            if o >= maxa:
                if o > maxa:
                    maxa = o
                maxaf = af

        for tf in trnascan.features:
            o = tf.overlap(gb.features[i], gb.circular, gb.size)
            if o >= maxt:
                if o > maxt:
                    maxt = o
                maxtf = tf
#        print gb.features[i], maxtf, maxt

        if maxaf != None and gb.features[i].name != maxaf.name:
            if not gb.features[i].name in rename:
                rename[gb.features[i].name] = {}
            if not maxaf.name in rename[gb.features[i].name]:
                rename[gb.features[i].name][maxaf.name] = 0
            rename[gb.features[i].name][maxaf.name] += 1

        if maxtf != None and gb.features[i].name != maxtf.name:
            if not gb.features[i].name in rename:
                rename[gb.features[i].name] = {}
            if not maxtf.name in rename[gb.features[i].name]:
                rename[gb.features[i].name][maxtf.name] = 0
            rename[gb.features[i].name][maxtf.name] += 1

            # special treatment of L and S.
            # just rename if there is no disagreement of trnascan and arwen
        if gb.features[i].name in rename and (gb.features[i].name == "S" or gb.features[i].name == "L"):
            oldname = gb.features[i].name
            if len(rename[gb.features[i].name]) == 1 and rename[gb.features[i].name].keys()[0][0] == gb.features[i].name:
                sys.stderr.write("%s rename %s %s\n" % (
                    gb.accession, gb.features[i].name, rename[gb.features[i].name].keys()[0]))
                gb.features[i].name = rename[gb.features[i].name].keys()[0]
            del rename[oldname]

        # rename "swap cycles"
    for i in range(len(gb.features)):
        if not gb.features[i].name in trna:
            continue

        memory = set()
        n = gb.features[i].name
        while 1:
            if not n in rename:
                break
            if len(rename[n]) != 1:
                break
            if n in memory:
                break
            memory.add(n)

            n = rename[n].keys()[0]
#            print "\t",n

        if (n in memory) and n == gb.features[i].name:
            sys.stderr.write("%s rename %s %s\n" %
                             (gb.accession, n, rename[n].keys()[0]))
            gb.features[i].name = rename[n].keys()[0]

    return gb


def correct_signs(gb, arwen, trnascan, threshold):
    for i in range(len(gb.features)):
        maxa = threshold
        maxaf = None

        maxt = threshold
        maxtf = None

        if not gb.features[i].name in trna:
            continue

        for af in arwen.features:
            o = af.overlap(gb.features[i], gb.circular, gb.size)
            if o >= maxa:
                if o > maxa:
                    maxa = o
                maxaf = af

        for tf in trnascan.features:
            o = tf.overlap(gb.features[i], gb.circular, gb.size)
            if o >= maxt:
                if o > maxt:
                    maxt = o
                maxtf = tf

        if (maxaf == None and maxtf != None and maxtf.name == gb.features[i].name):
            if gb.features[i].strand != maxtf.strand:
                sys.stderr.write("%s correct strand %s %d -> %d\n" %
                                 (gb.accession, gb.features[i].name, gb.features[i].strand, maxtf.strand))
                gb.features[i].strand = maxtf.strand
        elif (maxtf == None and maxaf != None and maxaf.name == gb.features[i].name):
            if gb.features[i].strand != maxaf.strand:
                sys.stderr.write("%s correct strand %s %d -> %d\n" %
                                 (gb.accession, gb.features[i].name, gb.features[i].strand, maxaf.strand))
                gb.features[i].strand = maxaf.strand
        elif (maxaf != None and maxtf != None and maxaf.name == gb.features[i].name and maxtf.name == gb.features[i].name):
            if gb.features[i].strand != maxaf.strand and maxaf.strand == maxtf.strand:
                sys.stderr.write("%s correct strand %s %d -> %d\n" %
                                 (gb.accession, gb.features[i].name, gb.features[i].strand, maxaf.strand))
                gb.features[i].strand = maxaf.strand

    return gb

# contruct data and gene orders


def unique(lst):

    i = 0

    while i < len(lst):
        if lst[i] == lst[(i + 1) % len(lst)]:
            del lst[i]
        else:
            i += 1

    return lst


for arg in files:
    if arg.endswith(".bed"):
        gb = bedfromfile(arg)

    else:
        gb = gbfromfile(arg)


#    sys.stderr.write( "%s\n" % arg )

    if not gb.is_allowed(options.atax, options.ftax):
        continue

#    sys.stderr.write("%s\n"%gb.accession)

    if options.max:
        gb.dellowscoreparts()

#    for a in arwen.features:
#        print "as", a
#    for t in trnascan.features:
#        print "ts", t
#    for g in gb.features:
#        if g.type != "tRNA":
#            continue
#        print "gb",g

# TODO    if options.improve:
#         get arwen and trnascan results from db
#        if( exists( "/tmp/%s.arw"%gb.accession ) ):
#            f = open("/tmp/%s.arw"%gb.accession, "r")
#            arwen = pickle.load(f)
#            f.close()
#        else:
        # # TODO arwen = arwenfromdb( gb.accession )
#            f = open("/tmp/%s.arw"%gb.accession, "w")
#            pickle.dump(arwen, f)
#            f.close
#        if( exists( "/tmp/%s.tsc"%gb.accession ) ):
#            f = open("/tmp/%s.tsc"%gb.accession, "r")
#            trnascan = pickle.load(f)
#            f.close()
#        else:
        # # TODO trnascan = trnascanfromdb( gb.accession )
#            f = open("/tmp/%s.tsc"%gb.accession, "w")
#            pickle.dump(trnascan, f)
#            f.close

        # delete trnas that
        # - dont have a standard name, or
        # - overlap by more then 50% with proteins and rRNA
        arwen = deltrnafeat_ovlprotrrna(gb, arwen, 0.5)
        trnascan = deltrnafeat_ovlprotrrna(gb, trnascan, 0.5)

        gb = correct_names(gb, arwen, trnascan, 70.0)

        # for trnas which do not occur
        # - if there are trnascan and arwen predictions take the pair of predictions which overlap 90%
        #   (if more than one overlapping pair take none)
        # - if there is only a trnascan of arwen prediction, take it
        # for trnas which occur multiple times
        # - if all but one do not appear in trnascan / arwen -> delete not predicted
        gb = correct_multiplicity(gb, arwen, trnascan, 70.0)

        # 3. fix strand
        gb = correct_signs(gb, arwen, trnascan, 70.0)

    go = gb.geneorder(
        atypes=["gene", "rRNA", "tRNA", "rep_origin"], fnames=options.ignore)

    if options.mad == True:
        go = unique(go)

#    cnt = {}
#    for i in genes:
#        cnt[i] = 0

    cnterr = False
    for g in go:
        if g[0] == '-':
            x = g[1:]
        else:
            x = g

        if not x in genes:
            sys.stderr.write("%s unknown %s\n" % (gb.accession, x))
            cnterr = True
#        else:
#            try:
#                cnt[x] += 1
#            except:
#                cnt[x] = 1

#    for g in cnt:
#        if cnt[g] != 1:
#            sys.stderr.write( "%s wrong multiplicity %s %d\n" % ( gb.accession, g, cnt[g] ) )

    for g in genes:
        if go.count(g) + go.count("-" + g) != 1:
            sys.stderr.write("%s %d x %s\n" %
                             (gb.accession, go.count(g) + go.count("-" + g), g))
            cnterr = True

    if not options.ignoreall and cnterr:
        sys.stderr.write("%s\n" % (str(go)))
        continue

    out = options.format
    out = out.replace("%ap", gb.abspre(mito.prot))
    out = out.replace("%a", gb.accession)
    out = out.replace("%n", gb.name)
    out = out.replace("%taxid", str(gb.taxid))
    out = out.replace("%code", str(gb.transl_table))
    out = out.replace("%s", str(gb.size))
    out = out.replace("%g", " ".join(go))
    out = out.replace("%t", " ".join(gb.taxonomy))
    ohandle.write("%s\n" % out)

    # for r in gb.references:
    #    print r.authors, r.journal, r.title

# outfile and outdir given ?
if options.outfile != None:
    ohandle.close()
