'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from sys import stderr, exit, stdout

from ..mito import revtrnamap, rrnamap, revprot
from ..rna.vienna import RNAeval
# TODO documentation


class LinearSequenceIndexError(Exception):
    """
    exception to be raised when a feature with stop < start is found for linear sequences
    """

    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __str__(self):
        return repr((self.start, self.stop))


def capcup(start1, stop1, start2, stop2, circular, size):
    """
    compute the size (i.e. nr of positions) of the intersection and union of two features

    @param start1 first position of feature 1 in [0:size-1]
    @param stop1 last position of feature 1 in [0:size-1]
    @param start2 first position of feature 2 in [0:size-1]
    @param stop2 last position of feature 2 in [0:size-1]
    @param circularity True iff the chromosome housing the feature is circular
    @param size size of the chromosome housing the feature

    """

    if start1 <= stop1 and start2 <= stop2:
        # check if overlap at all
        # self |---|                       |---|
        # other      |---|           |---|
        if stop1 < start2 or stop2 < start1:
            return 0, length(start1, stop1, circular, size) + length(start2, stop2, circular, size)

        # if overlap return percentage
        # 1  |------------|                |---...
        # 2      |--...              |------------|
        elif (start1 <= start2 <= stop1) or (start2 <= start1 <= stop2):
            return (min(stop1, stop2) - max(start2, start1) + 1), (max(stop1, stop2) - min(start1, start2) + 1)

        else:
            stderr.write(
                "error: unhandled feature position case for overlap computation\n")
            stderr.write("%(%d,%d) (%d,%d)\n" % (start1, stop1, start2, stop2))
            return 0, 0
    else:
        if not circular:
            if start1 > stop1:
                raise LinearSequenceIndexError(start1, stop1)
            else:
                raise LinearSequenceIndexError(start2, stop2)

        if start1 > stop1 and start2 <= stop2:
            a1, u1 = capcup(start1, size - 1, start2, stop2, circular, size)
            a2, u2 = capcup(0, stop1, start2, stop2, circular, size)
        elif start1 <= stop1 and start2 > stop2:
            a1, u1 = capcup(start1, stop1, start2, size - 1, circular, size)
            a2, u2 = capcup(start1, stop1, 0, stop2, circular, size)
        else:
            a1, u1 = capcup(start1, size - 1, start2, size - 1, circular, size)
            a2, u2 = capcup(0, stop1, 0, stop2, circular, size)
        return a1 + a2, u1 + u2


def length(start, stop, circular, size):
    """
    get the length of a feature with 1st position at start and last position 
    at stop, circularity and size of the chromosome are regarded

    @param start 1st position
    @param stop last position
    @param circular circularity of the chromosome homing the feature
    @param size length of the chromosome homing the feature
    """

    if circular:
        if start <= stop:
            return stop - start + 1
        else:
            # ((size-1)-self.start+1) + ((self.stop-0) + 1)
            return size - start + stop + 1
    else:
        if start <= stop:
            return stop - start + 1
        else:
            raise LinearSequenceIndexError(start, stop)


def genorderwriter(featurelist, acc, outfile, mode="w", start=None, signed=True):
    featurelist.sort(key=lambda x: x.start)

    if start != None:
        i = 0
        while(i < len(featurelist) and featurelist[i].outputname(False) != start):
            i += 1

        featurelist = featurelist[i:] + featurelist[:i]

    out = ">%s\n" % (acc)
    for feat in featurelist:
        if signed == True and feat.strand < 0:
            out += "-%s " % (feat.outputname(False))
        else:
            out += "%s " % (feat.outputname(False))
    out += "\n"

    if isinstance(outfile, str):
        file = open(outfile, mode)
        file.write(out)
        file.close()
    elif outfile == None:
        stdout.write(out)
    else:
        outfile.write(out)


