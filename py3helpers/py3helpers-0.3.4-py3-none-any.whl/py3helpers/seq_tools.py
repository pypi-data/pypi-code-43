#!/usr/bin/env python
"""Utility functions for fasta, fastq and mapping reads"""
########################################################################
# File: seq_tools.py
#  executable: seq_tools.py
#
# Author: Andrew Bailey
# History: 02/15/18 Created
########################################################################

import sys
import numpy as np
import os
import mappy as mp
import re
import tempfile
from collections import Counter, namedtuple

from Bio.Seq import Seq
from Bio import pairwise2, SeqIO
from Bio.pairwise2 import format_alignment
from pysam import FastaFile, AlignmentFile, AlignedSegment, AlignmentHeader
from py3helpers.utils import merge_two_dicts, split_every_string

IUPAC_BASES = ("A", "C", "T", "G", "W", "R", "Y", "S", "K", "M", "B", "D", "H", "V", "N")
IUPAC_DICT = {"A": "A",
              "C": "C",
              "T": "T",
              "G": "G",
              "W": ["A", "T"],
              "R": ["A", "G"],
              "Y": ["C", "T"],
              "S": ["G", "C"],
              "K": ["G", "T"],
              "M": ["A", "C"],
              "B": ["C", "G", "T"],
              "D": ["A", "G", "T"],
              "H": ["A", "C", "T"],
              "V": ["A", "C", "G"],
              "N": "N"}

IUPAC_COMPLEMENTS = {"A": "T",
                     "C": "G",
                     "T": "A",
                     "G": "C",
                     "W": "W",
                     "R": "Y",
                     "Y": "R",
                     "S": "S",
                     "K": "M",
                     "M": "K",
                     "B": "V",
                     "D": "H",
                     "H": "D",
                     "V": "B",
                     "N": "N"}


def read_fasta(fasta, upper=True):
    """
    Taken from David Bernick but modified slightly to fit my purposes.

    using filename given in init, returns each included FastA record
    as 2 strings - header and sequence.
    whitespace is removed, no adjustment is made to sequence contents.
    The initial '>' is removed from the header.


    :param fasta: path to fasta file
    :param upper: boolean option to convert strings to uppercase
    :return: generator yielding header, sequence
    """
    assert fasta.endswith(".fa") or fasta.endswith(".fasta"), "Did not receive fasta file: {}".format(fasta)

    # initialize return containers

    def upperstring(line):
        return ''.join(line.rstrip().split()).upper()

    def lowerstring(line):
        return ''.join(line.rstrip().split())

    if upper:
        funct = upperstring
    else:
        funct = lowerstring

    sequence = ''
    with open(fasta, 'r+') as fasta_f:
        # skip to first fasta header
        line = fasta_f.readline()
        while not line.startswith('>'):
            line = fasta_f.readline()
        header = line[1:].rstrip()

        # header is saved, get the rest of the sequence
        # up until the next header is found
        # then yield the results and wait for the next call.
        # next call will resume at the yield point
        # which is where we have the next header
        for line in fasta_f:
            if line.startswith('>'):
                yield header, sequence
                # headerList.append(header)
                # sequenceList.append(sequence)
                header = line[1:].rstrip()
                sequence = ''
            else:
                sequence += funct(line)
        # final header and sequence will be seen with an end of file
        # with clause will terminate, so we do the final yield of the data

    yield header, sequence


def get_minimap_cigar(genome, sequence, preset='map-ont', cigar_string=True):
    """Get the alignment between a genome and alignment file

    :param genome: fasta file to genome
    :param sequence: sequence to align
    :param preset: sr for single-end short reads;
                   map-pb for PacBio read-to-reference mapping;
                   map-ont for Oxford Nanopore read mapping;
                   splice for long-read spliced alignment;
                   asm5 for assembly-to-assembly alignment;
                   asm10 for full genome alignment of closely related species.
    :param cigar_string: if True return normal cigar string, if false return array of shape (n_cigar, 2)
                        The two numbers give the length and the operator of each CIGAR operation.

    """
    assert os.path.exists(genome), "Genome path does not exist: {}".format(genome)
    assert preset in ["sr", "map-pb", "map-ont", "splice", "asm5", "asm10"]
    assert len(sequence) > 60, "minimap does not find alignments for small reads"
    a = mp.Aligner(genome, preset=preset)  # load or build index
    if not a:
        raise Exception("ERROR: failed to load/build index")
    for hit in a.map(sequence):
        if hit.is_primary:
            print(hit)
            if cigar_string:
                return str(hit.cigar_str)
            else:
                return hit.cigar


