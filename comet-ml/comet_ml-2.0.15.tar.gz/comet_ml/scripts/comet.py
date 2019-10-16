#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

"""
Examples:

    comet upload file.zip ...
    comet upload --force-reupload file.zip ...

    comet optimize script.py optimize.config
    comet optimize -j 4 script.py optimize.config
    comet optimize -j 4 script.py optimize.config -- arg1 --flag arg2

    comet bootstrap_dir

    comet python script.py
    comet python -p /usr/bin/python3.6 script.py

    comet offline 60a1a617e4c24c8998cc78fa3bc7a31b.zip
    comet offline --csv 60a1a617e4c24c8998cc78fa3bc7a31b.zip

Note that `comet optimize` requires your COMET_API_KEY
be configured in the environment, or in your .comet.config
file. For example:

    COMET_API_KEY=74345364546 comet optimize ...

For more information:
    comet COMMAND --help
"""

from __future__ import print_function

import argparse
import os.path
import sys

from .comet_offline import (
    __doc__ as offline_doc,
    get_parser_arguments as offline_parser_arguments,
    offline,
)
from .comet_optimize import (
    __doc__ as optimize_doc,
    get_parser_arguments as optimize_parser_arguments,
    optimize,
)
from .comet_python import (
    __doc__ as python_doc,
    get_parser_arguments as python_parser_arguments,
    python_wrapper,
)
from .comet_upload import (
    __doc__ as upload_doc,
    get_parser_arguments as upload_parser_arguments,
    upload,
)


def bootstrap_dir(args):
    """ Print the bootstrap dir to include in PYTHONPATH for automatic early
    SDK initialization. See also `comet python` that set it automatically.
    """
    import comet_ml.bootstrap

    boostrap_dir = os.path.dirname(comet_ml.bootstrap.__file__)
    print(boostrap_dir, end="")


def main(raw_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers()

    # Add subparsers
    upload_parser = subparsers.add_parser(
        "upload",
        description=upload_doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    upload_parser.set_defaults(func=upload)
    upload_parser.set_defaults(additional_args=False)
    upload_parser_arguments(upload_parser)

    optimize_parser = subparsers.add_parser(
        "optimize",
        description=optimize_doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    optimize_parser.set_defaults(func=optimize)
    optimize_parser.set_defaults(additional_args=True)
    optimize_parser_arguments(optimize_parser)

    bootstrap_dir_parser = subparsers.add_parser(
        "bootstrap_dir",
        description=bootstrap_dir.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    bootstrap_dir_parser.set_defaults(func=bootstrap_dir)
    bootstrap_dir_parser.set_defaults(additional_args=False)

    python_parser = subparsers.add_parser(
        "python",
        description=python_doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    python_parser.set_defaults(func=python_wrapper)
    python_parser.set_defaults(additional_args=True)
    python_parser_arguments(python_parser)

    offline_parser = subparsers.add_parser(
        "offline",
        description=offline_doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    offline_parser.set_defaults(func=offline)
    offline_parser.set_defaults(additional_args=True)
    offline_parser_arguments(offline_parser)

    # First identify the subparser as some subparser pass additional args to
    # the subparser and other not
    args, rest = parser.parse_known_args(raw_args)

    if args.additional_args:
        parser_func = args.func

        parser_func(args, rest)
    else:
        # If the subcommand doesn't need extra args, reparse in strict mode so
        # the users get a nice message in case of unsupported CLi argument
        args = parser.parse_args(raw_args)
        parser_func = args.func

        parser_func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