class feature:

    def __init__(self, name, type, start, stop, strand, method, translation=None, score=None, rf=None, anticodon=None):
        """
        create a new feature
        @param name name of the feature, i.e. the gene's name
        @param type type of the feature, e.g. tRNA, gene, rRNA
        @param start start position (counting starts at 0, start position belongs to the gene)
        @param stop stop position (counting starts at 0, stop position belongs to the gene)
        @param strand strand (+1/-1)
        @param method method used for predicting the gene 
        @param translation 
        @param score 
        @param rf 
        """

        # TODO score is method dependent
        # TODO translation and rf are only useful for protein coding genes, create derived feature
        # TODO make checks (rf\in\{1,-1\}, start < stop/ circular, len<size/2)

        self.name = name
        self.type = type
        self.start = start
        self.stop = stop
        self.strand = strand
        self.method = method
        self.translation = translation
        self.score = score
        self.rf = rf
        self.anticodon = anticodon

        self.copy = None
        self.part = None
        self.mito = None

    def __add__(self, other):
        """
        this functions should be called to adjust the feature start stop
        if they are of same name .. type

        TODO
        """

        if(other.name.startswith(self.name)):
            name = other.name
        else:
            name = self.name
        type = other.type
        strand = other.strand
        start = min(self.start, other.start)
        stop = max(self.stop, other.stop)
        method = self.method
        translation = self.translation
        if self.translation == None and other.translation != None:
            translation = other.translation

        if self.translation != None and other.translation != None and self.translation != other.translation:
            stderr.write("warning: cannot combine %s with %s\n" %
                         (str(self), str(other)))
            stderr.write("         %s\n" % (repr(self.translation)))
            stderr.write("         %s\n" % (repr(other.translation)))

        return feature(name, type, start, stop, strand, method, translation)

    def __eq__(self, other):
        """
        check two features for equality
        @param self the feature
        @param other another feature
        @return False if name, start, stop, strand, or translation are different True otherwise
        """

        if other == None:
            return False

        if not self.equal_name_type(other):
            return False
        if self.start != other.start:
            return False
        if self.stop != other.stop:
            return False
        if self.strand != other.strand:
            return False
        if self.translation != other.translation:
            return False

        return True

    def __ne__(self, other):
        """
        check for unequality
        @param self the feature
        @param other another feature
        @return True if name, start, stop, strand, or translation are different False otherwise
        """
        return (not self == other)

    def __repr__(self):
        """
        get a string 
        """
        return "%s(%s, %d, %d..%d, %s)" % (self.type, self.getname(), self.strand, self.start + 1, self.stop + 1, self.method)

    def __str__(self):
        """
        get a string 
        """
        return '{0:4}({1:>4},{2:1},{3:5d},{4:5d},{5:5}, {6})'.format(self.type, self.getname(), self.plusminus(), self.start + 1, self.stop + 1, self.method, self.score)

# return "%s(%s, %d, %d..%d, %s)" % ( self.type, self.getname(),
# self.strand, self.start + 1, self.stop + 1, self.method )

    def length(self, circular, size):
        """
        get the length of a feature

        @param self the feature
        @param circular circularity of the chromosome homing the feature
        @param size length of the chromosome homing the feature
        """

        return length(self.start, self.stop, circular, size)

    def capcup(self, other, circular, size):
        """
        compute the size (i.e. nr of positions) of the intersection and union of two features
        @param self the feature
        @param other another feature  
        @param circularity True iff the chromosome housing the feature is circular
        @param size size of the chromosome housing the feature

        """

        return capcup(self.start, self.stop, other.start, other.stop, circular, size)