def get_minimap_alignment(genome, sequence, preset='map-ont'):
    """Get the alignment between a genome and alignment file

    :param genome: fasta file to genome
    :param sequence: sequence to align
    :param preset: sr for single-end short reads;
                   map-pb for PacBio read-to-reference mapping;
                   map-ont for Oxford Nanopore read mapping;
                   splice for long-read spliced alignment;
                   asm5 for assembly-to-assembly alignment;
                   asm10 for full genome alignment of closely related species.
    """
    assert os.path.exists(genome), "Genome path does not exist: {}".format(genome)
    assert preset in ["sr", "map-pb", "map-ont", "splice", "asm5", "asm10"]
    assert len(sequence) > 60, "minimap does not find alignments for small reads"
    a = mp.Aligner(genome, preset=preset)  # load or build index
    if not a:
        raise Exception("ERROR: failed to load/build index")
    for hit in a.map(sequence):
        if hit.is_primary:
            return hit


def create_pairwise_alignment(ref=None, query=None, local=False):
    """Generate alignment from two strings
    :param ref: string for reference squence
    :param query: string for query sequence
    :param local: if true do local alignment else do global
    :return: dictionary with 'reference' and 'query' accessible alignment sequences
    """
    assert ref is not None, "Must set reference sequence"
    assert query is not None, "Must set query sequence"
    if local:
        alignments = pairwise2.align.localms(ref.upper(), query.upper(), 2, -0.5, -1, -0.3,
                                             one_alignment_only=True)

    else:
        alignments = pairwise2.align.globalms(ref.upper(), query.upper(), 2, -0.5, -1, -0.3,
                                              one_alignment_only=True)
    # print(format_alignment(*alignments[0]))
    return {'reference': alignments[0][0], 'query': alignments[0][1]}


def get_pairwise_cigar(ref=None, query=None, local=False):
    """Generate alignment from two strings
    :param ref: string for reference squence
    :param query: string for query sequence
    :param local: bool for local or global alignment
    """
    assert ref is not None, "Must set reference sequence"
    assert query is not None, "Must set query sequence"

    alignment = create_pairwise_alignment(ref=ref, query=query, local=local)
    final_str = str()
    # CIGAR = {"M": 0, "I": 0, "D": 0, "N": 0, "S": 0, "H": 0, "P": 0, "=": 0, "X": 0}
    current = str()
    count = 0
    for ref, query in zip(alignment['reference'], alignment["query"]):
        if ref == query:
            # matches
            if current == "M":
                count += 1
                current = "M"
            else:
                final_str += str(count) + current
                current = "M"
                count = 1
        elif ref == '-':
            # soft clipped sequences
            if current == "S":
                count += 1
                current = "S"
            elif current == str():
                final_str += str(count) + current
                current = "S"
                count = 1
            # insertions
            elif current == "I":
                count += 1
                current = "I"
            else:
                final_str += str(count) + current
                current = "I"
                count = 1
        elif query == '-':
            # deletions
            if current == "D":
                count += 1
                current = "D"
            else:
                final_str += str(count) + current
                current = "D"
                count = 1
        else:
            # mismatches
            if current == "X":
                count += 1
                current = "X"
            else:
                final_str += str(count) + current
                current = "X"
                count = 1
    if current == "I":
        final_str += str(count) + "S"
    else:
        final_str += str(count) + current
    # remove initial zero
    return final_str[1:]


def cigar_conversion(cigar):
    """Convert character or integer to corresponding integer or character for the SAM/BAM formatting
    :param cigar: character or int to get corresponding CIGAR equivalent
    """
    assert type(cigar) is str or type(cigar) is int, "Cigar character must be int or str"
    chars = ["M", "I", "D", "N", "S", "H", "P", "=", "X"]

    if type(cigar) is str:
        assert cigar in chars, "Character is not a cigar string character"
        return chars.index(cigar)
    else:
        assert 0 <= cigar <= 8, "Integer must be between 0 and 8"
        return chars[cigar]


