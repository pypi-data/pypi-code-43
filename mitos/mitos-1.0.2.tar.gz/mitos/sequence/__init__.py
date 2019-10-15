'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from __future__ import print_function
from random import randint, shuffle
from sys import stdout, stderr, exit

from Bio import Alphabet
from Bio.Alphabet.IUPAC import ambiguous_dna
try:
    from Bio.Alphabet import _verify_alphabet as verify_alphabet
except:  # for old biopython
    from Bio.utils import verify_alphabet
from Bio import Data
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord


class NoFastaException(Exception):
    """
    Exception to be raised when no Fasta is found.
    """

    def __str__(self):
        """
        print exception
        """
        return "The File is not a Fasta!"


class MultiFastaException(Exception):
    """
    Exception to be raised when a multi Fasta is found.
    """

    def __str__(self):
        """
        print exception
        """
        return "Can not parse multi Fasta!"


class AlphabetException(Exception):
    """
    Exception to be raised when the alphabet does not match the sequence 
    """

    def __init__(self, seq, alpha):
        """
        constructor
        @param value the sequence
        """
        self.seq = seq
        self.alpha = alpha

    def __str__(self):
        """
        print exception
        """
        return "Alphabet %s does not fit to sequence %s" % (str(self.alpha), str(self.seq))


class sequence(Seq):
    """
    overwritten from biopython
    - handle circular sequences
    """

    def __init__(self, data, alphabet=Alphabet.IUPAC.IUPACAmbiguousDNA(), circular=False, upper=False):
        """
        @param[in] upper if true: transform each letter to upper case, else: leave as is 
        """

        data = data.strip().upper()
        Seq.__init__(self, data, alphabet)
        self.circular = circular

        if not verify_alphabet(self):
            raise AlphabetException(str(self), alphabet)

    def __eq__(self, other):
        """
        check two sequences for equality
        - same type (two sequences)
        - same alphabet
        - same circularity
        - same data (ambiguities are checkes, i.e. N=A, ...)
        """

        if not isinstance(self, sequence) or not isinstance(other, sequence):
            return False

        if self.alphabet != other.alphabet:
            return False

        if self.circular != other.circular:
            return False

        if self.alphabet == Alphabet.IUPAC.ambiguous_dna or self.alphabet == Alphabet.IUPAC.unambiguous_dna:
            ambiguous_nucleotide_values = Data.IUPACData.ambiguous_dna_values
        elif self.alphabet == Alphabet.IUPAC.ambiguous_rna or self.alphabet == Alphabet.IUPAC.unambiguous_rna:
            ambiguous_nucleotide_values = Data.IUPACData.ambiguous_rna_values
        else:
            return (str(self) == str(other))

#        print self, other
        for i in range(len(self)):
            #            print self[i], other[i]
            # print self[i], other[i], ambiguous_nucleotide_values[other[i] ],
            # ambiguous_nucleotide_values[self[i] ]

            try:
                oa = set(ambiguous_nucleotide_values[other[i]])
            except:
                oa = set()

            try:
                sa = set(ambiguous_nucleotide_values[self[i]])
            except:
                sa = set()

            if self[i] == other[i] or\
                    ( self[i] in oa ) or ( other[i] in sa )\
                    or (not oa.isdisjoint(sa)):
                continue
            else:
                #                print "RETURN FALSE"
                return False
