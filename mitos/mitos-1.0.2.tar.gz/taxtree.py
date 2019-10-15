#!/usr/bin/venv python

'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).


@author: maze
'''
from __future__ import print_function
import os
import os.path
import logging

from gb import gbfromfile

import argparse
usage = "search for closest mitogenomes"
parser = argparse.ArgumentParser(description=usage)

parser.add_argument(
    "--gbdir", action="store", required=True, help="genbank directory")
parser.add_argument(
    "--names", action="store", required=True, help="names.dmp file to use")
parser.add_argument(
    "--nodes", action="store", required=True, help="nodes.dmp file to use")
parser.add_argument(
    "--merged", action="store", required=True, help="merged.dmp file to use")

args = parser.parse_args()


def count_nodes(sid, chld, taxidacc, ndcnt):

    gcnt = 0
    if sid in chld:
        cs = [count_nodes(x, chld, taxidacc, ndcnt) for x in chld[sid]]
        for i in range(len(cs) - 1, -1, -1):
            gcnt += cs[i]

    if sid in taxidacc:
        gcnt += len(taxidacc[sid])

    ndcnt[sid] = gcnt
    return gcnt


def print_nwk(sid, chld, taxidacc, ndcnt, nmsmap):

    if sid in chld:
        ac = len([x for x in chld[sid] if ndcnt[x] > 0])
    else:
        ac = 0

    nwk = []

    if sid in taxidacc:
        nwk += taxidacc[sid]
    if sid in chld:
        for i in range(len(chld[sid])):
            if ndcnt[chld[sid][i]] > 0:
                nwk.append(
                    print_nwk(chld[sid][i], chld, taxidacc, ndcnt, nmsmap))

    nwk = ",".join(nwk)
    if ac > 1:
        try:
            n = nmsmap[sid]
        except:
            n = ""
        return "(" + nwk + ")" + n
    else:
        return nwk

logging.info("reading names")

# read the taxid name mapping. the two dictionaries nmsmap and taxmap
# map from id to name (nmsmap) and vice versa (taxmap)
nmsmap = {}
taxmap = {}
nmsdmp = open(args.names)
for l in nmsdmp.readlines():
    l = l.split("|")
    l = [x.strip() for x in l]
    l[0] = int(l[0])
    if not l[0] in nmsmap:
        #        stderr.write("duplicate entry in names.dmp: \n\t%d %s\t%s\n" %(l[0], l[1],nmsmap[l[0]] ))
        #    else:
        nmsmap[l[0]] = l[1]

    taxmap[l[1]] = l[0]
nmsdmp.close()

logging.info("reading tree")
# read the taxonomic tree
chld = {}
prnt = {}

rankmap = {}
ndsdmp = open(args.nodes)
for l in ndsdmp.readlines():
    l = l.split("|")
    l = [x.strip() for x in l]
    l[0] = int(l[0])
    l[1] = int(l[1])

    if l[1] != l[0]:
        try:
            chld[l[1]].append(l[0])
        except:
            chld[l[1]] = [l[0]]
        prnt[l[0]] = l[1]
    elif l[0] != 1 or l[1] != 1:
        logging.error("cycle detected: \t%d \t%d" % (l[0], l[1]))

    if not l[0] in rankmap:
        rankmap[l[0]] = l[2]
    else:
        logging.error("duplicate rank in nodes.dmp: \n\t%d %s\t%s" %
                      (l[0], l[2], rankmap[l[0]]))
ndsdmp.close()


logging.info("reading merged")
mrgdmp = open(args.merged)
for l in mrgdmp.readlines():
    l = l.split("|")
    l = [x.strip() for x in l]
    old = int(l[0])
    new = int(l[1])

    if not new in prnt:
        print("missing merged new", new)
        continue

    p = prnt[new]

    if not old in chld[p]:
        chld[p].append(old)

    prnt[old] = prnt[new]
    rankmap[old] = rankmap[new]

mrgdmp.close()

# crawl the gbdirectory and store accession to taxid mappings
acctaxid = {}
taxidacc = {}
accgb = {}

logging.info("reading gb")

x = 0
for f in os.listdir(args.gbdir):
    if not os.path.isfile(args.gbdir + "/" + f):
        continue

    if not f.endswith(".gb"):
        continue

    gb = gbfromfile(args.gbdir + "/" + f)

    acctaxid[gb.accession] = gb.taxid

    try:
        taxidacc[gb.taxid].append(gb.accession)
    except:
        taxidacc[gb.taxid] = [gb.accession]

    accgb[gb.accession] = gb
    x += 1
#     if x > 100:
#         break

ndcnt = {}

p = count_nodes(1, chld, taxidacc, ndcnt)

logging.info("found {fnd} of {all}".format(fnd=p, all=len(taxidacc)))

nwk = print_nwk(1, chld, taxidacc, ndcnt, nmsmap)
print(nwk + ";")
