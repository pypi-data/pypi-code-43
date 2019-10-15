'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from __future__ import print_function
import os
import re
import subprocess
from sys import stderr

import mitos.extprog as extprog


def is_valid_bp(a, b):
    a = a.lower()
    b = b.lower()

    if a > b:
        a, b = b, a

    if a == 'a' and (b == 't' or b == 'u'):
        return True
    elif a == 'c' and b == 'g':
        return True
    elif a == 'g' and (b == 't' or b == 'u'):
        return True
    else:
        return False


class rna:
    """
    TODO
    """

    def init(self):
        self.db = ""
        self.bp = []
        return

    def load_dotbracket(self, db):
        """
        load a dot bracket representation
        \param db the dot bracket representation
        """
#        print "loading rna ", db
        self.db = ""
        self.bp = []
        stack = []

        for i in xrange(len(db)):
            if db[i] == '(':
                stack.append(i)
            elif db[i] == ')':
                self.bp.append((stack.pop(), i))

    def ckeck_sequence(self, seq):
        vbp = []
        for bp in self.bp:
            if is_valid_bp(seq[bp[0]], seq[bp[1]]):
                vbp.append(bp)
        return vbp

    def check_sequences(self, sequences):

        valbp = []
        for bp in self.bp:
            v = 0
            for seq in sequences:
                if is_valid_bp(seq[bp[0]], seq[bp[1]]):
                    v += 1
            valbp.append(v)

        print("VALIDITY ", len(sequences), ",".join([str(x) for x in valbp]))


# -p
#    Calculate the partmarna.tar.bz2ition function and base pairing probability matrix in addition to the mfe structure.
#    Default is calculation of mfe structure only. Prints a coarse representation of the pair probabilities
#    in form of a pseudo bracket notation, the ensemble free energy, the frequency of the mfe structure,
#    and the structural diversity. See the description of pf_fold() and mean_bp_dist() in the RNAlib documentation for details.
#    Note that unless you also specify -d2 or -d0, the partition function and mfe calculations will use a slightly
#    different energy model. See the discussion of dangling end options below.
# -p0
#    Calculate the partition function but not the pair probabilities, saving about 50% in runtime. Prints the ensemble
#    free energy -kT ln(Z).
# -C
#    Calculate structures subject to constraints. The program reads first the sequence, then a string containing constraints
#    on the structure encoded with the symbols: | (the corresponding base has to be paired x (the base is unpaired) < (base
#    i is paired with a base j>i) > (base i is paired with a base j<i) and matching brackets ( ) (base i pairs base j)
#    With the exception of "|", constraints will disallow all pairs conflicting with the constraint. This is usually sufficient
#    to enforce the constraint, but occasionally a base may stay unpaired in spite of constraints. PF folding ignores constraints
#    of type "|".
# -T temp
#    Rescale energy parameters to a temperature of temp C. Default is 37C.
# -4
#    Do not include special stabilizing energies for certain tetra-loops. Mostly for testing.
# -d[0|1|2|3]
#    How to treat "dangling end" energies for bases adjacent to helices in free ends and multi-loops: With (-d1) only unpaired
#    bases can participate in at most one dangling end, this is the default for mfe folding but unsupported for the partition
#    function folding. With -d2 this check is ignored, dangling energies will be added for the bases adjacent to a helix on both
#    sides in any case; this is the default for partition function folding (-p). -d or -d0 ignores dangling ends altogether (mostly for debugging).
#    With -d3 mfe folding will allow coaxial stacking of adjacent helices in multi-loops. At the moment the implementation
#    will not allow coaxial stacking of the two interior pairs in a loop of degree 3 and works only for mfe folding.
#    Note that by default (as well as with -d1 and -d3) pf and mfe folding treat dangling ends differently. Use -d2 in addition
#    to -p to ensure that both algorithms use the same energy model.
# -noLP
#    Produce structures without lonely pairs (helices of length 1). For partition function folding this only disallows pairs
#    that can only occur isolated. Other pairs may still occasionally occur as helices of length 1.
# -noGU
#    Do not allow GU pairs.
# -noCloseGU
#    Do not allow GU pairs at the end of helices.
# -e 1|2
#    Rarely used option to fold sequences from the artificial ABCD... alphabet, where A pairs B, C-D etc. Use the energy
#    parameters for GC (-e 1) or AU (-e 2) pairs.
# -P <paramfile>
#    Read energy parameters from paramfile, instead of using the default parameter set. A sample parameter file should
#    accompany your distribution. See the RNAlib documentation for details on the file format.
# -nsp pairs
#    Allow other pairs in addition to the usual AU,GC,and GU pairs. pairs is a comma separated list of additionally allowed
#    pairs. If a the first character is a "-" then AB will imply that AB and BA are allowed pairs. e.g. RNAfold -nsp -GA will
#    allow GA and AG pairs. Nonstandard pairs are given 0 stacking energy.
# -S scale
#    In the calculation of the pf use scale*mfe as an estimate for the ensemble free energy (used to avoid overflows).
#    The default is 1.07, useful values are 1.0 to 1.2. Occasionally needed for long sequences. You can also recompile the
#    program to use double precision (see the README file).
# -circ
# Assume a circular (instead of linear) RNA molecule. Currently works only
# for mfe folding.

