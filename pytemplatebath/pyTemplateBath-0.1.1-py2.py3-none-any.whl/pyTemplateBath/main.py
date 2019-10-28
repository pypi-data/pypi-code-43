#!/usr/bin/env python3

""" Basic command line tool for Hello World. """

import pyTemplateBath as tb
import pyCommonTools as pct
import sys
import argparse
import logging


def main():

    epilog = 'Stephen Richer, University of Bath, Bath, UK (sr467@bath.ac.uk)'

    formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(
        prog='pyTemplateBath',
        description=__doc__,
        formatter_class=formatter_class,
        epilog=epilog)

    subparsers, base_parser = pct.set_subparser(parser)

    # Sub-parser
    sub_parser = subparsers.add_parser(
        'hello',
        description=tb.hello.__doc__,
        help='Classic Hello World program.',
        parents=[base_parser],
        formatter_class=formatter_class,
        epilog=epilog)
    sub_parser.add_argument(
        '-n', '--name', default='World',
        help='Provide name.')
    sub_parser.set_defaults(function=tb.hello.hello_world)

    return (pct.execute(parser))