#        # if one of the features spans the 0 -> shift it
#        # assuming that this only happens for features on circular chromosomes
#        if self.start > self.stop:
#            selfstop = self.stop + size
#        else:
#            selfstop = self.stop
#
#        if other.start > other.stop:
#            otherstop = other.stop + size
#        else:
#            otherstop = other.stop
#
#        # check if overlap at all
#        # self |---|                       |---|
#        # other      |---|           |---|
#        if selfstop < other.start or otherstop < self.start:
#            return 0, self.len( circular, size ) + other.len( circular, size )
#
#        # if overlap return percentage
#        # self  |------------|                |---...
#        # other      |--...              |------------|
#        elif ( self.start <= other.start and other.start <= selfstop ) or ( other.start <= self.start and self.start <= otherstop ):
#            return ( min( selfstop, otherstop ) - max( other.start, self.start ) + 1 ) , ( max( selfstop, otherstop ) - min( self.start, other.start ) + 1 )
#
#        else:
#            stderr.write( "error: unhandled feature position case for overlap computation\n" )
#            stderr.write( "%s\n" % str( self ) )
#            stderr.write( "%s\n" % str( other ) )
#            return 0, 0

    def equal_name_type(self, other):
        """
        check if two features have equal name and type
        L is treated as equal to L1 and L2 (same for S)
        @param self the feature
        @param other another feature
        @return False if name or type differ, True otherwise
        """
        if self.name != other.name:
            if not((self.name == "trnL" and (other.name == "trnL1" or other.name == "trnL2")) or (other.name == "trnL" and (self.name == "trnL1" or self.name == "trnL2")) or
                   (self.name == "trnS" and (other.name == "trnS1" or other.name == "trnS2")) or (other.name == "trnS" and (self.name == "trnS1" or self.name == "trnS2"))):
                return False
            # return False
        if self.type != other.type:
            return False

        return True

    def is_allowed(self, aname=None, fname=None, atype=None, ftype=None, astrand=None, amethod=None, fmethod=None):
        """
        checks if the feature is of a certain type or name 
        @param atype list of allowed types or a string of a type  
        @param ftype forbidden types 
        @param aname list of allowed types or a string of a type  
        @param fname forbidden types 
        @param astrand allowed strand 
        @param fmethod forbidden method 
        @param amethod allowed method 
        @return true if feature in atype and feature not in ftype and name in aname and name not in fname
        """

        if isinstance(atype, str):
            atype = [atype]
        if isinstance(ftype, str):
            ftype = [ftype]

        if atype != None and self.type not in atype:
            return False
        elif ftype != None and self.type in ftype:
            return False

        if isinstance(aname, str):
            aname = [aname]
        if isinstance(fname, str):
            fname = [fname]

        if aname != None and "S" in aname:
            aname.append("S1")
            aname.append("S2")
        if fname != None and "S" in fname:
            fname.append("S1")
            fname.append("S2")
        if aname != None and "L" in aname:
            aname.append("L1")
            aname.append("L2")
        if fname != None and "L" in fname:
            fname.append("L1")
            fname.append("L2")

        if aname != None and self.name not in aname:
            return False
        elif fname != None and self.name in fname:
            return False
        elif astrand != None and self.strand != astrand:
            return False

        if isinstance(amethod, str):
            amethod = [amethod]
        if isinstance(fmethod, str):
            fmethod = [fmethod]

        # need to get the local and global difference
        if self.method == "mitfi" and "local" in self.__dict__:
            if self.local and amethod != None and "lmitfi" in amethod:
                return True
            elif not self.local and amethod != None and "gmitfi" in amethod:
                return True
            elif self.local and fmethod != None and "lmitfi" in fmethod:
                return False
            elif not self.local and fmethod != None and "fmitfi" in fmethod:
                return False

        if amethod != None and self.method not in amethod:
            return False
        elif fmethod != None and self.method in fmethod:
            return False

        return True

    def overlap(self, other, circular, size):
        """
        check if two features overlap and return the overlap percentage, i.e.
        length of the intersection of the intervals / length of the union of the intervals

        @param self the feature
        @param other another feature
        @param size of the chromosom housing the feature 
        @return overlap percentage (i.e. 100*cap/cup) 
        """

        cap, cup = self.capcup(other, circular, size)

        return 100.0 * float(cap) / cup

    def getname(self):
        """
        get a printable represenation of the gene name including the copy and 
        part information
        @return X_Y_Z where X is the gene name, Y the copy number, and the part number (as character)  
        """

        return self.outputname()

    def bedstr(self, acc):
        """
        this function returns the string to be written in a bed file
        """
        if self.score != None:
            s = str(self.score)
        else:
            s = "."

        return "%s\t%d\t%d\t%s\t%s\t%s" % (acc, self.start, self.stop + 1, self.getname(), s, self.plusminus())

    def gffstr(self, acc):
        """
        this function returns the string to be written in a ggf3 file
        http://gmod.org/wiki/GFF3#GFF3_Format).
        """
        if self.score != None:
            s = str(self.score)
        else:
            s = "."
        if self.rf == None:
            rf = "."
        else:
            rf = str(self.rf)

        return "{seqid}\t{source}\t{type}\t{start}\t{end}\t{score}\t{strand}\t{phase}\tName={name}".format(seqid=acc, source=self.method, type=self.type, start=self.start + 1, end=self.stop + 1, score=s, strand=self.plusminus(), phase=rf, name=self.getname())

    def tblstr(self):
        """
        this function returns the string to be written in a mito file
        """

        if int(self.strand) == 1:
            pos = "%d\t%d" % (self.start + 1, self.stop + 1)
        elif int(self.strand) == -1:
            pos = "%d\t%d" % (self.stop + 1, self.start + 1)
        else:
            raise Exception("Strand Error")
        out = "%s\tgene\n" % (pos)
        if self.type == "gene":
            out += "\t\t\tgene\t%s\n" % self.getname()
            out += "%s\tCDS\n" % (pos)
            out += "\t\t\tproduct\t%s\n" % (revprot[self.name])
        elif self.type == "tRNA":
            out += "\t\t\tgene\t%s\n" % self.getname()
            out += "%s\ttRNA\n" % (pos)
            out += "\t\t\tproduct\ttRNA-%s\n" % (revtrnamap(self.name))
        elif self.type == "rRNA":
            out += "%s\trRNA\n" % (pos)
            out += "\t\t\tproduct\t%s-rRNA\n" % (rrnamap[self.name])
        else:
            raise Exception("type Error")
        return out

    def mitostr(self, acc):
        """
        this function returns the string to be written in a mito file
        """
        if self.score != None:
            s = str(self.score)
        else:
            s = "."
        if self.anticodon != None:
            acodon = self.anticodon
        else:
            acodon = "-"
        if self.part != None:
            part = str(self.part)
        else:
            part = "."
        if self.copy != None:
            copy = str(self.copy)
        else:
            copy = "."

        try:
            struct = self.structure
        except:
            struct = "."

        try:
            acp = self.anticodonpos
        except:
            acp = "."

        return "{acc}\t{tpe}\t{name}\t{met}\t{start}\t{stop}\t{strand}\t{score}\t{acodon}\t{part}\t{copy}\t{struct}\t{apos}".format(acc=acc,
                                                                                                                                    tpe=self.type, name=self.name, met=self.method, start=self.start,
                                                                                                                                    stop=self.stop, strand=self.strand, score=s,
                                                                                                                                    acodon=acodon, part=part, copy=copy, struct=struct,
                                                                                                                                    apos=acp)
