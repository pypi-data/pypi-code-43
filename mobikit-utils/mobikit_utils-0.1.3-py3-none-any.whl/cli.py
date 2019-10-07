#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from argparse import ArgumentParser

from mobikit_utils import __version__


def create_parser():
    parser = ArgumentParser("mobikit utilities")
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="show the mobikit utilities version",
    )
    return parser


def version():
    print(__version__)


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.version:
        version()