class ReverseComplement(object):
    """Class to deal with reverse, complement and reverse-complement sequences"""

    def __init__(self, find="ATGC", replace="TACG"):
        """Set find and replace characters. Entire class will turn everything into upper case

        :param find: strings to find then replace with replace
        :param replace: string which replaces the corresponding index of parameter find
        """
        assert len(find) == len(set(find)), "No repeats allowed in param 'find': {}".format(find)
        assert len(replace) == len(set(replace)), "No repeats allowed in param 'replace': {}".format(replace)
        assert len(find) == len(replace), "Length of 'find' must match 'replace': len({}) != len({})".format(find,
                                                                                                             replace)
        self.find = find.upper()
        self.replace = replace.upper()
        self.transtab = str.maketrans(self.find, self.replace)

    def complement(self, string):
        """Generate complement sequence"""
        return string.upper().translate(self.transtab)

    @staticmethod
    def reverse(string):
        """Reverse string sequence"""
        return string.upper()[::-1]

    def reverse_complement(self, string):
        """Reverse complement string from transtable"""
        string = self.reverse(string)
        return self.complement(string)

    def convert_write_fasta(self, in_fasta, outpath, complement=True, reverse=True):
        """Write new fasta file to outpath while adding info to header names

        :param reverse: boolean option for reverse direction of string
        :param complement: boolean option for complement of string
        :param in_fasta: input fasta file
        :param outpath: path to output fasta """
        assert outpath.endswith(".fa") or outpath.endswith(".fasta"), "Output file needs to end with .fa or .fasta"
        assert os.path.isfile(in_fasta), "If fasta is selected, sequence must be a real path"
        assert complement or reverse is True, "Must select complement or reverse"

        # choose function and information to add to header
        if complement and not reverse:
            funct = self.complement
            add_to_header = "_complement"
        elif reverse and not complement:
            funct = self.reverse
            add_to_header = "_reverse"
        elif complement and reverse:
            funct = self.reverse_complement
            add_to_header = "_reverse_complement"
        # write to fasta file
        with open(outpath, 'w+') as out_fa:
            for header, sequence in read_fasta(in_fasta):
                out_fa.write('>' + header + add_to_header + '\n')
                for sub_seq in split_every_string(80, funct(sequence)):
                    out_fa.write(sub_seq + '\n')
        return outpath

    def convert_write_fastq(self, in_fastq, outpath, complement=True, reverse=True):
        """Write new fastq file to outpath while adding info to header names

        :param reverse: boolean option for reverse direction of string
        :param complement: boolean option for complement of string
        :param in_fastq: input fastq file
        :param outpath: path to output fastq """
        assert outpath.endswith(".fq") or outpath.endswith(".fastq"), \
            "Output file needs to end with .fq or .fastq: {}".format(outpath)
        assert os.path.isfile(in_fastq), "If fastq is selected, sequence must be a real path: {}".format(in_fastq)
        assert complement or reverse is True, "Must select complement and/or reverse"

        # choose function and information to add to header
        if complement and not reverse:
            funct = self.complement
            add_to_header = "_complement"
        elif reverse and not complement:
            funct = self.reverse
            add_to_header = "_reverse"
        elif complement and reverse:
            funct = self.reverse_complement
            add_to_header = "_reverse_complement"
        # write to fastq file
        reads = []
        for record in SeqIO.parse(in_fastq, "fastq"):
            record.id = record.id + add_to_header
            record.seq = Seq(funct(str(record.seq)))
            if reverse:
                record.letter_annotations["phred_quality"] = record.letter_annotations["phred_quality"][::-1]
            reads.append(record)
        SeqIO.write(reads, outpath, "fastq")
        return outpath


def write_fasta(header_sequence_dict, outpath):
    """Write header and sequence with correct fasta formatting. Sequence converted to uppercase

    :param header_sequence_dict: dict of header with sequence
    :param outpath: path to file ending in .fa or .fasta
    """
    assert outpath.endswith(".fa") or outpath.endswith(".fasta"), "Output file needs to end with .fa or .fasta"
    assert type(header_sequence_dict) is dict, "header_sequence_dict needs to be a dictionary"

    with open(outpath, 'w+') as out_fa:
        for header, sequence in header_sequence_dict.items():
            out_fa.write('>' + header + '\n')
            for subset in split_every_string(80, sequence.upper()):
                out_fa.write(subset + '\n')