def RNAalifold(alnfile, alifname, alifoldf=None, alirnaf=None, alidotf=None, alnf=None, constraints=None, **keywords):
    """
    call RNAalifold
    \param alnfile alignment file for input
    \param alifname filename for the output of RNAalifold
    \param alifoldf filename for alifold.out (only produced with -p), if None then the file will be deleted 
    \param alirnaf filename for the alirna.ps file (produced per default), if None then the file will be deleted
    \param alidotf filename for the alidot.ps file (only produced with -p), if None then the file will be deleted 
    \param alnf filename for the aln.ps file (only produced with -aln), if None then the file will be deleted 
    \param constraints name of the constraints file 

    -cv factor
        Set the weight of the covariance term in the energy function to factor. Default is 1.
    -nc factor
        Set the penalty for non-compatible sequences in the covariance term of the energy function to factor. Default is 1.
    -E
        Score pairs with endgaps same as gap-gap pairs.
    -mis
        Output "most informative sequence" instead of simple consensus: For each column of the alignment output the set of nucleotides with frequence greater than average in IUPAC notation.
    -color
        print in color
    -aln
    """

    cfile = None  # constraints file

    alifoldpar = [extprog.shortparm('cv', 'int'), extprog.shortparm('nc', 'int'), extprog.shortparm('E', 'flag'), extprog.shortparm('mis', 'flag'),
                  extprog.shortparm('color', 'flag'), extprog.shortparm('aln', 'flag')]
    stdpar = [extprog.shortparm('p', 'flag'), extprog.shortparm('p0', 'flag'), extprog.shortparm('C', 'flag'), extprog.shortparm('T', 'float'),
              extprog.shortparm('_4', 'flag'), extprog.shortparm('d', 'int', [
                  0, 1, 2, 3]), extprog.shortparm('noLP', 'flag'), extprog.shortparm('noGU', 'flag'),
              extprog.shortparm('noCloseGU', 'flag'), extprog.shortparm(
                  'e', 'int', [1, 2]), extprog.shortparm('P', 'file'), extprog.shortparm('nsp', 'str'),
              extprog.shortparm('S', 'float'), extprog.shortparm('circ', 'flag')]

    cl = extprog.cmdline(keywords, stdpar, alifoldpar)
    pars = str(cl) + alnfile

    if cl.get("C") != None:
        if constraints == None:
            raise "RNAalifold", "-C but no constraints file given"
        cfile = open(constraints, "r")
#    print "alifold parameters ", pars
    p = subprocess.Popen("RNAalifold %s" % (pars), shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True)
    if cfile != None:
        p.stdin.write(cfile.read())

    if cl.get("C") != None:
        cfile.close()

    err = ""
    for i in p.stderr.readlines():
        if i == "" or re.match("^\\d+ sequences; length of alignment \\d+\.$", i) != None:
            continue
        else:
            err += i + "\n"

    if err != "":
        raise extprog.StderrError("RNAalifold %s" % pars, err)

    ali = open(alifname, "w")
    ali.write(p.stdout.read())
    ali.close()

    # rename / delete alifold.out
    if os.path.exists("alifold.out"):
        if alifoldf == None:
            os.remove("alifold.out")
        else:
            os.rename("alifold.out", str(alifoldf))
    elif alifoldf != None:
        print("warning: RNAalifold did not produced a alifold.out file")
        if cl.get('p') == None:
            print("         you have to enable parameter -p")

    # rename / delete the various ps outputs
    if os.path.exists("alirna.ps"):
        if alirnaf == None:
            os.remove("alirna.ps")
        else:
            os.rename("alirna.ps", str(alirnaf))
    elif alirnaf != None:
        print("warning: RNAalifold did not produced a alirna.ps file")

    if os.path.exists("alidot.ps"):
        if alidotf == None:
            os.remove("alidot.ps")
        else:
            os.rename("alidot.ps", str(alidotf))
    elif alidotf != None:
        print("warning: RNAalifold did not produced a alidot.ps file")
        if cl.get('p') == None:
            print("         you have to enable parameter -p")

    if os.path.exists("aln.ps"):
        if alnf == None:
            os.remove("aln.ps")
        else:
            os.rename("aln.ps", str(alnf))
    elif alnf != None:
        print("warning: RNAalifold did not produced a aln.ps file")
        if cl.get('aln') == None:
            print("         you have to enable parameter -aln")

    return


