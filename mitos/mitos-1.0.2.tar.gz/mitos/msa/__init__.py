'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from __future__ import print_function
import os
import re
import subprocess
import sys
from tempfile import mktemp

from Bio import Data

from .. import extprog


class msa:
    """
    class for a multiple sequence alignment
    """

    def __init__(self):
        """
        msa the sequence alignment
        len the length of the sequences
        cnt the number of sequences
        """
        self.msa = {}
        self.len = 0
        self.cnt = 0

    def consensus(self):
        """
        get consensus sequence from a msa
        """
        consensus = ""

        sequences = self.msa.values()

        freq = []
        for i in range(self.len):
            freq.append({})

        for m in msa:
            for i in range(self.cnt):
                if not m[i] in freq[i]:
                    freq[i][m[i]] = 0
                freq[i][m[i]] += 1

        consensus = []
        for f in freq:
            flist = f.items()
            flist.sort(lambda x, y: cmp(x[1], y[1]))

            if float(flist[-1][1]) / float(len(msa)) > 0.66:
                consensus.append(flist[-1][0].upper())
            else:
                consensus.append(flist[-1][0].lower())

        return "".join(consensus)

    def init_cnts(self):
        """
        initialise the cnt and len variables
        """
        self.cnt = len(self.msa)
        self.len = len(self.msa.values()[0])

        for m in self.msa:
            if self.len != len(self.msa[m]):
                sys.stderr.write("error: sequences of different length found in msa %d != %d" % (
                    self.len, len(self.msa[m])))
                sys.exit()

    def load_clustal(self, infile):
        """
        parse a clustal formated file
        \param infile input file name
        """

        # reset
        self.msa = {}
        self.cnt = 0
        self.len = 0

        eol = re.compile("[\n\r]+")
        blockmsa = {}
        # open file
        f = open(infile, "r")
        clu = eol.split(f.read())
        f.close()

        version = ""
        for c in clu:
            # print c
            m = re.match("^(\\S+)\\s+([%s.-]+)$" %
                         Data.IUPACData.ambiguous_dna_letters, c)
            if m != None:
                # print "|%s|%s|" %(m.group(1), m.group(2))
                if not m.group(1) in self.msa:
                    self.msa[m.group(1)] = ""
                if m.group(1) in blockmsa:
                    print("warning: ignoring duplicate %s " % (m.group(1)))
                    if m.group(2) == blockmsa[m.group(1)]:
                        comp = "=="
                    else:
                        comp = "!="
                    print("   %s %s %s" %
                          (m.group(2), comp, blockmsa[m.group(1)]))
                    continue
                blockmsa[m.group(1)] = m.group(2)
                self.msa[m.group(1)] += m.group(2)
            else:
                blockmsa.clear()

        self.init_cnts()

        return

    def remove(self, loki):
        """
        remove some rows from the msa
        \param loki in Norse  mythology, the god of evil and destruction; but here a list of row names to delete
        """
        msa = {}
        for m in self.msa:
            if m in loki:
                continue
            msa[m] = self.msa[m]

        self.msa = msa

    def __str__(self):
        s = ""
        for m in self.msa:
            s += "%s %s\n" % (m, self.msa[m])
        return s

    def write_clustal(self, fname, offset=60):
        """
        write the msa in the clustal format to a file
        \param fname the filename; if empty -> stdout
        \param offset chunk size (clustal format splits the lines in chunks)
        """

        if fname != "":
            f = open(fname, "w")
        else:
            f = sys.stdout

        keys = self.msa.keys()
        maxlen = 0
        for k in keys:
            if len(k) > maxlen:
                maxlen = len(k)

        i = 0
        f.write("CLUSTAL W (1.83) multiple sequence alignment\n\n")
        while i * offset < self.len:
            #            f.write("%s " %(" "*maxlen))
            #            for p in xrange(i*offset,(i+1)*offset):
            #                f.write("%d" %(p/10))
            #            f.write("\n%s " %(" "*maxlen))
            #            for p in xrange(i*offset,(i+1)*offset):
            #                f.write("%d" %(p%10))
            #            f.write("\n")

            for m in self.msa:
                mm = m.replace(" ", "_")
                f.write("%s%s %s\n" % (
                    mm, " " * (maxlen - len(m)), self.msa[m][i * offset:(i + 1) * offset]))
            i += 1
            f.write("\n")
        if fname != "":
            f.close()
        return