def check_fastq_line(fastq):
    """Check if fastq string has some necessary features of the fasta format.

    :param fastq: single string with a record of fastq """

    check = fastq.split('\n')
    assert len(check) == 4, "Data is not fastq format: Not enough fields"
    assert check[0].startswith('@'), "Data is not fastq format: Does not start with @"
    assert len(check[1]) == len(check[3]), "Data is not fastq format: Sequence and quality scores do not match"
    assert check[2].startswith('+'), "Data is not fastq format: third line does not start with +"
    return True


def create_fastq_line(read_id, sequence, q_values):
    """Create a fastq string from the necessary fields. Do not include newlines!

    :param read_id: unique identifier for read
    :param sequence: sequence of nucleotides
    :param q_values: quality score values associated with the sequence
    """
    # make sure we have not included newline characters
    assert read_id.find("\n") == -1, "Remove newline characterss from read_id"
    assert sequence.find("\n") == -1, "Remove newline characters from sequence"
    assert q_values.find("\n") == -1, "Remove newline characters from q_values"
    assert len(sequence) == len(q_values), "sequence and q_values must to be the same size"

    if not read_id.startswith("@"):
        read_id = '@' + read_id
    line1 = read_id + "\n"
    line2 = sequence + "\n"
    line3 = "+\n"
    fastq = line1 + line2 + line3 + q_values
    return fastq


class SeqAlignment(object):
    """Keep track of alignment accuracy statistics from two sequences and a cigar string"""
    CIGAR = ["M", "I", "D", "N", "S", "H", "P", "=", "X"]

    # S= soft clip (ignore)
    # H = Hard clip (ignore)
    # N = ignore length for splice assignments (ignore)
    # P = padded reference (ignore)
    # M = Match
    # I = Insertion
    # D = Deletion
    # = = match
    # X = Mismatch

    def __init__(self, query, ref, cigar):
        """Initialize summary accuracy information from a cigar alignment

        :param query: query sequence (can be soft padded)
        :param ref: reference sequence (only aligned part)
        :param cigar: cigar string
        """
        self.query = query.upper()
        self.ref = ref.upper()
        self.cigar = cigar
        # contains alignment for each base in the query and reference positions
        self.query_map = []
        self.ref_map = []
        # contains the entire alignment and true matches mapping
        # full_alignment contains soft clipped sections
        self.full_alignment_map = []
        # alignment map does not contain clipped regions
        self.alignment_map = []
        self.true_matches_map = []
        self.matches_map = []
        # each key h
        self.base_alignment = namedtuple('base_alignment',
                                         ['query_index', 'query_base', 'reference_index', 'reference_base'])
        self.alphabet = set(self.ref + self.query)
        # self.totals = namedtuple('totals', ['matches', 'inserts', 'deletes', 'clipped', 'mismatch])

        self.counts = {char: [0, 0, 0, 0, 0] for char in self.alphabet}
        assert self._initialize()

    def _initialize(self):
        """Get percent of identically matched bases over the alignment length"""
        cigar_chars = set(''.join([i for i in self.cigar if not i.isdigit()]))
        assert cigar_chars.issubset(self.CIGAR), \
            "Cigar contains extraneous characters. Only 'MIDNSHP=X' allowed. {}".format(cigar_chars)
        # track indexes
        query_index = 0
        ref_index = 0
        total_len = 0
        # go through cigar
        for num, cigar_char in re.findall('(\d+)([MIDNSHP=X])', self.cigar):
            num = int(num)
            total_len += num
            # map bases to reference
            for x in range(num):
                if cigar_char == "M" or cigar_char == "=" or cigar_char == "X":
                    # matches and mismatches
                    align = self.base_alignment(query_index, self.query[query_index],
                                                ref_index, self.ref[ref_index])
                    # consumes both
                    self.query_map.append(align)
                    self.ref_map.append(align)
                    self.alignment_map.append(align)
                    self.full_alignment_map.append(align)
                    self.matches_map.append(align)
                    if self.ref[ref_index] == self.query[query_index]:
                        self.true_matches_map.append(align)
                        self.counts[self.query[query_index]][0] += 1
                    else:
                        self.counts[self.query[query_index]][4] += 1

                    query_index += 1
                    ref_index += 1
                elif cigar_char == "S" or cigar_char == "I":
                    # skips and inserts
                    align = self.base_alignment(query_index, self.query[query_index],
                                                None, None, )
                    # consumes query
                    self.query_map.append(align)
                    if cigar_char != "S":
                        self.alignment_map.append(align)
                        self.counts[self.query[query_index]][3] += 1
                    else:
                        self.counts[self.query[query_index]][1] += 1

                    self.full_alignment_map.append(align)
                    query_index += 1
                elif cigar_char == "D" or cigar_char == "N":
                    # skipped regions for splice assignments so not used for alignment length but is used for ref length
                    align = self.base_alignment(None, None,
                                                ref_index, self.ref[ref_index])
                    # consumes reference
                    self.ref_map.append(align)
                    self.alignment_map.append(align)
                    self.full_alignment_map.append(align)
                    if cigar_char == "D":
                        self.counts[self.ref[ref_index]][2] += 1
                    ref_index += 1
                elif cigar_char == "P":
                    # currently passing
                    pass

        assert len(self.full_alignment_map) == total_len, "Full alignment map does not match cigar length. Check inputs"
        assert len(self.ref_map) == len(self.ref), "Ref map does not match ref seq. map: {} != ref_len: {}" \
            .format(len(self.ref_map), len(self.ref))
        assert len(self.query_map) == len(self.query), "Query map does not match query seq. map: {} != query_len: {}" \
            .format(len(self.query_map), len(self.query))

        return True

    def alignment_accuracy(self, soft_clip=False):
        """Get percent accuracy from cigar string

        :param soft_clip: boolean include soft clip in accuracy calculation
        """
        if soft_clip:
            acc = float(len(self.true_matches_map)) / len(self.full_alignment_map)
        else:
            acc = float(len(self.true_matches_map)) / len(self.alignment_map)

        return acc


