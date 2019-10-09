#!/usr/bin/env python
"""Generate kmer counts from a methyl bed file given a reference"""
########################################################################
# File: methyl_bed_kmer_analysis.py
#  executable: methyl_bed_kmer_analysis.py
#
# Author: Andrew Bailey
# History: 06/02/19 Created
########################################################################

import os
import sys
import pickle
from argparse import ArgumentParser
from collections import Counter
from py3helpers.seq_tools import ReferenceHandler, count_all_sequence_kmers, ReverseComplement
from py3helpers.utils import time_it


def comma_separated_list(s):
    tokens = s.strip().split(",")
    return tokens


def parse_args():
    parser = ArgumentParser(description=__doc__)
    # required arguments
    parser.add_argument('--methyl_bed', '-m', action='store',
                        dest='methyl_bed', required=True,
                        type=str, default=None,
                        help="path methyl bed file")
    parser.add_argument('--reference', '-r', action='store',
                        dest='reference', required=True,
                        type=str, default=None,
                        help="path to reference sequence")
    parser.add_argument('--output', '-o', action='store',
                        dest='output', required=True,
                        type=str, default=None,
                        help="path to output directory")
    parser.add_argument('--check_base', '-c', action='store',
                        dest='check_base', required=False,
                        type=str, default=None,
                        help="If argument is passed in, will confirm that all bases in bed file match in reference")
    parser.add_argument('--kmer_length', '-k', action='store',
                        dest='kmer_length', required=False,
                        type=int, default=5,
                        help="Set kmer length. Default: 5")
    parser.add_argument('--filter_by_coverage', action='store',
                        dest='filter_by_coverage', required=False,
                        type=comma_separated_list, default=None,
                        help="Pass in a min and max value for coverage")
    parser.add_argument('--filter_by_percentage', action='store',
                        dest='filter_by_percentage', required=False,
                        type=comma_separated_list, default=None,
                        help="A low max and high min value for methylation percentage")

    args = parser.parse_args()
    return args


def parse_methyl_bed(path_to_bed):
    """Parse a 9+2 methyl bed file and yield each field
    :param path_to_bed: path to
    """
    with open(path_to_bed, 'r') as fh:
        for line in fh:
            chromosome, start1, stop1, name, coverage1, strand, start2, stop2, color, coverage2, percentage \
                = line.split()
            yield chromosome, int(start1), int(stop1), name, int(coverage1), strand, int(start2), int(stop2), color, \
                  int(coverage2), int(percentage)


class FilterBed(object):
    """Easy class to allow for filtering out bed rows by specific parameters"""

    def __init__(self):
        self.coverage_filter = False
        self.coverage_params = None
        self.percentage_filter = False
        self.percentage_params = None
        self.strand_filter = False
        self.strand_params = None
        self.chromosome_filter = False
        self.chromosome_params = None
        self.position_filter = False
        self.position_params = None
        self.filters = []

    @staticmethod
    def return_true(*args):
        """_return_true function to keep easy flow through get_kmer_counts_from_reference_given_bed
        :param args: takes in an assortemnt of argumetns and returns true
        :return:
        """
        return True

    def set_filter_by_coverage(self, *args):
        """Set filter by coverage parameters"""
        self.coverage_filter = True
        self.coverage_params = [*args]

    def filter_by_coverage_min_max(self, chromosome, start, stop, strand, coverage, percentage):
        """Return true if coverage is between a min and max"""
        if self.coverage_params[0] <= coverage <= self.coverage_params[1]:
            return True
        return False

    def filter_by_coverage_min_min_max_max(self, chromosome, start, stop, strand, coverage, percentage):
        """Return true if coverage is between a min and max"""
        if self.coverage_params[0] >= coverage or coverage >= self.coverage_params[1]:
            return True
        return False

    def set_filter_by_percentage(self, *args):
        """Set filter by coverage parameters"""
        self.percentage_filter = True
        self.percentage_params = [*args]

    def filter_by_percentage_min_max(self, chromosome, start, stop, strand, coverage, percentage):
        """Return true if coverage is between a min and max"""
        if self.percentage_params[0] <= percentage <= self.percentage_params[1]:
            return True
        return False

    def filter_by_percentage_min_min_max_max(self, chromosome, start, stop, strand, coverage, percentage):
        """Return true if coverage is between a min and max"""
        if self.percentage_params[0] >= percentage or percentage >= self.percentage_params[1]:
            return True
        return False

    def chain_logic(self, *args):
        for x in args:
            self.filters.append(x)

    def function(self, chromosome, start, stop, strand, coverage, percentage):
        start1 = True
        for filter1 in self.filters:
            start1 = start1 and filter1(chromosome, start, stop, strand, coverage, percentage)
        return start1


def get_kmer_counts_from_reference_given_bed(reference, bed_file, k=5, param_filter=FilterBed.return_true,
                                             check_base=None):
    """Generate kmer counts covering positions in a bed file"""
    ref_handler = ReferenceHandler(reference)
    kmers = Counter()
    counter = 0
    for chromosome, start, stop, _, _, strand, _, _, _, coverage, percentage in parse_methyl_bed(bed_file):
        if param_filter(chromosome, start, stop, strand, coverage, percentage):
            block_start = max(0, start - (k - 1))
            block_end = min(ref_handler.get_chr_sequence_length(chromosome), stop + (k - 1))
            seq = ref_handler.get_sequence(chromosome,
                                           block_start,
                                           block_end)
            # Check if base in bed file matches the reference sequence
            if check_base is not None:
                base = ref_handler.get_sequence(chromosome, start, stop)
                if strand == "-":
                    this_base = ReverseComplement().complement(check_base)
                else:
                    this_base = check_base

                assert this_base == base, \
                    "Check base is not the same as the one from the reference. " \
                    "{} != {}. {}".format(this_base, base, [chromosome, start, stop, strand, coverage, percentage])
            kmers += count_all_sequence_kmers(seq, k=k, rev_comp_only=(strand == "-"))

        # Print some updates because this takes a long time
        counter += 1
        if counter % 10000 == 0:
            print(".", end="")
            sys.stdout.flush()
            if counter % 1000000 == 0:
                print(counter)

    return kmers


def main():
    args = parse_args()
    filter_bed = FilterBed()
    filters = []
    if args.filter_by_percentage is not None:
        filter_bed.set_filter_by_percentage(*[float(x) for x in args.filter_by_percentage])
        filters.append(filter_bed.filter_by_percentage_min_min_max_max)

    if args.filter_by_coverage is not None:
        filter_bed.set_filter_by_coverage(*[float(x) for x in args.filter_by_coverage])
        filters.append(filter_bed.filter_by_coverage_min_max)

    filter_bed.chain_logic(*filters)

    kmers = get_kmer_counts_from_reference_given_bed(args.reference, args.methyl_bed,
                                                     k=args.kmer_length,
                                                     param_filter=filter_bed.function,
                                                     check_base=args.check_base)
    print(kmers)
    with open(os.path.join(args.output, "kmer_counts.pkl"), 'wb') as fh:
        pickle.dump(kmers, fh)


if __name__ == '__main__':
    _, time = time_it(main)
    print(time, "seconds")
