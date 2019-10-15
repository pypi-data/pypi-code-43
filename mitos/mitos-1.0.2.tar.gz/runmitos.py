#!/usr/bin/env python

'''
@author: M. Bernt

This is a confidential release. Do not redistribute without
permission of the author (bernt@informatik.uni-leipzig.de).
'''

import json
import logging
import os
import StringIO
import subprocess
import sys

from Bio import SeqIO
from Bio.Alphabet.IUPAC import ambiguous_dna
from Bio.SeqRecord import SeqRecord

from mitos import blast
from mitos import bedfile
from mitos import gfffile
from mitos.mergefeature import featureappend, appendlokalfeature, \
    checklokalfeature
from mitos import mitfi
from mitos import mito
from mitos.feature import genorderwriter
from mitos.mitofile import mitowriter
from mitos.rna.vienna import RNAplot
from mitos.sequence import fastawriter, sequence_info_fromfile, sequence_info_fromfilehandle
from mitos import tbl
from mitos import update

def mitos(fastafile, code, outdir=None, cutoff="%50", minevalue=2, finovl=35,
          maxovl=0.2, clipfac=10, fragovl=0.2, fragfac=10.0, ststrange=6,
          prot=True, trna=True, rrna=True, cr=False, refdir=None):
    """
    @param[in] cr predict control region based on blastn
    @param[in] refdir directory containing reference data
    """

    # The things that influence the results:
    if outdir is None:
        path = os.path.dirname(fastafile) + "/"
    else:
        path = outdir + "/"
    # The path where the mitfi results are safed
    mitfipath = "%smitfi-global/" % (path)

    if (trna == 1 or rrna == 1) and not os.path.exists(mitfipath):
        os.mkdir(mitfipath)

    fasta = sequence_info_fromfile(fastafile)
    # parse fasta header

    sequence = fasta[0]["sequence"]

    # create plot path
    if not os.path.exists("%s/plots/" % path):
        os.mkdir("%s/plots/" % path)

    # create empty (or reset) rna plot
    if rrna or trna:
        f = open("%s/plots/rna.dat" % (path), "w")
        f.close()

    acc = []
    for a in "_".join(fasta[0]["name"].split()):
        if a.isalnum() or a == "_" or a == "-":
            acc.append(a)
#        else:
#            acc.append( "_" )

    if len(acc) == 0:
        acc = "noname"
    else:
        acc = "".join(acc)

    if '|' in acc:
        raise Exception("No | character allowed in fasta header! Aborting")

    # run RNA models
    mitfi.cmsearch(fastafile, mitfipath, code, gl=True, trna=trna,
                   rrna=rrna, refdir=refdir)

    # read RNA results
    rnalist = mitfi.parse(mitfipath, False)

    protcrlist = []
    if prot:
        # Start Blast
        update.singleblastx(fastafile, code, path, refdir)
        if cr:
            update.singleblastn(fastafile, path, refdir)
        # Read Blast results
        protcrlist = blast.blastx("%sblast/" % (path), plot=True, cutoff=cutoff,
                                  minevalue=minevalue, acc=acc, code=code, fastafile=fastafile,
                                  maxovl=maxovl, clipfac=clipfac, fragovl=fragovl, fragfac=fragfac,
                                  ststrange=ststrange, cr=cr)

    protfeat = [x for x in protcrlist if (
        x.type == "gene" and (x.copy is None or x.copy == 0))]
    mprotfeat = [x for x in protcrlist if (
        x.type == "gene" and (x.copy is not None and x.copy != 0))]

    if trna:
        trnafeat = [x for x in rnalist if x.type == "tRNA" and x.mito == 2]
        mtrnafeat = [x for x in rnalist if x.type ==
                     "tRNA" and x.mito == 1 and x.evalue <= 0.001]
        print_for_plotting(
            trnafeat, mtrnafeat, "%s/plots/rna.dat" % (path), "global")
    else:
        trnafeat = []
        mtrnafeat = []

    if rrna:
        rrnafeat = [x for x in rnalist if x.type == "rRNA" and x.mito == 2]
        mrrnafeat = [x for x in rnalist if x.type == "rRNA" and x.mito == 1]
        print_for_plotting(
            rrnafeat, mrrnafeat, "%s/plots/rna.dat" % (path), "global")
    else:
        rrnafeat = []
        mrrnafeat = []

    if cr:
        crfeat = [x for x in protcrlist if (
            x.type == "rep_origin" and (x.copy is None or x.copy == 0))]
        mcrfeat = [x for x in protcrlist if (
            x.type == "rep_origin" and (x.copy is not None and x.copy != 0))]
    else:
        crfeat = []
        mcrfeat = []