class Cigar(object):
    """Cigar string object to handle cigar strings"""
    CIGAR = ["M", "I", "D", "N", "S", "H", "P", "=", "X"]

    # S= soft clip (ignore)
    # H = Hard clip (ignore)
    # N = ignore length for splice assignments (ignore)
    # P = padded reference (ignore)
    # M = Match
    # I = Insertion
    # D = Deletion
    # = = match
    # X = Mismatch

    def __init__(self, cigar):
        """Get some basic info from a cigar string

        :param cigar: cigar string
        """
        self.cigar = cigar
        self.ref_len = 0
        self.query_len = 0
        self.alignment_length = 0
        self.alignment_length_soft_clipped = 0
        self.matches = 0
        self.indexed_cigar = []
        self._initialize()

    def _initialize(self):
        """Initialize important information from cigar string"""
        cigar_chars = set(''.join([i for i in self.cigar if not i.isdigit()]))
        assert cigar_chars.issubset(
            self.CIGAR), "Cigar contains extraneous characters. Only 'MIDNSHP=X' allowed. {}".format(cigar_chars)
        soft_clipped = 0
        for num, char in re.findall('(\d+)([MIDNSHP=X])', self.cigar):
            num = int(num)
            if char == "M" or char == "=":
                self.matches += num
                self.alignment_length += num
                self.ref_len += num
                self.query_len += num
                self.indexed_cigar.extend(["M" for _ in range(num)])
            elif char == "X":
                self.alignment_length += num
                self.ref_len += num
                self.query_len += num
                self.indexed_cigar.extend(["X" for _ in range(num)])
            elif char == "S":
                self.query_len += num
                soft_clipped += num
                self.indexed_cigar.extend(["S" for _ in range(num)])
            elif char == "I":
                self.query_len += num
                self.alignment_length += num
                self.indexed_cigar.extend(["I" for _ in range(num)])
            elif char == "D":
                self.ref_len += num
                self.alignment_length += num
                self.indexed_cigar.extend(["D" for _ in range(num)])
            elif char == "N":
                # skipped regions for splice assignments so not used for alignment length but is used for ref length
                self.ref_len += num
                self.indexed_cigar.extend(["N" for _ in range(num)])
            elif char == "P":
                self.indexed_cigar.extend(["P" for _ in range(num)])
                # do nothing for padded regions
                pass

        self.alignment_length_soft_clipped = self.alignment_length + soft_clipped

    def accuracy_from_cigar(self, soft_clip=False):
        """Get percent accuracy from cigar string

        :param soft_clip: boolean include soft clip in accuracy calculation
        """
        if soft_clip:
            acc = float(self.matches) / self.alignment_length_soft_clipped
        else:
            acc = float(self.matches) / self.alignment_length

        return acc

    def reverse_cigar(self):
        """Reverse cigar sequence"""
        reversed_cigar = self.indexed_cigar[::-1]
        new_cigar = ""
        prev_char = reversed_cigar[0]
        counter = 1
        for x in reversed_cigar[1:]:
            if x == prev_char:
                counter += 1
            else:
                new_cigar += str(counter) + prev_char
                prev_char = x
                counter = 1
        new_cigar += str(counter) + prev_char
        return new_cigar


