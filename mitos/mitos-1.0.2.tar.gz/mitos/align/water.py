'''
@author: maze

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from __future__ import print_function

from Bio import Data

import os
import re
import subprocess
import sys
import tempfile


from . import WATER, alignment
from .. import extprog


class waterparm(extprog.parm):

    def __init__(self, name, type, range=[]):
        extprog.parm.__init__(self, name, type, range)
        self.infix = " "
        self.prefix = "-"


class water(alignment):
    """
    make alignment with water
    http://emboss.sourceforge.net/apps/cvs/emboss/apps/water.html
    """

    def __init__(self, seq1, seq2, **keywords):

        self.len = None
        self.id = None
        self.sim = None
        self.gaps = None
        self.score = None

        seq1file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        seq1filename = seq1file.name
        seq1file.write(">seq1\n%s\n" % (str(seq1)))
        seq1file.close()

        seq2file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        seq2filename = seq2file.name
        seq2file.write(">seq2\n%s\n" % (str(seq2)))
        seq2file.close()

        outfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        outfilename = outfile.name
        outfile.close()

        pars = [waterparm('asequence', 'file'), waterparm('bsequence', 'file'),
                waterparm('gapopen', 'float'), waterparm(
                    'gapextend', 'float'), waterparm('outfile', 'file'),
                waterparm('datafile', 'file'), waterparm(
                    'brief', 'flag'), waterparm('nobrief', 'flag'),
                waterparm('auto', 'flag'), waterparm('awidth3', 'int'), waterparm('aglobal3', 'flag')]

        # set input and output file names
        keywords['asequence'] = seq1filename
        keywords['bsequence'] = seq2filename
        keywords['outfile'] = outfilename
        # dont ask for unset parameters
        # set alignment output width to get the whole alignment on one line
        keywords['auto'] = True
        keywords['awidth3'] = max(len(seq1), len(seq2))

        cl = extprog.cmdline(keywords, pars)
        pars = str(cl)

        p = subprocess.Popen("%s %s" % (
            WATER, pars), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        stdout, stderr = p.communicate()

        stderrr = ""
        for l in stderr.splitlines():
            if l != "Smith-Waterman local alignment.":
                stderrr += l
        if stderrr != "":
            print("water returned an error %s" % sys.stderr)
            sys.exit()

        fo = open(outfilename)

        # parse its output

        alnseq = []
        for l in fo.readlines():
            # print(l.strip())
            m = re.match("^# Length:\s+(\d+)", l)
            if m != None:
                # print("match len")
                self.len = int(m.group(1))
            m = re.match("^# Identity:\s+(\d+)/(\d+) \(\s{0,2}([.\d]+)%\)", l)
            if m != None:
                # print("match id")
                self.id = float(m.group(3))
            m = re.match(
                "^# Similarity:\s+(\d+)/(\d+) \(\s{0,2}([.\d]+)%\)", l)
            if m != None:
                # print("match sim")
                self.sim = float(m.group(3))
            m = re.match("^# Gaps:\s+(\d+)/(\d+) \(\s{0,2}([.\d]+)%\)", l)
            if m != None:
                # print("match gaps")
                self.gaps = float(m.group(3))
            m = re.match("^# Score:\s+([.\d]+)", l)
            if m != None:
                # print("match score")
                self.score = float(m.group(1))

            m = re.match(
                "^.*(\d+)\s+([%s.-]+)\s+(\d+)" % Data.IUPACData.ambiguous_dna_letters, l)
            if m != None:
                # print("match seq")
                alnseq.append((m.group(2), int(m.group(1)), int(m.group(3))))

#        print("len %d id %f sim %d gaps %d score %d" %(alnlen,alnid, alnsim, alngaps, alnscore ))
#        for a in alnseq:
#            print(a)

        alignment.__init__(self, alnseq[0][0], alnseq[1][0], alnseq[0][
                           1], alnseq[0][2], alnseq[1][1], alnseq[1][2])

        fo.close()

        os.unlink(seq1filename)
        os.unlink(seq2filename)
        os.unlink(outfilename)

        return

    def __str__(self):
        """
        pretty print the alignment
        """

        return """# Length     %d
# Identity   %.2f
# Similarity %.2f
# Gaps       %.2f
# Score      %.2f
%s""" % ( self.len, self.id, self.sim, self.gaps, self.score, alignment.__str__( self ) )