#     print "PROT FEATURES CAND"
#     for f in sorted( protfeat, key = lambda x:x.start ):
#         print f.name, f.type, f.strand, f.start, f.stop
#     print "TRNA FEATURES CAND"
#     for f in sorted( trnafeat, key = lambda x:x.start ):
#         print f.name, f.strand, f.start, f.stop
#     print "RRNA FEATURES CAND"
#     for f in sorted( rrnafeat, key = lambda x:x.start ):
#         print f.name, f.strand, f.start, f.stop
#     print "CR FEATURES CAND"
#     for f in sorted( crfeat, key = lambda x:x.start ):
#         print f.name, f.strand, f.start, f.stop
# #
#     print "MFEATURES CAND"
#     for f in mprotfeat:
#         print f.name, f.strand, f.start, f.stop
#     for f in sorted( mtrnafeat, key = lambda x:x.start ):
#         print f.name, f.strand, f.start, f.stop
#     for f in sorted( mrrnafeat, key = lambda x:x.start ):
#         print f.name, f.strand, f.start, f.stop
#     for f in sorted( mcrfeat, key = lambda x:x.start ):
#         print f.name, f.strand, f.start, f.stop

    # set features: 1st round
    featurelist = protfeat
    featureappend(trnafeat, featurelist, overlap=finovl)
    featureappend(rrnafeat, featurelist, overlap=finovl, rnd=True)
    featureappend(crfeat, featurelist, overlap=finovl)

    logging.debug("State after first round")
    for f in featurelist:
        logging.debug("%s %d %d" % (f.name, f.start, f.stop))

    # try to get results from the local search if global did not yielded a
    # result
    localcheck = []  # stores for which rRNAs the local mode was applied
    if rrna > 0:
        # search both rRNA, of course
        for lname in ["rrnS", "rrnL"]:
            # check if the feature exists
            if len([feat for feat in featurelist if feat.name == lname]) == 0:
                logging.debug("adding local %s" % (lname))

                # save the info that this rRNA was searched also with local
                # mode
                localcheck.append(lname)

        # the path where the mitfi results are saved
        lokalpath = "%s/mitfi-local/" % (path)
        if not os.path.exists(lokalpath):
            os.mkdir(lokalpath)

        # search
        logging.debug("running mitfi for %s" % (str(localcheck)))
        mitfi.cmsearch(fastafile, lokalpath, code, gl=False,
                       rRNA=localcheck, rrna=True, trna=False, refdir=refdir)

        for lname in localcheck:
            # read results
            lokalHits = [
                x for x in mitfi.parse(lokalpath, True) if x.mito > 0 and x.name == lname]
            print_for_plotting(
                lokalHits, [], "%s/plots/rna.dat" % (path), "glocal")

            # append the local features
            appendlokalfeature(
                lokalHits, lname, rrnafeat, featurelist, len(sequence), allowoverlap=finovl)

    # for the remaining rRNAs, tRNAs, and proteins (which were not in the set of the best of each kind)
    # - determine the quotient of the best evalue and the evalue (or quality for proteins)
    # - sort by the quotient
    # - try to add
    for feat in mrrnafeat + mtrnafeat:
        besthit = [x for x in featurelist if x.name == feat.name]
        if len(besthit) == 0:
            maxevalue = 1
        else:
            besthit.sort(key=lambda x: (-x.mito, x.evalue))
            maxevalue = besthit[0].evalue
        if maxevalue == 0:
            maxevalue = 1E-46
        feat.evalfaktor = feat.evalue / maxevalue

    for feat in mprotfeat + mcrfeat:
        besthit = [x for x in featurelist if x.name == feat.name]
        if len(besthit) == 0:
            maxevalue = 1
        else:
            besthit.sort(key=lambda x: x.score)
            maxevalue = besthit[0].score
        if maxevalue == 0:
            maxevalue = 1E46
        feat.evalfaktor = 1 / (feat.score / maxevalue)

    dolist = mrrnafeat + mtrnafeat + mprotfeat + mcrfeat
    dolist.sort(key=lambda x: x.evalfaktor)

    featureappend(dolist, featurelist, overlap=finovl)

    # check if local features are too short / mergeable
    checklokalfeature(localcheck, featurelist, sequence, refdir)
    mitowriter(featurelist, acc, "%s/result" % (path))
    # produce protein plot

    if prot or cr:
        cmd = ["plotprot.R",
               "%s/blast/blast.dat" % (path),
               "%s/result" % (path),
               "%s/plots/prot.pdf" % (path),
               "%d" % (len(sequence))]
        logging.debug("executing %s" % " ".join(cmd))
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p.wait()
        if ret != 0:
            stdout, stderr = p.communicate()
            raise Exception("Rscript returned non zero \n%s\nstdout: %s\nstderr: %s\n" % (
                " ".join(cmd), str(stdout), str(stderr)))

    if trna or rrna:
        cmd = ["plotrna.R",
               "%s/plots/rna.dat" % (path),
               "%d" % (len(sequence)),
               "%s/plots/rna.pdf" % (path)]
        logging.debug("executing %s" % " ".join(cmd))
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p.wait()
        if ret != 0:
            stdout, stderr = p.communicate()
            raise Exception("Rscript returned non zero \n%s\nstdout: %s\nstderr: %s\n" % (
                " ".join(cmd), str(stdout), str(stderr)))

    # produce rRNA plots
    for f in featurelist:
        if f.type != "tRNA" and f.type != "rRNA":
            continue

        if not os.path.exists("%s/plots/" % path):
            os.mkdir("%s/plots/" % path)