def pairwise_alignment_accuracy(ref=None, query=None, local=False, soft_clip=False):
    """Get accuracy from pairwise alignment of two sequences

    :param ref: string 1 to treat as reference
    :param query: string 2 to treat as query
    :param local: boolean for local or global alignment
    :param soft_clip: boolean option for including soft_clipped regions for accuracy
    """
    # complete pairwise alignment and generate cigar string
    assert ref is not None, "Must set reference sequence"
    assert query is not None, "Must set query sequence"
    cigar = get_pairwise_cigar(ref, query, local=local)
    accuracy = Cigar(cigar).accuracy_from_cigar(soft_clip=soft_clip)
    return accuracy


class ReferenceHandler:
    """
    This class handles fasta reference files, ensuring that the sequence is not a terminal 'N' and that the end of the
    sequence has not been reached
    """

    def __init__(self, reference_file_path):
        """
        create fasta file object given file path to a fasta reference file
        :param fasta_file_path: full path to a fasta reference file
        """

        self.fasta_file_path = reference_file_path
        assert os.path.exists(reference_file_path), "Reference path does not exist: {}".format(reference_file_path)
        try:
            self.fasta = FastaFile(self.fasta_file_path)
        except Exception as e:
            print(e)
            raise IOError("Fasta File Read Error: Try indexing reference with 'samtools faidx {}'"
                          .format(reference_file_path))

    def get_sequence(self, chromosome_name, start, stop):
        """
        Return the sequence of a chromosome region by zero based indexing: chr[start:stop]

        :param chromosome_name: Chromosome name
        :param start: Region start index
        :param stop: Region end, one more than last index
        :return: Sequence of the region
        """
        return self.fasta.fetch(reference=chromosome_name, start=start, end=stop).upper()

    def get_chr_sequence_length(self, chromosome_name):
        """
        Get sequence length of a chromosome. This is used for selecting windows of parallel processing.
        :param chromosome_name: Chromosome name
        :return: Length of the chromosome reference sequence
        """
        return self.fasta.get_reference_length(chromosome_name)

    def write_new_reference(self, outpath, reverse=False, complement=False, find="ATGC", replace="TACG"):
        """Write a new reference sequence file to a given directory with options of reverse and/or complement the strand

        ex... directory = '/home/name/dir/', reverse=True, complement=True
              return = /home/name/dir/reference.reverse.complement.fa

        :param outpath: path to directory
        :param reverse: bool option to reverse sequence
        :param complement: bool option to complement sequence
        :param find: strings to find then replace with replace
        :param replace: string which replaces the corresponding index of parameter find
        :return: path to file if pass otherwise False
        """
        # get original fasta name
        fasta_name = os.path.splitext(os.path.basename(self.fasta_file_path))[0]
        # edit fasta name
        if reverse:
            fasta_name += '.reverse'
        if complement:
            fasta_name += '.complement'
        fasta_name += '.fa'
        # create outpath
        outpath = os.path.join(outpath, fasta_name)
        # write fasta with edits
        ReverseComplement(find=find, replace=replace).convert_write_fasta(self.fasta_file_path, outpath,
                                                                          complement=complement, reverse=reverse)
        return outpath


