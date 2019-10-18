#!/usr/bin/env python

"""
Download a series of static files for various organisms and genome assemblies.
"""

import os
import sys

from argparse import ArgumentParser

from ngs_toolkit import _CONFIG, _LOGGER, Analysis


def parse_arguments():
    """
    Argument Parsing.
    """
    parser = ArgumentParser(
        prog="python -m ngs_toolkit.recipes.resources", description=__doc__)
    parser.add_argument(
        "--output-dir",
        dest="output_dir", type=str,
        help="Directory to write files to.")
    parser.add_argument(
        "--steps",
        dest="steps", type=str,
        default="blacklist,tss,genomic_context,genome",
        help="What type of resource to get files for."
        "Comma-delimiter list. Defaults to all possible.")
    parser.add_argument(
        "--organisms",
        dest="organisms", type=str,
        default="human",
        help="Organisms to get files for."
        " Comma-delimited list: e.g. human,mouse")
    parser.add_argument(
        "--genome-assemblies",
        dest="genome_assemblies", type=str,
        default="hg38",
        help="Genome assemblies to get files for."
        " Comma-delimited list: e.g. hg38,mm10")
    parser.add_argument(
        "--no-overwrite", action="store_false",
        dest="overwrite",
        help="Whether results should not be overwritten if existing.")
    return parser


def main():
    """Download a series of static files for various organisms and genome assemblies."""
    args = parse_arguments().parse_args()

    for attr in ["steps", "organisms", "genome_assemblies"]:
        setattr(args, attr, getattr(args, attr).split(","))

    prev_level = _LOGGER.getEffectiveLevel()
    _LOGGER.setLevel("ERROR")
    an = Analysis()
    an.organism = "organism"
    an.genome = "genome"
    _LOGGER.setLevel(prev_level)

    if args.output_dir is None:
        args.output_dir = an._format_string_with_environment_variables(
            _CONFIG["preferences"]["root_reference_dir"])
        if args.output_dir is None:
            args.output_dir = os.path.abspath(os.path.curdir)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for organism in args.organisms:
        for genome_assembly in args.genome_assemblies:
            for step in args.steps:
                print((
                    "Getting '{}' resource for '{}/{}'."
                    .format(step, organism, genome_assembly)))
                out = an.get_resources(
                    output_dir=args.output_dir,
                    organism=organism,
                    genome_assembly=genome_assembly,
                    steps=[step], overwrite=args.overwrite)
                if step == "genome":
                    output = list(out[step].items())[0][1]
                else:
                    output = list(out.items())[0][1]
                print((
                    "Saved '{}' resource for '{}/{}': {}"
                    .format(step, organism, genome_assembly, output)))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Program canceled by user!")
        sys.exit(1)
