#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file name: args.py
author: Shlomi Ben-David (shlomi.ben.david@gmail.com)
file version: 0.0.1
"""
from pylib3 import get_version
import argparse
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_cli_args():
    """
    Get commandline arguments

    :return: arguments object
    """
    prog = 'package-generator'
    arguments_parser = argparse.ArgumentParser(prog=prog, add_help=False)
    optional_arguments_group = \
        arguments_parser.add_argument_group(title='optional arguments')
    optional_arguments_group.add_argument(
        '--help', action='help', default=argparse.SUPPRESS,
        help="show this help message and exit"
    )
    optional_arguments_group.add_argument(
        '--version', action='version',
        version=('%(prog)s v{0}'.format(
            get_version(caller=__file__, version_file='PYGENERATOR3_VERSION')
        )),
        help="shows program version"
    )
    optional_arguments_group.add_argument(
        '--log-file', metavar='NAME', dest='log_file',
        default='package_generator.log',
        help="log file name"
    )
    optional_arguments_group.add_argument(
        '--verbose', action='store_true',
        help="if added will print more information"
    )
    optional_arguments_group.add_argument(
        'console', action='store_true', default=True,
        help=argparse.SUPPRESS
    )
    optional_arguments_group.add_argument(
        '--python-version', metavar='NUM', default='3.5',
        help="python version (default: 3.5)"
    )
    optional_arguments_group.add_argument(
        '--url', metavar='URL', default='',
        help="url to package source code"
    )
    optional_arguments_group.add_argument(
        '--description', metavar='TEXT', default='sample package',
        help="python package description"
    )
    optional_arguments_group.add_argument(
        '--version-file', metavar='TEXT',
        help="python package version file name"
    )
    optional_arguments_group.add_argument(
        '--dst', metavar='PATH',
        help="destination path where the python package will be created"
    )
    optional_arguments_group.add_argument(
        '--package-version', metavar='TEXT', default='0.0.1',
        help="python package version number (default: 0.0.1)"
    )
    required_arguments_group = \
        arguments_parser.add_argument_group(title='required arguments')
    required_arguments_group.add_argument(
        '--package-name', metavar='TEXT', required=True,
        help="python package name"
    )
    required_arguments_group.add_argument(
        '--author', metavar='TEXT', required=True,
        help="Author's full name"
    )
    required_arguments_group.add_argument(
        '--author-email', metavar='EMAIL', required=True,
        help="Author's email address"
    )

    return arguments_parser.parse_args()