def RNAalifold_parse(alifname, alifoldf=None):
    """
    parse the result file of RNAalifold
    \param alifname name of the file conatining the stdout of RNAalifold
    \param alifoldf name of the file conatining the alifold.out contents, if None -> ignored
    \return dict containing the keys 'seq', 'mfe', and 'pf'; seq contains just the sequence which is folded; 
    mfe contains the mfe-structure 'str', the energy 'nrg', as well as the energy components :
    'mnrg' mfe contribution and 'snrg' sequence contribution
    """
# A plain text file containing information on each plausible pair, ranked by "credibility" (see paper).
# [they are sorted by: (probability + #comp_mutations/#incomp_mutations) ]
# Each line lists the paired bases i and j, the number of incompatible sequences, the predicted probability,
# an entropy measure, and the base pair types occurring at this position.


# Base pair probabilities are sometimes summarized in pseudo bracket notation with the additional symbols
# ',', '|', '{', '}'. Here, the usual '(', ')', '.', represent bases with a strong preference (more than 2/3)
# to pair upstream (with a partner further 3'), pair down-stream, or not pair, respectively. '{', '}', and ','
# are just weaker version of the above and '|' represents a base that is mostly paired but has pairing partners
# both upstream and downstream. In this case open and closed brackets need
# not match up.

    pairs = []
    if alifoldf != None:
        f = open(alifoldf, "r")
        for l in f.readlines():
            if re.match("^\\s*\\d+ sequence; length of alignment \\d+\\s*$", l) != None:
                continue
            if re.match("^alifold output$", l) != None:
                continue
            if re.match("^([\.,\|\{\}\(\)]+)\\s*$", l) != None:
                continue

            l = l.strip().split()
            pairs.append({'start': int(l[0]), 'end': int(l[1]), 'incomp': int(
                l[2]), 'prob': float(l[3][:-1]), 'entropy': float(l[4]), 'bp': []})
            for i in range(5, len(l)):
                if l[i] == '+':
                    continue
                pairs[-1]['bp'].append((l[i][:2], int(l[i][3:])))

            if l[-1] == '+':
                pairs[-1]['inmfe'] = True
            else:
                pairs[-1]['inmfe'] = False

        f.close

    f = open(alifname, "r")

    results = {}
    for l in f.readlines():
        if l == "":
            continue

        m = re.match("^([_ACGTUXagctux]+)$", l)
        if m != None:
            results['seq'] = m.group(1)
            continue

        m = re.match(
            "^([\.\(\)]+)\\s*\(\\s*([-.\\d]+)\\s*=\\s*(\\s*[-.\\d]+)\\s*\+\\s*([-.\\d]+)\\s*\)\\s*$", l)
        if m != None:
            results['mfe'] = {}
            results['mfe']['str'] = m.group(1)
            results['mfe']['nrg'] = float(m.group(2))
            results['mfe']['mnrg'] = float(m.group(3))
            results['mfe']['snrg'] = float(m.group(4))

            continue

        m = re.match("^([\.,\|\{\}\(\)]+)\\s+\[\\s*([+-\.\\d]+)\\s*\]\\s*$", l)
        if m != None:
            results['pf'] = {}
            results['pf']['str'] = m.group(1)
            results['pf']['nrg'] = m.group(2)
            results['pf']['pairs'] = pairs
            continue

        print("RNAalifold_parse: ", l)
    f.close()

    return results


