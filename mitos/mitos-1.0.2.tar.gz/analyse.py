'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

compare the features given in two files (gb or bed). 
for each feature f1 from file1 the feature f2 from file2 is searched which 
interects most and f1 is covered more than the given cutoff. 
coverage is computed as the size of the intersection / the length of the feature. 

the output is: 
accession, f1.name, f2.name, standdiff, f1.cover, f2.cover, f1.score, f2.score, dstart, dend, fs

where: 
stranddiff: is +1 for same strand, -1 different strand  
fX.cover: intersection/fX.length

dstart|dend f1start-f2start , resp. end
fs 1 if frameshift for proteins NA otherwise

if perfeature is NOT set then each gene family is treated as a whole.  
an additional column is added to the output giving the difference of the number of 
members of the gene family in file1 and file2. 
  

@author: maze
'''

from __future__ import print_function
from optparse import OptionParser, OptionGroup
from os.path import splitext, basename
from sys import exit, stderr

from mitos.gb import gbfromfile
from mitos.bedfile import bedfromfile


def featurelist2map(list):
    """
    create a dictionary for a list of features
    for each name one name one entry is created in the map containing 
    1. pos : the position of the features with the name
    2. sgn : a sorted list of signs of the features with the name
    3. cnt : the number of features with the name
    3. scr : the sum of the scores of features with the name

    @param[in] list a list of features 
    """

    map = {}
    for f in list:
        if not f.name in map:
            map[f.name] = {}
            map[f.name]["pos"] = set()
            map[f.name]["sgn"] = None
            map[f.name]["cnt"] = 0
            map[f.name]["scr"] = 0
            map[f.name]["start"] = 100000000
            map[f.name]["stop"] = -1
            map[f.name]["type"] = ""

        if f.strand > 0:
            map[f.name]["start"] = min(f.start, map[f.name]["start"])
            map[f.name]["stop"] = max(f.stop, map[f.name]["stop"])
        else:
            map[f.name]["start"] = min(f.start, map[f.name]["stop"])
            map[f.name]["stop"] = max(f.stop, map[f.name]["start"])

        map[f.name]["pos"] = map[f.name]["pos"].union(
            set(range(f.start, f.stop + 1)))
        if map[f.name]["sgn"] == None or map[f.name]["sgn"] == f.strand:
            map[f.name]["sgn"] = f.strand
        else:
            f.strand = 0
        map[f.name]["cnt"] += 1
        if f.score == None:
            map[f.name]["scr"] += 0
        else:
            map[f.name]["scr"] += f.score * (f.stop - f.start + 1)
        map[f.name]["type"] = f.type

#    for i in map.keys():
#        map[i]["sgn"].sort()

    return map

usage = "usage: %prog [options] FILES"
parser = OptionParser(usage)

parser.add_option("--perfeature", action="store_true", default=False,
                  help="analyse each feature separately; default: analyse featuresets with the same name")

parser.add_option("--cutoff", action="store", default=0, type="float",
                  help="festure intersection cutoff; default: 0")

# parser.add_option( "-T", dest = "ftax", action = "append", type = "string", metavar = "TAX", help = "forbid all entries with TAX in the taxonomy" )
# parser.add_option( "-f", dest = "format", action = "store", type = "string", default = ">%a\n%g", metavar = "FORMAT", help = "output format: %n=name, %a=accession, %g=gene order" )
# parser.add_option( "--improve", action = "store_true", default = False, help = "improve with arwen and tRNAscan from database" )
# parser.add_option( "--ignore", action = "append", type = "string", metavar = "NAME", help = "ignore genes with name NAME" )
# parser.add_option( "--notrna", action = "store_true", default = False, help = "ignore tRNAs" )
group = OptionGroup(parser, "parameters to specify a subset of the features",
                    "type can be tRNA, rRNA, and gene"
                    "Note: -y,-Y,-n,-N can be specified more than once, combinations are possible.")
group.add_option("-y", "--atype", action="append", type="string",
                 metavar="TYPE", help="get all features of type TYPE")
group.add_option("-Y", "--ftype", action="append", type="string",
                 metavar="TYPE", help="get all features except features of type TYPE")

group.add_option("-n", "--aname", action="append", type="string",
                 metavar="NAME", help="get all features with name NAME")
group.add_option("-N", "--fname", action="append", type="string",
                 metavar="NAME", help="get all features except features with name NAME")
parser.add_option_group(group)

(options, args) = parser.parse_args()

if len(args) != 2:
    stderr.write("error: analyse needs two input files. %d given" % len(args))
    exit()

size = 0
circular = False
ext = splitext(args[0])[1]
if ext == ".gb":
    g = gbfromfile(args[0])
    size = g.size
    circular = g.circular
elif ext == ".embl":
    g = gbfromfile(args[0])
    size = g.size
    circular = True
elif ext == ".bed":
    g = bedfromfile(args[0])

bname = g.name
feat1 = g.getfeatures(
    anames=options.aname, fnames=options.fname, atypes=options.atype, ftypes=options.ftype)

ext = splitext(args[1])[1]
if ext == ".gb":
    g2 = gbfromfile(args[1])
    size = g2.size
    circular = g2.circular
elif ext == ".embl":
    g2 = gbfromfile(args[1])
    size = g2.size
    circular = True
elif ext == ".bed":
    g2 = bedfromfile(args[1])
feat2 = g2.getfeatures(
    anames=options.aname, fnames=options.fname, atypes=options.atype, ftypes=options.ftype)


# for f in feat1:
#    print(f)
# print("----------")


# CODE FOR BIDIRECTIONAL TESTING
# feat1best = {}
# feat2best = {}
#
# if options.perfeature == False:
#    feat1map = featurelist2map( feat1 )
#    feat2map = featurelist2map( feat2 )
#    for i in feat1map.keys():
#        maxcap = 0
#        maxj = None
#        for j in feat2map.keys():
#            cap = len( feat1map[i]["pos"].intersection( feat2map[j]["pos"] ) )
# #            print(i, j, cap)
#            if cap > maxcap and ( cap / len( feat1map[i]["pos"] ) >= options.cutoff ):
#                maxcap = cap
#                maxj = j
#        if maxj != None:
#            feat1best[i] = {'idx':maxj, 'cap':maxcap}
#
#    for i in feat2map.keys():
#        maxcap = 0
#        maxj = None
#        for j in feat1map.keys():
#            cap = len( feat2map[i]["pos"].intersection( feat1map[j]["pos"] ) )
#            if cap > maxcap and ( cap / len( feat2map[i]["pos"] ) >= options.cutoff ):
#                maxcap = cap
#                maxj = j
#        if maxj != None:
#            feat2best[i] = {'idx':maxj, 'cap':maxcap}
#
#    for i in feat1map:
#        if i in feat1best and feat1best[i]['idx'] in feat2best and feat2best[ feat1best[i]['idx'] ]['idx'] == i:
#            # bidirectional best -> report match i, feat1best[i]
#            j = feat1best[i]['idx']
#
# #            if feat1map[i]["sgn"] == feat2map[j]["sgn"]:
# #                strand = 1
# #            else:
# #                strand = -1
#
#            # frameshift analysis only if genes
#            if feat1map[i]['type'] == "gene" and feat2map[j]['type'] == "gene" and feat1map[i]["sgn"] == feat2map[j]["sgn"] and \
#                ( ( feat1map[i]['start'] % 3 + 1 ) != ( feat2map[j]['start'] % 3 + 1 ) ):
#                fs = ( feat1map[i]['start'] % 3 + 1 ) - ( feat2map[j]['start'] % 3 + 1 )
#            else:
#                fs = "NA"
#
#            print(bname, i, j, feat1map[i]["sgn"], feat2map[j]["sgn"], \
#                feat1best[i]['cap'] / float( len( feat1map[i]["pos"] ) ), \
#                feat2best[j]['cap'] / float( len( feat2map[j]["pos"] ) ), \
#                feat1map[i]["scr"] / float( len( feat1map[i]["pos"] ) ), \
#                feat2map[j]["scr"] / float( len( feat2map[j]["pos"] ) ), \
#                feat1map[i]['start'] - feat2map[j]['start'], \
#                feat1map[i]['stop'] - feat2map[j]['stop'], \
#                fs, \
#                feat1map[i]['type'], feat2map[j]['type'], \
#                len( feat1map[i]["pos"] ), len( feat2map[j]["pos"] ), \
#                feat1map[i]['start'], feat2map[j]['start'], \
#                feat1map[i]['stop'], feat2map[j]['stop'], \
#                feat1map[i]["cnt"] - feat2map[j]["cnt"])
#
#        else:
#            # report i, NA
#            print(bname, i, "NA", feat1map[i]["sgn"], "NA", \
#                "NA", "NA", \
#                feat1map[i]["scr"] / float( len( feat1map[i]["pos"] ) ), "NA", \
#                "NA", "NA", "NA", \
#                feat1map[i]['type'], "NA", \
#                len( feat1map[i]["pos"] ), "NA", \
#                feat1map[i]['start'], "NA", \
#                feat1map[i]['stop'], "NA", \
#                "NA")
#
#    for j in feat2map:
#        if j in feat2best and feat2best[j]['idx'] in feat1best and feat1best[ feat2best[j]['idx'] ]['idx'] == j:
#            # bidirectional best (already reported)
#            pass
#        else:
#            print(bname, "NA", j, "NA", feat2map[j]["sgn"], \
#                "NA", "NA", \
#                "NA", feat2map[j]["scr"] / float( len( feat2map[j]["pos"] ) ), \
#                "NA", "NA", "NA", \
#                "NA", feat2map[j]['type'], \
#                "NA", len( feat2map[j]["pos"] ), \
#                "NA", feat2map[j]['start'], \
#                "NA", feat2map[j]['stop'], \
#                "NA")
#
#
# else:
#    for i in range( len( feat1 ) ):
#        maxcap = -1
#        maxidx = -1
#        f1length = float( feat1[i].length( circular = circular, size = size ) )
#        for j in range( len( feat2 ) ):
#            cap = feat1[i].capcup( feat2[j], circular = circular, size = size )[0]
#            if cap > maxcap and ( cap / f1length >= options.cutoff ):
#                maxcap = cap
#                maxidx = j
#
#        if maxidx != -1:
#            feat1best[i] = {'idx':maxidx, 'cap':maxcap}
# #            print(i, "->", maxidx)
#
#    for i in range( len( feat2 ) ):
#        maxcap = -1
#        maxidx = -1
#        f2length = float( feat2[i].length( circular = circular, size = size ) )
#        for j in range( len( feat1 ) ):
#            cap = feat2[i].capcup( feat1[j], circular = circular, size = size )[0]
# #            print(i, j, feat2[i].name, feat1[j].name, cap)
#            if cap > maxcap and ( cap / f2length >= options.cutoff ):
#                maxcap = cap
#                maxidx = j
#        if maxidx != -1:
#            feat2best[i] = {'idx':maxidx, 'cap':maxcap}
# #            print(i, "->", maxidx)
#
# #    print(feat1best)
# #    print(feat2best)
#
#    for i in range( len( feat1 ) ):
#        f1length = float( feat1[i].length( circular = circular, size = size ) )
#
#        if i in feat1best and feat1best[i]['idx'] in feat2best and feat2best[ feat1best[i]['idx'] ]['idx'] == i:
#            # bidirectional best -> report match i, feat1best[i]
#            j = feat1best[i]['idx']
#
#            f2length = float( feat2[j].length( circular = circular, size = size ) )
#
#            # dstart + -> feat1 inside feat2; - -> feat2 inside feat1
#            # dstop  + -> feat1 inside feat2; - -> feat2 inside feat1
#            f1start = feat1[i].start
#            f1stop = feat1[i].stop
#            f2start = feat2[j].start
#            f2stop = feat2[j].stop
#            if feat1[i].strand == -1:
#                f1start, f1stop = f1stop, f1start
#            if feat2[j].strand == -1:
#                f2start, f2stop = f2stop, f2start
#
#            if feat1[i].name == feat2[j].name and feat1[i].strand == feat2[j].strand:
#                dstart = f1start - f2start
#                dstop = f2stop - f1stop
#                # for the inverse strand it must be reversed -> then + means feat1 in feat2
#                if feat1[i].strand == -1:
#                    dstart *= -1
#                    dstop *= -1
#            else:
#                dstart = "NA"
#                dstop = "NA"
#
#            # frameshift analysis only if genes
#            if feat1[i].type == "gene" and feat2[j].type == "gene" and feat1[i].strand == feat2[j].strand and\
#                ( ( f1start % 3 + 1 ) != ( f2start % 3 + 1 ) ):
#                fs = ( f1start % 3 + 1 ) - ( f2start % 3 + 1 )
#            else:
#                fs = "NA"
#
#            print(bname, feat1[i].name, feat2[j].name, \
#                feat1[i].strand, feat2[j].strand, \
#                feat1best[i]['cap'] / float( f1length ), \
#                feat2best[j]['cap'] / float( f2length ), \
#                feat1[i].score, feat2[j].score, \
#                dstart, dstop, \
#                fs, feat1[i].type, feat2[j].type, \
#                f1length, f2length, \
#                f1start, f2start, f1stop, f2stop)
#        else:
#            print(bname, feat1[i].name, "NA", \
#                feat1[i].strand, "NA", \
#                "NA", \
#                "NA", \
#                feat1[i].score, "NA", \
#                "NA", "NA", \
#                "NA", feat1[i].type, "NA", \
#                f1length, "NA", \
#                feat1[i].start, "NA", feat1[i].stop, "NA")
#
#    for j in range( len( feat2 ) ):
#        f2length = float( feat2[j].length( circular = circular, size = size ) )
#        if j in feat2best and feat2best[j]['idx'] in feat1best and feat1best[ feat2best[j]['idx'] ]['idx'] == j:
#            # bidirectional best (already reported)
#            pass
#        else:
#            print(bname, "NA", feat2[j].name, \
#                "NA", "NA", \
#                "NA", \
#                "NA", \
#                "NA", feat2[j].score, \
#                "NA", "NA", \
#                "NA", "NA", feat2[j].type, \
#                "NA", f2length, \
#                "NA", feat2[j].start, "NA", feat2[j].stop)
#
#
#
#
# exit()

feat2hits = {}

if options.perfeature == False:
    feat1map = featurelist2map(feat1)
    feat2map = featurelist2map(feat2)
    for i in feat1map.keys():
        maxcap = -1
        maxj = "XXX"
        for j in feat2map.keys():
            cap = len(feat1map[i]["pos"].intersection(feat2map[j]["pos"]))
            if cap > maxcap:
                maxcap = cap
                maxj = j

        if (maxcap / float(len(feat1map[i]["pos"]))) > options.cutoff:
            try:
                feat2hits[maxj] += 1
            except:
                feat2hits[maxj] = 1

            if feat1map[i]["sgn"] == feat2map[maxj]["sgn"]:
                strand = 1
            else:
                strand = -1

            print(bname, i, maxj, strand,
                  maxcap / float(len(feat1map[i]["pos"])),
                  maxcap / float(len(feat2map[maxj]["pos"])),
                  feat1map[i]["scr"] / float(len(feat1map[i]["pos"])),
                  feat2map[maxj]["scr"] / float(len(feat2map[maxj]["pos"])),
                  feat1map[i]["cnt"] - feat2map[maxj]["cnt"])
        else:
            print(bname, i, "None", 0, 0, 0, feat1map[i]["scr"] / float(len(feat1map[i]["pos"])), 0)

    for j in feat2map.keys():
        if not j in feat2hits:
            print(bname, "None", j, 0, 0, 0, None, 0)

else:
    for i in range(len(feat1)):
        #        print feat1[i]
        maxcap = -1
        maxidx = -1
        f1length = float(feat1[i].length(circular=circular, size=size))
        f1start = feat1[i].start
        f1stop = feat1[i].stop
        if feat1[i].strand == -1:
            f1start, f1stop = f1stop, f1start

        for j in range(len(feat2)):
            cap, cup = feat1[i].capcup(feat2[j], circular=circular, size=size)
            if cap > maxcap:
                maxcap = cap
                maxidx = j

        # if the overlap is over the min cutoff -> report it
        # otherwith report the current element of feat1 as uncovered
        if (maxcap / f1length) > options.cutoff:
            try:
                feat2hits[maxidx] += 1
            except:
                feat2hits[maxidx] = 1

            f2start = feat2[maxidx].start
            f2stop = feat2[maxidx].stop
            if feat2[maxidx].strand == -1:
                f2start, f2stop = f2stop, f2start

            if feat1[i].name == feat2[maxidx].name and feat1[i].strand == feat2[maxidx].strand:
                dstart = f1start - f2start
                dstop = f2stop - f1stop
                # for the inverse strand it must be reversed -> then + means
                # feat1 in feat2
                if feat1[i].strand == -1:
                    dstart *= -1
                    dstop *= -1
            else:
                dstart = "NA"
                dstop = "NA"

            # frameshift analysis only if genes
            if feat1[i].type == "gene" and feat2[maxidx].type == "gene" and feat1[i].strand == feat2[maxidx].strand and\
                    ((f1start % 3 + 1) != (f2start % 3 + 1)):
                fs = (f1start % 3 + 1) - (f2start % 3 + 1)
            else:
                fs = "NA"

            print(bname, feat1[i].name, feat2[maxidx].name, \
                feat1[i].strand, feat2[maxidx].strand, \
                maxcap / float( f1length ), \
                maxcap / float( float( feat2[maxidx].length( circular=circular, size=size ) ) ), \
                feat1[i].score, feat2[maxidx].score, \
                dstart, dstop, \
                fs, feat1[i].type, feat2[maxidx].type, \
                f1length, float( feat2[maxidx].length( circular=circular, size=size ) ), \
                f1start, f2start, f1stop, f2stop)

        else:
            print(bname, feat1[i].name, "NA", \
                feat1[i].strand, "NA", \
                "NA", "NA", \
                feat1[i].score, "NA", \
                "NA", "NA", "NA", feat1[i].type, "NA", f1length, "NA", \
                f1start, "NA", f1stop, "NA")

    # print the elements from feat2 which have no 'partner' in feat1
    for j in range(len(feat2)):
        if not j in feat2hits:
            f2start = feat2[j].start
            f2stop = feat2[j].stop
            if feat2[j].strand == -1:
                f2start, f2stop = f2stop, f2start

            print(bname, "NA", feat2[j].name, \
                "NA", feat2[j].strand, \
                "NA", "NA", \
                "NA", feat2[j].score, \
                "NA", "NA", "NA", "NA", feat2[j].type, "NA", \
                float( feat2[j].length( circular=circular, size=size ) ), \
                "NA", f2start, "NA", f2stop)

# for i in range( len( feat1 ) ):
#    print(feat1[i])
# print("")
# for i in range( len( feat2 ) ):
#    print feat2[i]