#        print "seq", f.sequence
#        print "str", f.structure
        RNAplot(f.sequence, f.structure, "%s/plots/%s-%d-%d.ps" %
                (path, f.name, f.start, f.stop))
        RNAplot(f.sequence, f.structure, "%s/plots/%s-%d-%d.svg" %
                (path, f.name, f.start, f.stop), o="svg")

    return featurelist


def print_for_plotting(features, mfeatures, fname, mode):
    """
    print 1st and 2nd grade features to a file for plotting
    @param features 1st grade features
    @param mfeatures 2nd grade features
    @param mode mode
    @param fname file name
    """

    f = open(fname, "a")
    for feat in features:
        f.write("{start}\t{stop}\t{strand}\t{name}\t{type}\t{score}\t{mode}\t1\n".format(
            start=feat.start, stop=feat.stop, strand=feat.strand, name=feat.name,
            type=mito.types[feat.name], score=feat.score, mode=mode))
    for feat in mfeatures:
        f.write("{start}\t{stop}\t{strand}\t{name}\t{type}\t{score}\t{mode}\t2\n".format(
            start=feat.start, stop=feat.stop, strand=feat.strand, name=feat.name,
            type=mito.types[feat.name], score=feat.score, mode=mode))

    f.close()


def problems(prot, trna, rrna, cr, features):
    """
    determine lists of potential problems and peculiarities
    missing, duplicated/split genes
    @param prot consider protein
    @param trna consider tRNAs
    @param rrna consider rRNAs
    @param cr consider control region
    @return a triple containing the list of missing and duplicated/split
    """

    consider = []
    dup = []
    mis = []
    nst = []

    if prot:
        consider += mito.dprot
    if trna:
        consider += mito.dtrna
    if rrna:
        consider += mito.rrna
    if cr:
        consider += mito.rep_origin

    for c in consider:
        cf = [x for x in features if x.name == c]
        if len(cf) == 0:
            mis.append(c)
        elif len(cf) > 1:
            dup.append(c)

    for f in features:
        if f.name not in consider:
            nst.append(f.name)

    return (mis, dup, nst)


class _objectview(object):
    """
    little helper to be able to access a dictionary like an object
    """

    def __init__(self, d):
        self.__dict__ = d