#        print "RETURN TRUE"
        return True

    def __neq__(self, other):
        """
        check two sequences for inequality
        """
        return (not self == other)

    def __repr__(self):
        """
        Returns a (truncated) representation of the sequence for debugging.
        """
        if self.circular:
            mode = "circular"
        else:
            mode = "linear"

        if len(self) > 60:
            # Shows the last three letters as it is often useful to see if there
            # is a stop codon at the end of a sequence.
            # Note total length is 54+3+3=60
            return "%s('%s...%s', %s, %s)" % (self.__class__.__name__,
                                              self[:54], self[-3:],
                                              mode,
                                              repr(self.alphabet))
        else:
            return "%s(%s, %s, %s)" % (self.__class__.__name__,
                                       str(self),
                                       mode,
                                       repr(self.alphabet))

   # def __str__(self):
   #     """
   #     print sequence in fasta format
   #     """
   #     return "%s" %(self.__data)

    def __lshift__(self, other):
        """
        shift the sequence by other (int) to the left
        """
        if (type(other) != type(0)):
            raise TypeError, "sequence shift with " + \
                repr(other) + " " + repr(type(other)) + " is impossible"
        if (self.circular == False):
            raise TypeError, "sequence shift of linear sequence is impossible"

        rdata = "".join([self[(i + other) % len(self)]
                         for i in range(len(self))])
        return sequence(rdata, self.alphabet, self.circular)

    def __rshift__(self, other):
        """
        shift the sequence by other (int) to the right
        """
        if (type(other) != type(0)):
            raise TypeError, "sequence shift with " + \
                repr(other) + " " + repr(type(other)) + " is impossible"
        if (self.circular == False):
            raise TypeError, "sequence shift of linear sequence is impossible"

        rdata = "".join([self[(i - other) % len(self)]
                         for i in range(len(self))])
        return sequence(rdata, self.alphabet, self.circular)

    def dinucleotide_count(self, osb=True):
        """
        get the dinucleotide count of the sequence
        \param osb if true consider only standard bases (ATCG)
        \return a dictionary containing the counts 
        """
        dn = {}

        for sb1 in Data.IUPACData.unambiguous_dna_letters:
            for sb2 in Data.IUPACData.unambiguous_dna_letters:
                dn[sb1 + sb2] = 0.0

        for i in xrange(len(self)):
            if not self.circular and (i + 1) >= len(self):
                continue

            ip = (i + 1) % len(self)
            if osb and (self[i] not in Data.IUPACData.unambiguous_dna_letters or self[ip] not in Data.IUPACData.unambiguous_dna_letters):
                continue
            if not self[i] + self[ip] in dn:
                dn[self[i] + self[ip]] = 0.0
            dn[self[i] + self[ip]] += 1.0
        return dn

    def dinucleotide_frequency(self, osb=True):
        """
        get the dinucleotide count of the sequence
        \param osb if true consider only standard bases (ATCG)
        \return a dictionary containing the frequencies
        """
        dn = self.dinucleotide_count(osb)
        if self.circular:
            sum = len(self)
        else:
            sum = len(self) - 1

        for k in dn:

            dn[k] /= float(sum)

        return dn

    def nucleotide_count(self, osb=True):
        """
        count the number of occurences of a,t,c,g,...
        @param osb iff true only count unambigous dna letters (ATGC)
        """

        nc = {}
        for sb in Data.IUPACData.unambiguous_dna_letters:
            nc[sb] = 0.0

        for i in xrange(len(self)):
            if osb and (self[i] not in Data.IUPACData.unambiguous_dna_letters):
                continue
            if not self[i] in nc:
                nc[self[i]] = 0.0
            nc[self[i]] += 1.0
            # print "x", self[i]
        return nc

    def nucleotide_frequency(self, osb=True):
        """
        get the frequency of the nucleotides in the sequence
        """
        nc = self.nucleotide_count(osb)
        sum = len(self)
        for k in nc:
            try:
                nc[k] /= float(sum)
            except ZeroDivisionError:
                nc[k] = 0.0

        return nc

    def shuffle(self):
        """
        random shuffle the sequence 
        """
        tdata = [x for x in self.data]
        shuffle(tdata)
        self.data = "".join(tdata)

    def subseq(self, start, stop, strand):
        """
        get the subsequence between start and stop
        note: subsequences are always linear

        @param start start index, note counting starts at 0
        @param stop end index, note element at the stop index is included in the sequence  
        @param strand +1/-1 get the reverse complement of the sequence if -1 and the sequence if 1 
        """

        if strand != 1 and strand != -1:
            #            stderr.write( "Strans" )
            raise Exception("StrandError", "strand is", strand)

        if not self.circular and (start < 0 or stop < 0):
            stderr.write("error: [%d,%d] of linear sequence\n" % (start, stop))

        while start < 0 or stop < 0:
            start += len(self)
            stop += len(self)

        if self.circular and start > len(self):
            start %= len(self)
        if self.circular and stop > len(self):
            stop %= len(self)

        if start <= stop:
            seq = self.__class__(
                str(self[start:stop + 1]), self.alphabet, circular=False)
#            seq = self.__class__( self.data[start:stop + 1], self.alphabet, circular = False )
        else:
            if self.circular:
                seq = self.__class__(
                    str(self[start:] + self[:stop + 1]), self.alphabet, circular=False)