# return "%s\t%s\t%s\t%s\t%d\t%d\t%d\t%s\t%s\t%s\t%s\t%s" % ( acc,
# self.type, self.name, self.method, self.start, self.stop, self.strand,
# s, acodon, part, copy, struct )

    def outputname(self, anticodon=True):
        #        if self.name.startswith( "ND" ):
        #            return "nad%s" % self.name[2:].upper()
        #        if self.name == "CYTB":
        #            return "cob"
        #        if self.name == "12S":
        #            return "rrnS"
        #        if self.name == "16S":
        #           return "rrnL"
        #        if self.type == "gene":
        #            if self.name[-1] == "l" or self.name[-1] == "L":
        #                return self.name[:-1].lower() + "L"
        #            return self.name.lower()

        name = ""
        if self.type == "tRNA" and not self.name.startswith("trn"):
            name += "trn"

        name += self.name

        if self.copy != None:
            name += "-" + str(self.copy)
        if self.part != None:
            name += "_" + chr(97 + self.part)

        if anticodon and self.type == "tRNA":
            if self.anticodon != None:
                name += "(%s)" % self.anticodon.get_anticodon().lower()
            else:
                name += "(---)"

        return name

    def plusminus(self):
        """
        @return '+' if on positive strand, '-' else 
        """
        if self.strand > 0:
            return '+'
        else:
            return '-'