def initialize_pysam_wrapper(sam_file_string, reference_path=None):
    """Create a temp file to initialize the pysam wrapper class
    :param sam_file_string: correctly formatted SAM alignment string
    :param reference_path: path to reference file
    """
    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "test.sam")
        with open(path, "w") as tmp:
            tmp.write(sam_file_string)
        try:
            pysam_handle = PysamWrapper(path)
            pysam_handle.initialize(reference_path)
            return pysam_handle
        except StopIteration:
            raise ValueError("sam_file_string is not in SAM format")


class PysamWrapper(AlignmentFile):
    """Use pysam AlignmentFile functions for a string sam entry"""

    def __init__(self, path):
        """Create wrapper for pysam to deal with single alignment sam files

        :param path: path to temp single alignment sam file

        """
        try:
            self.alignment_segment = self.fetch().__next__()
        except OSError:
            raise OSError("Check SAM cigar/ MDZ field formatting. Truncated File error")
        self.reference_path = None
        self.seq_alignment = None
        self.initialized = False

    def initialize(self, reference_path=None):
        """Initialization function for Pysam Wrapper class

        Since AlignmentFile is in Cython, could not get the inheritance to work correctly

        :param reference_path: path to reference genome
        """
        self.reference_path = reference_path
        self.seq_alignment = SeqAlignment(cigar=self.get_cigar(),
                                          ref=self.get_reference_sequence(),
                                          query=self.alignment_segment.get_forward_sequence())
        self.initialized = True

    def get_reference_sequence(self):
        """Get reference sequence from sequence position. Will reverse if alignment is to reverse strand"""
        if not self.alignment_segment.has_tag('MD'):
            assert self.reference_path is not None, "Need to designate reference path if MD:Z field is not defined"
            fasta_handle = ReferenceHandler(self.reference_path)
            ref_sequence = fasta_handle.get_sequence(chromosome_name=self.alignment_segment.reference_name,
                                                     start=self.alignment_segment.reference_start,
                                                     stop=self.alignment_segment.reference_end)
        else:
            ref_sequence = self.alignment_segment.get_reference_sequence().upper()

        if self.alignment_segment.is_reverse:
            ref_sequence = ReverseComplement().reverse_complement(ref_sequence)

        return ref_sequence

    def get_cigar(self):
        """Get cigar string. Will reverse if alignment is to reverse strand"""
        cigar = self.alignment_segment.cigarstring
        # deal with reversed alignment
        if self.alignment_segment.is_reverse:
            cigar = Cigar(cigar).reverse_cigar()
        return cigar

    def alignment_accuracy(self, soft_clip=False):
        """Get alignment accuracy
        :param soft_clip: boolean include soft clip in accuracy calculation
        """
        return self.seq_alignment.alignment_accuracy(soft_clip=soft_clip)


class AlignmentSegmentWrapper(object):
    """Use pysam AlignmentSegment functions for a string sam entry"""

    def __init__(self, aligned_segment):
        """Create wrapper for pysam to deal with single alignment sam files

        :param aligned_segment: AlignmentSegment object

        """
        self.alignment_segment = aligned_segment
        self.reference_path = None
        self.seq_alignment = None
        self.initialized = False

    def initialize(self, reference_path=None):
        """Initialization function for Pysam Wrapper class

        Since AlignmentFile is in Cython, could not get the inheritance to work correctly

        :param reference_path: path to reference genome
        """
        self.reference_path = reference_path
        self.seq_alignment = SeqAlignment(cigar=self.get_cigar(),
                                          ref=self.get_reference_sequence(),
                                          query=self.alignment_segment.get_forward_sequence())
        self.initialized = True

    def get_reference_sequence(self):
        """Get reference sequence from sequence position. Will reverse if alignment is to reverse strand"""
        if not self.alignment_segment.has_tag('MD'):
            assert self.reference_path is not None, "Need to designate reference path if MD:Z field is not defined"
            fasta_handle = ReferenceHandler(self.reference_path)
            ref_sequence = fasta_handle.get_sequence(chromosome_name=self.alignment_segment.reference_name,
                                                     start=self.alignment_segment.reference_start,
                                                     stop=self.alignment_segment.reference_end)
        else:
            ref_sequence = self.alignment_segment.get_reference_sequence().upper()

        if self.alignment_segment.is_reverse:
            ref_sequence = ReverseComplement().reverse_complement(ref_sequence)

        return ref_sequence

    def get_cigar(self):
        """Get cigar string. Will reverse if alignment is to reverse strand"""
        cigar = self.alignment_segment.cigarstring
        # deal with reversed alignment
        if self.alignment_segment.is_reverse:
            cigar = Cigar(cigar).reverse_cigar()
        return cigar

    def alignment_accuracy(self, soft_clip=False):
        """Get alignment accuracy
        :param soft_clip: boolean include soft clip in accuracy calculation
        """
        return self.seq_alignment.alignment_accuracy(soft_clip=soft_clip)