#                seq = self.__class__( self.data[start:] + self.data[:stop + 1], self.alphabet, circular = False )
            else:
                stderr.write(
                    "error: [%d,%d] of linear sequence\n" % (start, stop))

        if strand == -1:
            seq = seq.reverse_complement()
            # @TODO crude fix .. biopython 1.49 complement function returns Seq not sequence
            seq = self.__class__(str(seq), self.alphabet, circular=False)

        return seq

    def start_stop_subsequence(self, transl_table, max=False):
        """
        get (start,stop, strand) tuples of the sequence such that at start is a 
        start codon and at end a end codon
        \param transl_table the id of the translation table
        \param max only return maximal sequences, i.e. if there are two sequences 
        (s1,e) and (s2,e) with s1<s2 then only (s1,e) will be returned
        \todo subsequences crossing the 0 .. attention the reading frame calculations 
        get tricky
        """

        ret = []
        table = Data.CodonTable.unambiguous_dna_by_id[transl_table]

        # print table

        start_codons = table.start_codons
        stop_codons = table.stop_codons

        # first +strand
        stack = [[], [], []]
        for i in range(len(self) - 2):
            subs = str(self.subseq(i, i + 3, 1))
            if subs in start_codons:
                stack[i % 3].append(i)
            elif subs in stop_codons:
                for s in stack[i % 3]:
                    ret.append((s, (i + 2) % len(self), 1))
                    if max:
                        break

                stack[i % 3] = []

        # first -strand
        if self.circular == False:
            return ret

        stack = [[], [], []]
        for i in range(len(self) - 1, -1, -1):
            subs = str(self.subseq(i, i + 3, -1))

            if subs in start_codons:
                stack[i % 3].append(i)

            if subs in stop_codons:
                for s in stack[i % 3]:
                    ret.append(((i + 2) % len(self), s, -1))
                    if max:
                        break
                stack[i % 3] = []

        return ret

    def deambig(self):
        """
        return a list of sequences 
        """
        # print "deambig"
        if self.alphabet == Alphabet.IUPAC.ambiguous_dna or self.alphabet == Alphabet.IUPAC.unambiguous_dna:
            # print "dna"
            ambiguous_nucleotide_values = Data.IUPACData.ambiguous_dna_values
            unambiguous_alph = Alphabet.IUPAC.unambiguous_dna
        elif self.alphabet == Alphabet.IUPAC.ambiguous_rna or self.alphabet == Alphabet.IUPAC.unambiguous_rna:
            # print "rna"
            ambiguous_nucleotide_values = Data.IUPACData.ambiguous_rna_values
            unambiguous_alph = Alphabet.IUPAC.unambiguous_rna
        else:
            # print self.alphabet
            return [sequence(str(self), self.alphabet, False)]
        # print
        # print(self.data)

        c1, c2, c3 = self.data
        x1 = ambiguous_nucleotide_values[c1]
        x2 = ambiguous_nucleotide_values[c2]
        x3 = ambiguous_nucleotide_values[c3]
        # print "DA", self.data, x1,x2,x3
        da = []
        for y1 in x1:
            for y2 in x2:
                for y3 in x3:
                    da.append(y1 + y2 + y3)

        return da

    def heavyStrand(self):
        return float(self.count("A") + self.count("G")) / len(self) >= 0.5


class randsequence(sequence):

    def __init__(self, length, alphabet=Alphabet.IUPAC.IUPACUnambiguousDNA(), circular=False):
        """
        generate a random sequence of a certain alphabet
        \param length how long should the sequence be
        \param alphabet which alphabet 
        \param circular init as circular
        """
        data = []
        for i in xrange(length):
            data.append(
                alphabet.letters[randint(0, len(alphabet.letters) - 1)])
        data = "".join(data).strip().upper()
        sequence.__init__(self, data, alphabet, circular)


def sequences_fromfilehandle(handle, alphabet=ambiguous_dna, circular=False):

    seq = []
    for seq_record in SeqIO.parse(handle, "fasta"):
        #        print seq_record
        #        print dir(seq_record)
        #        print 'annotations', seq_record.annotations
        #        print 'dbxrefs', seq_record.dbxrefs
        #        print 'description' , seq_record.description
        #        print 'features', seq_record.features
        #        print 'format', seq_record.format
        #        print 'id', seq_record.id
        #        print 'name', seq_record.nameSeqIO
        seq.append(sequence(str(seq_record.seq), alphabet, circular=circular))
        # print seq[-1]

    return seq