def RNAeval(sequences, structures, **keywords):
    """
    call RNAeval [-T temp] [-4] [-d[0|1|2|3]]  [-e 1|2] [-P paramfile] [-circ] [-noconv] [-logML]
    \param sequences a list of sequences / one sequence
    \param structures a list of structures / one structure
    \param keywords parameters for RNAeval
    \return list of energy values
    """
    # print sequences
    # print structures
    evalpar = [extprog.shortparm('T', 'float'), extprog.shortparm('_4', 'flag'), extprog.shortparm('d', 'flag'),
               extprog.shortparm('d0', 'flag'), extprog.shortparm(
                   'd1', 'flag'), extprog.shortparm('d2', 'flag'), extprog.shortparm('d3', 'flag'),
               extprog.shortparm('e', 'int'), extprog.shortparm('P', 'file'), extprog.shortparm(
                   'circ', 'flag'), extprog.shortparm('noconv', 'flag'),
               extprog.shortparm('logML', 'flag')]

    if isinstance(sequences, str):
        sequences = [sequences]
    if isinstance(structures, str):
        structures = [structures]

    input = ""
    if len(sequences) == 1 and len(structures) > 1:
        for i in range(len(structures)):
            input += sequences[0] + "\n" + structures[i] + "\n"
    elif len(sequences) > 1 and len(structures) == 1:
        for i in range(len(sequences)):
            input += sequences[i] + "\n" + structures[0] + "\n"
    elif len(sequences) == len(structures):
        for i in range(len(sequences)):
            input += sequences[i] + "\n" + structures[i] + "\n"
    else:
        raise "RNAeval", "need equal number of sequences and structures or one of them has to be single"
    input += "@\n"

    cl = extprog.cmdline(keywords, evalpar)
    pars = str(cl)
    p = subprocess.Popen("RNAeval %s" % (pars), shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    p.stdin.write(input)
    p.stdin.close()
    p.wait()

    # evaluate the output
    err = p.stderr.readlines()
    nerr = []
    for e in err:
        m = re.match(
            "^WARNING: bases [0-9]+ and [0-9]+ \(..\) can't pair!$", e)
        if m == None:
            nerr.append(e)

    err = "".join(nerr)
    if err != "":
        stderr.write(
            "RNAeval returned an error message for:\n%s\n%s\n" % (input, err))

    results = []
    for l in p.stdout.readlines():
        m = re.match("[\.\(\)]+\\s+\(\\s*([-\.\\d]+)\)", l)
        if m != None:
            results.append(float(m.group(1)))

    return results


def RNALfold(sequence, **keywords):
    """
    [-L span] [-T temp] [-4] [-noLP] [-noGU] [-noCloseGU] [-e 1|2] [-P paramfile] [-nsp pairs]
    return a list of 3-tuples (structure, energy, position)
    """

    st = re.compile("^([\(\)\.]+)\\s\(\\s*([\-0-9\.]+)\)\\s+(\\d+)\\s*$")
    sq = re.compile("^\\S+$")
    en = re.compile("^\\s*\(\\s*([\-0-9\.]+)\)\\s*$")

    par = [extprog.shortparm('L', 'int'), extprog.shortparm('T', 'float'), extprog.shortparm('noGU', 'flag'), extprog.shortparm('noCloseGU', 'flag'),
           extprog.shortparm('e', 'int', [1, 2]), extprog.shortparm('P', 'file'), extprog.shortparm('nsp', 'string')]
    cl = str(extprog.cmdline(keywords, par))

    p = subprocess.Popen("RNALfold %s" % (cl), shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

    p.stdin.write(sequence + "\n")
    p.stdin.write("@\n")
    p.stdin.close()

    # parse output
    structures = []
    minenergy = 0.0

    for l in p.stdout.readlines():
        if len(l) == 0 or l[0] == '>':
            continue

        m = st.match(l)
        if m != None:
            #            print "structure"
            structures.append((m.group(1), float(m.group(2)), int(m.group(3))))
            continue
        m = sq.match(l)
        if m != None:
            #            print "sequence ", l
            continue
        m = en.match(l)
        if m != None:
            #            print "energy   ", l
            minenergy = float(m.group(1))
            continue
        print("NO MATCH ", l)

#    for s in structures:
#        print s
#    print minenergy
    p.wait()
    return structures, minenergy


def RNAplot(sequence, structure, fname, **keywords):
    """
    RNAplot [-t 0|1] [-o ps|gml|xrna|svg]
    """
    # todo parameters [--pre string] [--post string]

    plotpar = [extprog.shortparm('t', 'int', [0, 1]), extprog.shortparm(
        'o', 'str', ['ps', 'gml', 'xrna', 'svg'])]
    cl = extprog.cmdline(keywords, plotpar)
    pars = str(cl)

    p = subprocess.Popen("cd %s; RNAplot %s; cd -;" % (os.path.dirname(fname), pars), shell=True,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    p.stdin.write(sequence + "\n")
    p.stdin.write(structure + "\n")
    p.stdin.write("@\n")
    p.stdin.close()
    p.wait()

    if cl.get("o") != None:
        ext = cl.get("o")
    else:
        ext = "ps"

    if os.path.exists("%s/rna.%s" % (os.path.dirname(fname), ext)):
        os.rename("%s/rna.%s" % (os.path.dirname(fname), ext), fname)
    elif fname != None:
        print("warning: RNAplot did not produced a %s file" % (ext))
        for l in p.stderr.readlines():
            print("stderr", l.strip())
        for l in p.stdout.readlines():
            print("stdout", l.strip())

    return
