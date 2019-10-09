#!/usr/bin/env python
"""Merge methyl bed files (9+2) into a single bed file"""
########################################################################
# File: merge_methyl_bed_files.py
#  executable: merge_methyl_bed_files.py
#
# Author: Andrew Bailey
# History: 06/02/19 Created
########################################################################

from argparse import ArgumentParser
from py3helpers.utils import NestedDefaultDict


def comma_separated_list(s):
    tokens = s.strip().split(",")
    return tokens


def parse_args():
    parser = ArgumentParser(description=__doc__)
    # parsers for running the full pipeline
    # required arguments
    parser.add_argument('--methyl_beds', '-m', action='store',
                        dest='methyl_beds', required=True,
                        type=comma_separated_list, default=None,
                        help="paths methyl bed files")
    parser.add_argument('--output', '-o', action='store',
                        dest='output', required=True,
                        type=str, default=None,
                        help="path to output bed file")

    args = parser.parse_args()
    return args


def aggregate_methylbeds(methyl_beds):
    """Aggregate methylbed files into a single defaultdictionary
    :param methyl_beds: list of methyl bed files
    """
    all_data = NestedDefaultDict()
    for input_file in methyl_beds:
        with open(input_file, 'r') as fh:
            for line in fh:
                chromosome, start1, stop1, name, coverage1, \
                strand, start2, stop2, color, coverage2, percentage = line.split()
                try:
                    all_data[chromosome][strand][start1].append((color, int(coverage2), float(percentage)))
                except AttributeError:
                    all_data[chromosome][strand][start1] = [(color, int(coverage2), float(percentage))]
    return all_data


def write_bed_file(bed_default_dict, output_file):
    """Write default dict to a bed file
    :param bed_default_dict: default dict created from aggregate_methylbeds
    :param output_file: path to output file
    """
    with open(output_file, "w") as fh:
        for chromosome, strand_dict in bed_default_dict.items():
            for strand, start_dict in strand_dict.items():
                for start, coverage_list in start_dict.items():
                    coverage_total = 0
                    percentage_total = 0
                    max_percentage = 0
                    for x in coverage_list:
                        coverage_total += x[1]
                        percentage_total += x[1] * x[2]
                        max_percentage += x[1] * 100

                    color = x[0]
                    if max_percentage != 0:
                        percentage = int((percentage_total / max_percentage) * 100)
                        print("\t".join([chromosome, start, str(int(start) + 1), ".",
                                         str(coverage_total), strand, start, str(int(start) + 1), color,
                                         str(coverage_total), str(percentage)]), file=fh)


def main():
    args = parse_args()
    all_data = aggregate_methylbeds(args.methyl_beds)
    write_bed_file(all_data, args.output)


if __name__ == '__main__':
    main()