class blast_feature(feature):
    """
    a feature predicted with blast; 
    derived from feature with the additional properties: 
    - qstart: avg. relative start position in the query
    - qstop : avg. relative stop position in the query 
    """

    def __init__(self, name, type, strand, positions, ascore, avg, pavg, mito=None):
        """
        @param positions: a list of positions, the first and the last in the list 
            must be really the first and last position 
        @param ascore: specify which value at the position should be used for
            the calculation of the score, 'h': height, 'e': (exponent of) evalue,
            'b': bitscore
        @param avg: if False then get the sum of the values at the positions, 
            if True then get the average of the summed values (i.e. divided by length)
        @param pavg: False: Sum of the values at a position
            True: the average values at each position are summed  
            (does not apply for height) 
        """

        self._evalue = 0.0
        self._bitscore = 0.0
        self._height = 0.0

        len = float(
            positions[-1].get_position() - positions[0].get_position() + 1)

        for p in positions:
            self._evalue += p.get_evalue(pavg)
            self._bitscore += p.get_bitscore(pavg)
            self._height += p.get_height()

        self._evalue /= len
        self._bitscore /= len
        self._height /= len

        if ascore == 'h':
            s = self._height
        elif ascore == 'e':
            s = self._evalue
        elif ascore == 'b':
            s = self._bitscore

        if avg == False:
            s *= len

        s = round(s, 1)

        feature.__init__(self, name, type,
                         start=positions[0].get_position(), stop=positions[-1].get_position(),
                         strand=strand, method="mitos", score=s)

        self.qstart = positions[0].get_query()
        self.qstop = positions[-1].get_query()

        if(self.qstart > self.qstop):
            self.qstart, self.qstop = self.qstop, self.qstart

        self.mito = mito

    def __str__(self):
        return '{0} {1:6.1f} {2:5.1f} {3:5.1f} {4:>4.0f}-{5:<4.0f}'.format(
               feature.__str__(self), round(self._height, 1),
               round(self._evalue, 1), round(self._bitscore, 1), round(self.qstart), round(self.qstop))


class blasthit_feature(feature):
    """
    a feature for blast data; derived from feature with the additional properties:
    - identity
    - aligment_length
    - mismatches
    - gap_openings 
    - evalue: 
    - qstart: 
    - qstop :
    """

    def __init__(self, name, type, start, stop, method, identity, aligment_length, mismatches, gap_openings, qstart, qstop, evalue):
        """
        constructor
        """
        # get strand
        if qstart < qstop:
            strand = 1
        else:
            strand = -1

        feature.__init__(self, name, type, start, stop, strand, method)

        self.identity = identity
        self.aligment_length = aligment_length
        self.mismatches = mismatches
        self.gap_openings = gap_openings
        self.evalue = evalue
        self.qstart = qstart
        self.qstop = qstop


class trnafeature(feature):
    """
    a feature predicted with trna; derived from feature with the additional properties: 
    - structure: 
    - anticodonpos: 
    - anticdon : 
    - sequence:
    - evalscore result of RNAeval 
    """

    def __init__(self, name, type, start, stop, strand, method, score, sequence, struct, anticodonpos, anticodon, evalscore=None):
        feature.__init__(
            self, name, type, start, stop, strand, method, score=score)

        self.structure = struct
        self.anticodonpos = anticodonpos
        self.anticodon = anticodon
        self.sequence = sequence
        if evalscore == None and self.sequence != None and self.structure != None:
            self.evalscore = RNAeval(self.sequence, self.structure)[0]
        else:
            self.evalscore = evalscore
        return

    def __str__(self):

        if self.anticodon != None:
            ac = " " + self.anticodon.get_anticodon()
        else:
            ac = ""

        return '{0}{1} score:{2:6.1f}\n{3}\n{4}'.format(feature.__str__(self),
                                                        ac, round(
                                                            self.score, 1),
                                                        self.structure, self.sequence)

    def gffstr(self, acc):
        return "%s\t" % (feature.gffstr(self, acc))


class mitfifeature(trnafeature):
    """
    a trnafeature predicted with mitfi; derived from trnafeature with the additional properties: 
    - qstart: 
    - qstop:
    - evalue 
    - pvalue: 
    - model:
    - local: It is 0 if it is a global hit and it is 1 if it is a local hit
    - mito: If we belive it is 2 if it is a copy it is 1 and if it is crap it is 0 
    """

    def __init__(self, name, type, start, stop, strand, method, score, sequence, struct, anticodonpos, anticodon, qstart, qstop, evalue, pvalue, model, evalscore=None, local=None, mito=None):
        trnafeature.__init__(self, name, type, start, stop, strand, method,
                             score, sequence, struct, anticodonpos, anticodon, evalscore=evalscore)

        self.qstart = qstart
        self.qstop = qstop
        self.evalue = evalue
        self.pvalue = pvalue
        self.model = model
        self.local = local
        self.mito = mito
        return

    def gffstr(self, acc):
        return "%s; model %s; evalue %f; pvalue %f; qstart %d; qstop %d" % (trnafeature.gffstr(self, acc), self.model, self.evalue, self.pvalue, self.qstart + 1, self.qstop + 1)