class MSAError(Exception):

    def __init__(self, prog, msg):
        self.prog = prog
        self.msg = msg

    def __str__(self):
        return "%s returned an error:\n %s" % (str(self.prog), str(self.msg))


class clustalparm(extprog.parm):

    def __init__(self, name, type, range=[]):
        extprog.parm.__init__(self, name, type, range)
        self.infix = "="
        self.prefix = "-"


def clustalw(alnf=None, dndf=None, sequences=None, **keywords):
    """
    call clustalw; creates a aln and dnd file in the working directory
    \param alnf if None the alnfile is deleted, else renames to the given file name
    \param dndf if None the dndfile is deleted, else renamed to the given file name
                DATA (sequences)
    -INFILE=file.ext                             :input sequences.
    -PROFILE1=file.ext  and  -PROFILE2=file.ext  :profiles (old alignment).
                    VERBS (do things)
    -OPTIONS            :list the command line parameters
    -HELP  or -CHECK    :outline the command line params.
    -ALIGN              :do full multiple alignment 
    -tree               :calculate NJ tree.
    -BOOTSTRAP(=n)      :bootstrap a NJ tree (n= number of bootstraps; def. = 1000).
    -CONVERT            :output the input sequences in a different file format.
                    PARAMETERS (set things)
    ***General settings:****
    -INTERACTIVE :read command line, then enter normal interactive menus
    -QUICKTREE   :use FAST algorithm for the alignment guide tree
    -TYPE=       :PROTEIN or DNA sequences
    -NEGATIVE    :protein alignment with negative values in matrix
    -OUTFILE=    :sequence alignment file name
    -OUTPUT=     :GCG, GDE, PHYLIP, PIR or NEXUS
    -OUTORDER=   :INPUT or ALIGNED
    -CASE        :LOWER or UPPER (for GDE output only)
    -SEQNOS=     :OFF or ON (for Clustal output only)
    -SEQNO_RANGE=:OFF or ON (NEW: for all output formats) 
    -RANGE=m,n   :sequence range to write starting m to m+n. 
    ***Fast Pairwise Alignments:***
    -KTUPLE=n    :word size
    -TOPDIAGS=n  :number of best diags.
    -WINDOW=n    :window around best diags.
    -PAIRGAP=n   :gap penalty
    -SCORE       :PERCENT or ABSOLUTE
    ***Slow Pairwise Alignments:***
    -PWMATRIX=    :Protein weight matrix=BLOSUM, PAM, GONNET, ID or filename
    -PWDNAMATRIX= :DNA weight matrix=IUB, CLUSTALW or filename
    -PWGAPOPEN=f  :gap opening penalty        
    -PWGAPEXT=f   :gap opening penalty
    ***Multiple Alignments:***
    -NEWTREE=      :file for new guide tree
    -USETREE=      :file for old guide tree
    -MATRIX=       :Protein weight matrix=BLOSUM, PAM, GONNET, ID or filename
    -DNAMATRIX=    :DNA weight matrix=IUB, CLUSTALW or filename
    -GAPOPEN=f     :gap opening penalty        
    -GAPEXT=f      :gap extension penalty
    -ENDGAPS       :no end gap separation pen. 
    -GAPDIST=n     :gap separation pen. range
    -NOPGAP        :residue-specific gaps off  
    -NOHGAP        :hydrophilic gaps off
    -HGAPRESIDUES= :list hydrophilic res.    
    -MAXDIV=n      :% ident. for delay
    -TYPE=         :PROTEIN or DNA
    -TRANSWEIGHT=f :transitions weighting
    ***Profile Alignments:***
    -PROFILE      :Merge two alignments by profile alignment
    -NEWTREE1=    :file for new guide tree for profile1
    -NEWTREE2=    :file for new guide tree for profile2
    -USETREE1=    :file for old guide tree for profile1
    -USETREE2=    :file for old guide tree for profile2
    ***Sequence to Profile Alignments:***
    -SEQUENCES   :Sequentially add profile2 sequences to profile1 alignment
    -NEWTREE=    :file for new guide tree
    -USETREE=    :file for old guide tree
    ***Structure Alignments:***
    -NOSECSTR1     :do not use secondary structure-gap penalty mask for profile 1 
    -NOSECSTR2     :do not use secondary structure-gap penalty mask for profile 2
    -SECSTROUT=STRUCTURE or MASK or BOTH or NONE   :output in alignment file
    -HELIXGAP=n    :gap penalty for helix core residues 
    -STRANDGAP=n   :gap penalty for strand core residues
    -LOOPGAP=n     :gap penalty for loop regions
    -TERMINALGAP=n :gap penalty for structure termini
    -HELIXENDIN=n  :number of residues inside helix to be treated as terminal
    -HELIXENDOUT=n :number of residues outside helix to be treated as terminal
    -STRANDENDIN=n :number of residues inside strand to be treated as terminal
    -STRANDENDOUT=n:number of residues outside strand to be treated as terminal 
    ***Trees:***
    -OUTPUTTREE=nj OR phylip OR dist OR nexus
    -SEED=n        :seed number for bootstraps.
    -KIMURA        :use Kimura's correction.   
    -TOSSGAPS      :ignore positions with gaps.
    -BOOTLABELS=node OR branch :position of bootstrap values in tree display
    """

    pars = [clustalparm('INFILE', 'file'), clustalparm('PROFILE1', 'file'), clustalparm('PROFILE2', 'file'),
            clustalparm('ALIGN', 'flag'), clustalparm('tree', 'flag'), clustalparm(
                'BOOTSTRAP', 'int'), clustalparm('CONVERT', 'flag'),

            clustalparm('QUICKTREE', 'flag'), clustalparm(
                'TYPE', 'string', ['DNA', 'PROTEIN']),
            clustalparm('OUTFILE', 'string'), clustalparm(
                'OUTPUT', 'string', ['GCG', 'GDE', 'PHYLIP', 'PIR', 'NEXUS']),
            clustalparm('OUTORDER', 'string', ['INPUT', 'ALIGNED']), clustalparm(
                'CASE', 'string', ['UPPER', 'LOWER']),
            clustalparm('SEQNOS', 'string', ['ON', 'OFF']), clustalparm(
                'SEQNO_RANGE', 'string', ['ON', 'OFF']),
            clustalparm('RANGE', 'string'),

            clustalparm('KTUPLE', 'int'), clustalparm(
                'TOPDIAGS', 'int'), clustalparm('WINDOW', 'int'),
            clustalparm('PAIRGAP', 'int'), clustalparm(
                'SCORE', 'string', ['PERCENT', 'ABSOLUTE']),

            clustalparm('PWMATRIX', 'string'), clustalparm(
                'PWDNAMATRIX', 'string'), clustalparm('PWGAPOPEN', 'float'),
            clustalparm('PWGAPEXT', 'float'),

            clustalparm('NEWTREE', 'str'), clustalparm(
                'USETREE', 'str'), clustalparm('MATRIX', 'str'),
            clustalparm('DNAMATRIX', 'str'), clustalparm(
                'GAPOPEN', 'float'), clustalparm('GAPEXT', 'float'),
            clustalparm('ENDGAPS', 'flag'), clustalparm(
                'GAPDIST', 'int'), clustalparm('NOPGAP', 'flag'),
            clustalparm('NOHGAP', 'flag'), clustalparm(
                'HGAPRESIDUES', 'str'), clustalparm('MAXDIV', 'int', (0, 100)),
            clustalparm('TRANSWEIGHT', 'float'),

            clustalparm('PROFILE', 'flag'), clustalparm(
                'NEWTREE1', 'str'), clustalparm('NEWTREE2', 'str'),
            clustalparm('USETREE1', 'str'), clustalparm('USETREE2', 'str'),

            clustalparm('SEQUENCES', 'flag'), clustalparm(
                'NEWTREE', 'str'), clustalparm('USETREE', 'str'),

            clustalparm('NOSECSTR1', 'flag'), clustalparm('NOSECSTR2', 'flag'), clustalparm(
                'SECSTROUT', 'str', ['STRUCTURE', 'MASK', 'BOTH', 'NONE']),
            clustalparm('HELIXGAP', 'int'), clustalparm(
                'STRANDGAP', 'int'), clustalparm('LOOPGAP', 'int'),
            clustalparm('TERMINALGAP', 'int'), clustalparm(
                'HELIXENDIN', 'int'), clustalparm('HELIXENDOUT', 'int'),
            clustalparm('STRANDENDIN', 'int'), clustalparm('STRANDENDOUT', 'int'), clustalparm(
                'OUTPUTTREE', 'str', ['nj', 'phylip', 'nexus']),
            clustalparm('SEED', 'int'), clustalparm('KIMURA', 'flag'), clustalparm('TOSSGAPS', 'flag'), clustalparm('BOOTLABELS', 'str', ['node', 'branch'])]

    fname = ""
    if keywords.get("INFILE") == None:
        if sequences == None:
            sys.stderr.write(
                "error: clustalw: no sequences or INFILE given\n ")
            sys.exit()
        fname = mktemp()
        keywords["INFILE"] = fname
        f = open(fname, "w")

        for i in xrange(len(sequences)):
            f.write(">%d\n%s\n" % (i, str(sequences[i])))
        f.close()

        # f = open(fname)
        # for l in f.readlines():
        #    print l
        # f.close()

    cl = extprog.cmdline(keywords, pars)
    pars = str(cl)

    dndfname = ""
    alnfname = ""
    p = subprocess.Popen("clustalw %s" % pars, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    err = ""
    for l in p.stdout.readlines():
        # print l.strip()
        m = re.match("^\\S+ tree\\s+file created:\\s+\[(\\S+)]\\s+$", l)
        if m != None:
            #            print "match"
            dndfname = m.group(1)
            continue

        m = re.match("^CLUSTAL-Alignment file created\\s+\[(.*)\]\\s*$", l)
        if m != None:
            alnfname = m.group(1)
            continue

        if l.startswith("ERROR"):
            err += l
            continue

    p.wait()

    if fname != "":
        os.remove(fname)
    # parse stdout: looking for ERROR lines and the one giving the name of the dnd file
#        print "clustal stdout: ", l.strip()

    err += p.stderr.read()
    if err != "":
        raise MSAError("clustalw", err)

    # delete the dnd file
    if dndfname != "" and os.path.exists(dndfname):
        if dndf == None:
            os.remove(dndfname)
        else:
            os.rename(dndfname, str(dndf))
    elif dndf != None:
        print("warning: clustalw did not produced a dnd file")

        # read the aln fname
    if alnfname != "" and os.path.exists(alnfname):
        aln = msa()
        aln.load_clustal(alnfname)

        if dndf == None:
            os.remove(alnfname)
        else:
            os.rename(alnfname, str(alnf))
    else:
        sys.stderr.write("error: clustalw did not produced a aln file\n")
        sys.exit()

    return aln


def t_coffee(dndf=False, htmlf=None, **keywords):
    """
    run tcoffee
    \param dndf if None the dndfile is deleted, else renamed to the given file name
    \param htmlf the same as for dndf, but with the html file produced per default
    supported parameters 
    in 
    seq specify sequence input
    outfile
    output:  csv of 'clustalw_aln', 'clustalw', 'gcg', 'msf_aln', 'pir_aln', 'fasta_aln', 'phylip', 'pir_seq', 'fasta_seq', 'score_ascii', 'score_html', 'score_pdf', 'score_ps'
    """

    pars = [clustalparm('in', 'str'), clustalparm('seq', 'str'), clustalparm(
        '-output', 'str'), clustalparm('outfile', 'str')]
    cl = extprog.cmdline(keywords, pars)
    pars = str(cl)

#    print "t-coffee parms ", pars
    p = subprocess.Popen("t_coffee %s" % pars, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    p.wait()

    err = ""
    htmlfname = ""
    dndfname = ""
    for l in p.stdout.readlines() + p.stderr.readlines():
        m = re.match(
            "^\s*\#\#\#\# File Type=\\s+(.*)\\s+Format=\\s+(.*)\\s+Name=\\s+(.*)\\s+$", l)
        if m != None:
            if m.group(2) == "html":
                htmlfname = m.group(3)
            elif m.group(2) == "newick":
                dndfname = m.group(3)
#        else:
#            print "tcoffee stdout:%s" %l.strip()
    print(dndfname, htmlfname)

    # delete the dnd file
    if dndfname != "" and os.path.exists(dndfname):
        if dndf == None:
            os.remove(dndfname)
        else:
            os.rename(dndfname, str(dndf))
    elif dndf != None:
        print("warning: t-coffee did not produced a dnd file")

    # delete the dnd file
    if htmlfname != "" and os.path.exists(htmlfname):
        if htmlf == None:
            os.remove(htmlfname)
        else:
            os.rename(htmlfname, str(htmlf))
    elif htmlf != None:
        print("warning: t-coffee did not produced a html file")

    if err != "":
        raise MSAError("t-coffee", err)

    return