def sequences_fromfile(fname, alphabet=ambiguous_dna, circular=False):
    """
    get a list of sequences found in a fasta file
    """
    handle = open(fname, "r")
    seq = sequences_fromfilehandle(handle, alphabet, circular)
    handle.close()
    return seq


def sequence_info_fromfilehandle(handle, alphabet=ambiguous_dna, circular=False):

    seq = []
    for seq_record in SeqIO.parse(handle, "fasta"):
        #        raise Exception( str( seq_record ) )
        #        print dir(seq_record)
        #        print 'annotations', seq_record.annotations
        #        print 'dbxrefs', seq_record.dbxrefs
        #        print 'description' , seq_record.description
        #        print 'features', seq_record.features
        #        print 'format', seq_record.format
        #        print 'id', seq_record.id
        #        print 'name', seq_record.name
        seq.append({'name': seq_record.name.strip(),
                    'description': seq_record.description.strip(),
                    'sequence': sequence(str(seq_record.seq), alphabet, circular=circular),
                    'id': seq_record.id})
        # print seq[-1]

    return seq


def sequence_info_fromfile(fname, alphabet=ambiguous_dna, circular=False):
    """
    get a list of sequences and their names found in a fasta file
    """

    handle = open(fname, "r")
    seq = sequence_info_fromfilehandle(handle, alphabet, circular)
    handle.close()

    return seq


def seqlistmaker(sequence, start, stop, strand, acc, name="", code=None, seqlist=[]):
    """
    @param sequence the whole sequence where the part is from. (Bio.Seq.Seq format)
    @param start the start of the part
    @param stop the stop of the part
    @param acc the acc of the species
    @param name the name of the part if ther is a name.
    @param code translate with code, do not translate if None 
    @param seqlist A list of sequences, online needet if this sequenz is only a part of bigger list.

    This method cut a part of a big sequence and append it in a list.
    It is needed for a fasta writing with parts of genoms.
    """

    if int(strand) == 1:
        ts = "+"
    else:
        ts = "-"

    # header with or without a name; coordinates as in gff
    out = "{acc}; {start}-{stop}; {strand}; {name}".format(
        acc=acc, start=start + 1, stop=stop + 1, strand=ts, name=name)
#     out += "%s: %d-%d" % ( acc, start + 1, stop + 1 )
#     if int( strand ) == 1:
#         out += "+"
#     else:
#         out += "-"
#
#     if name != "":
#         out += "; %s" % ( name )

    # set the subsequnc, need a Bio.Seq.Seq format
    mito_frag = sequence.subseq(start, stop, int(strand))

    if code != None:
        mito_frag = mito_frag.translate(table=code)

    # Set record with header
    record = SeqRecord(mito_frag, out, '', '')

    seqlist.append(record)
    return seqlist


def fastawriter(featurelist, sequence, code, acc, outputtype, outfile=None, mode="w"):
    """
    @param outputtype fas / faa
    """
    featurelist.sort(key=lambda x: x.start)
    seqlist = []
    for feat in featurelist:
        if outputtype == "faa" and feat.type != "gene":
            continue

        seqlistmaker(sequence=sequence, acc=acc, start=feat.start, stop=feat.stop,
                     strand=feat.strand, name=feat.outputname(), code=code, seqlist=seqlist)

    if isinstance(outfile, str):
        file = open(outfile, mode)
        SeqIO.write(seqlist, file, "fasta")
        file.close()

    elif outfile == None:
        SeqIO.write(seqlist, stdout, "fasta")
    else:
        SeqIO.write(seqlist, outfile, "fasta")

# def fastareader( lines ):
#    """
#    read a single fasta sequence from lines of text
#    should contain a single sequence .. otherwise exception
#
#    """
#
#    header = None
#    seq = ""
#    for line in lines:
#        if line.startswith( ">" ):
#            if header == None:
#                header = line[1:].strip()
#            else:
#                raise MultiFastaException()
#        elif header != None:
#            line = line.upper().strip()
#            if len( line ) > 0:
#                if line[0] in Alphabet.IUPAC.IUPACAmbiguousDNA().letters:
#                    seq += line
#                elif line[0] == "-":
#                    break
#                else:
#                    raise AlphabetException( line, Alphabet.IUPAC.IUPACAmbiguousDNA() )
# #            else:
# #                break
#    if header == None:
#        raise NoFastaException()
#
#    header = header.replace( "|", "_" )
#
#    seq = sequence( seq )
#    return header, seq