if __name__ == '__main__':
    import argparse
    usage = "usage: %prog [options]"
    parser = argparse.ArgumentParser(usage)

    group = parser.add_argument_group("mandatory options")
    ingroup = parser.add_mutually_exclusive_group(required=True)
    ingroup.add_argument(
        "-i", '--input', dest="file", action="store", help="the input file")
    ingroup.add_argument(
        '--fasta', dest="fastacontent", action="store", help="input fasta sequence")
    group.add_argument("-c", '--code', dest="code", action="store",
                       required=True, type=int, help="the genetic code")
    group.add_argument("-o", '--outdir', dest="outdir", action="store", required=True,
                       help="the directory where the output is written (default: current working dir)")
    group.add_argument("-r", '--refdir', dest="refdir", action="store",
                       required=True, help="the directory where the reference data is found")

    group = parser.add_argument_group("advanced options")
    group.add_argument("--noprot", dest="prot", action="store_false",
                       default=True, help="skip protein prediction")
    group.add_argument("--notrna", dest="trna", action="store_false",
                       default=True, help="skip tRNA prediction")
    group.add_argument("--norrna", dest="rrna", action="store_false",
                       default=True, help="skip rRNA prediction")
    group.add_argument(
        "--cr", action="store_true", default=False, help="predict CR based on blastn")
    group.add_argument("--finovl", action="store", type=int,
                       metavar="NRNT", default=35, help="final overlap <= NRNT nucleotides ")

    group = parser.add_argument_group("protein prediction advanced options")
    group.add_argument("--evalue", dest="minevalue", action="store", type=float, metavar="EVL",
                       default=2, help="discard BLAST hits with -1*log(e-value)<EVL (EVL < 1 has no effect)")
    group.add_argument("--cutoff", action="store", type=int, metavar="PERCENT",
                       default=50, help="discard positions with quality <PERCENT%% below max")
    group.add_argument("--maxovl", action="store", type=float, metavar="FRACTION",
                       default=0.2, help="allow overlap up to a fraction of FRACTION ")
    group.add_argument("--clipfac", action="store", type=float, metavar="FACTOR", default=10,
                       help="overlapping features of the same name differing by at most a factor of FACTOR are clipped")
    group.add_argument("--fragovl", action="store", type=float, metavar="FRACTION",
                       default=0.2, help="allow query range overlaps up for FRACTION for fragments")
    group.add_argument("--fragfac", action="store", type=float, metavar="FACTOR",
                       default=10, help="allow fragments to differ in score by at most a factor FACTOR")
    group.add_argument("--ststrange", action="store", type=int, metavar="NRAA", default=6,
                       help="search the perimeter of start and stop positions by NRAA aminocids for better values")

    group = parser.add_argument_group("debug/misc options")
    group.add_argument(
        "--debug", action="store_true", default=False, help="print debug output")
    group.add_argument("--json", default=None,
                       help="a JSON file with parameters. then outdir is the only other argument needed.")

    args = parser.parse_args()

    if args.json is not None:

            # get commandline arg/default as dict
        dargs = {}
        for o in dir(args):
            if o.startswith("_"):
                continue
            dargs[o] = getattr(args, o)

        f = open(args.json)
        jargs = json.load(f)
        f.close()

        # overwrite default args with json file contents
        for a in jargs:
            dargs[a] = jargs[a]

        args = _objectview(dargs)

    if args.refdir is None:
        args.refdir = os.environ.get('MITOS_REFDIR', None)
    if args.refdir is None:
        parser.error("no reference data directory given")
    if not os.path.isdir(args.refdir):
        parser.error("no such directory %s" % args.refdir)

    if args.file is None and args.fastacontent is None:
        parser.error("no input file/fasta given")
    elif args.file is not None and args.fastacontent is not None:
        parser.error("both file and fasta given")

    if args.debug:
        logging.basicConfig(
            format="%(levelname)s - %(message)s", level=logging.DEBUG)
        logging.debug("debug on")

    # get sequences from file / fasta
    if args.file is not None:
        fname = args.file
        sequences = sequence_info_fromfile(fname)
    else:
        fh = StringIO(args.fastacontent)
        sequences = sequence_info_fromfilehandle(
            fh, alphabet=ambiguous_dna, circular=False)
        fh.close

        fname = "%s/sequence.fas" % args.outdir

        tmpf = open(fname, "w")
        sr = SeqRecord(seq=sequences[0]["sequence"], id=sequences[0]["id"],
                       name=sequences[0]["name"],
                       description=sequences[0]["description"])
        SeqIO.write(sr, tmpf, "fasta")
        tmpf.close()
    featurelist = mitos(fname, args.code, args.outdir,
                        cutoff="%%%d" % (args.cutoff),
                        minevalue=args.minevalue,
                        finovl=args.finovl, maxovl=args.maxovl,
                        clipfac=args.clipfac, fragovl=args.fragovl,
                        fragfac=args.fragfac, ststrange=args.ststrange,
                        prot=args.prot, trna=args.trna, rrna=args.rrna,
                        cr=args.cr, refdir=args.refdir)

    fh = open(fname, "r")
    acclist = fh.readline()[1:].split()
    fh.close()
    acc = acclist[0]
    bedfile.bedwriter(
        featurelist, acc, outfile="%s/result.bed" % (args.outdir))
    gfffile.gffwriter(featurelist, acc, outfile = "%s/result.gff" % (args.outdir), mode = "w")
    tbl.tblwriter(featurelist, acc, outfile="%s/result.seq" % (args.outdir))
    genorderwriter( featurelist, acc, "%s/result.geneorder" % (args.outdir))
    fastawriter( featurelist, sequences[0]["sequence"], None, acc, "fas", outfile = "%s/result.fas" % (args.outdir))
    fastawriter( featurelist, sequences[0]["sequence"], args.code, acc, "faa", outfile = "%s/result.faa" % (args.outdir))

    mis, dup, nst = problems(
        args.prot, args.trna, args.rrna, args.cr, featurelist)
    if len(mis) > 0:
        sys.stdout.write("missing: {missing}\n".format(missing=" ".join(mis)))
    if len(dup) > 0:
        sys.stdout.write(
            "duplicated: {duplicated}\n".format(duplicated=" ".join(dup)))
    if len(nst) > 0:
        sys.stdout.write("non standard: {nst}\n".format(nst=" ".join(nst)))