def sam_string_to_aligned_segment(sam_string, header=None):
    """Convert a correctly formatted sam string into a pysam AlignedSegment object

    :param sam_string: correctly formatted SAM string
    :param header: AlignmentHeader object

    :return AlignedSegment
    """
    if not header:
        header = AlignmentHeader.from_references([sam_string.split("\t")[2]], [100000000])

    new_segment = AlignedSegment.fromstring(sam_string, header)

    return new_segment


def initialize_aligned_segment_wrapper(sam_string, reference_path=None):
    """Convert a correctly formatted sam string into a pysam AlignedSegment object

    :param sam_string: correctly formatted SAM string
    :param reference_path:

    :return AlignmentSegmentWrapper
    """

    segment = sam_string_to_aligned_segment(sam_string)
    as_wrapper = AlignmentSegmentWrapper(segment)
    as_wrapper.initialize(reference_path)
    return as_wrapper


def iupac_complement(nuc):
    """Return the complement character using IUPAC nucleotides"""
    nuc = nuc.upper()
    assert is_iupac_base(nuc), "Nucleotide is not IUPAC character"
    return IUPAC_COMPLEMENTS[nuc]


def iupac_base_to_bases(nuc):
    """Return the bases that are represented for a given iupac base"""
    nuc = nuc.upper()
    assert is_iupac_base(nuc), "Nucleotide is not IUPAC character"
    return IUPAC_DICT[nuc]


def is_iupac_base(nuc):
    """Returns True if an IUPAC base and False if not"""
    if nuc.upper() in IUPAC_BASES:
        return True
    else:
        return False


def is_non_canonical_iupac_base(nuc):
    """Return True if base is one of teh IUPAC bases but not ATGC"""
    nuc = nuc.upper()
    if nuc in IUPAC_BASES and nuc not in "ATGC":
        return True
    else:
        return False


def kmer_iterator(dna, k):
    """Generates kmers of length k from a string with one step between kmers

    :param dna: string to generate kmers from
    :param k: size of kmer to generate
    """
    assert len(dna) >= 1, "You must select a substring with len(dna) >= 1: {}".format(dna)
    assert k >= 1, "You must select a main_string with k >= 1: {}".format(k)

    for i in range(len(dna)):
        kmer = dna[i:(i + k)]
        if len(kmer) == k:
            yield kmer


def count_all_sequence_kmers(seq, k=5, rev_comp=False, rev_comp_only=False):
    """Count all the 5'-3' kmers of a nucleotide sequence, rev_comp counts rev_comp seq IN ADDITION to given sequence

    :param seq: nucleotide sequence
    :param k: size of kmer
    :param rev_comp: boolean option to count reverse complement kmers as well
    :param rev_comp_only: boolean option to only count reverse complement kmers
    :return: dictionary of kmers with counts as values
    """
    # loop through kmers
    kmers = Counter()
    if not rev_comp_only:
        for kmer in kmer_iterator(seq, k):
            kmers[kmer] += 1
    if rev_comp or rev_comp_only:
        rc = ReverseComplement()
        # loop through rev_comp kmers
        seq1 = rc.reverse_complement(seq)
        for kmer in kmer_iterator(seq1, k):
            kmers[kmer] += 1

    return kmers


if __name__ == '__main__':
    print("This is a library of sequence helper functions")
