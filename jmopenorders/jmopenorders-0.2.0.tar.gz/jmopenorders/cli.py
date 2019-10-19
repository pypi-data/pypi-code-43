#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementation of the command line interface."""
#
# Copyright (c) 2019 Jürgen Mülbert. All rights reserved.
#
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
#
# Lizenziert unter der EUPL, Version 1.2 oder - sobald
#  diese von der Europäischen Kommission genehmigt wurden -
# Folgeversionen der EUPL ("Lizenz");
# Sie dürfen dieses Werk ausschließlich gemäß
# dieser Lizenz nutzen.
# Eine Kopie der Lizenz finden Sie hier:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Sofern nicht durch anwendbare Rechtsvorschriften
# gefordert oder in schriftlicher Form vereinbart, wird
# die unter der Lizenz verbreitete Software "so wie sie
# ist", OHNE JEGLICHE GEWÄHRLEISTUNG ODER BEDINGUNGEN -
# ausdrücklich oder stillschweigend - verbreitet.
# Die sprachspezifischen Genehmigungen und Beschränkungen
# unter der Lizenz sind dem Lizenztext zu entnehmen.
#
from argparse import ArgumentParser
from inspect import getfullargspec

from . import __version__
from .api.hello import hello
from .api.report import report
from .core.config import config
from .core.logger import logger


def main(argv=None) -> int:
    """Execute the application CLI.

    :param argv: argument list to parse (sys.argv by default)
    :return: exit status
    """
    args = _args(argv)
    logger.start(args.warn or "DEBUG")  # can't use default from config yet
    logger.debug("starting execution")
    config.load(args.config)
    config.core.config = args.config
    if args.warn:
        config.core.logging = args.warn
    logger.stop()  # clear handlers to prevent duplicate records
    logger.start(config.core.logging)
    command = args.command
    args = vars(args)
    spec = getfullargspec(command)
    if not spec.varkw:
        # No kwargs, remove unexpected arguments.
        args = {key: args[key] for key in args if key in spec.args}
    try:
        command(**args)
    except RuntimeError as err:
        logger.critical(err)
        return 1
    logger.debug("sucessful completion")
    return 0


def _args(argv):
    """ Parse command line arguments.

    :param argv: argument list to parse
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", action="append",
        help="config file [etc/config.yml]",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="jmopenorders {:s}".format(__version__),
        help="print version and exit",
    )
    parser.add_argument(
        "-w", "--warn", default="WARN",
        help="logger warning level [WARN]",
    )
    parser.add_argument(
        "-i", "--inputpath", type=str,
        help="inputpath for data",
    )
    parser.add_argument(
        "-o", "--outputpath", type=str,
        help="outputpath to write files",
    )
    parser.add_argument(
        "-p", "--personfile", type=str,
        help="the names to report",
    )
    parser.add_argument("-d", "--datafile", type=str, help="the datafile")
    common = ArgumentParser(add_help=False)  # common subcommand arguments
    common.add_argument("-n", "--name", default="World", help="greeting name")
    subparsers = parser.add_subparsers(title="subcommand")
    _report(subparsers, common)
    args = parser.parse_args(argv)
    if not args.config:
        # Don't specify this as an argument default or else it will always be
        # included it the list.
        args.config = "etc/config.yml"
    return args


def _hello(subparsers, common):
    """ CLI adaptor for the api.hello command.

    :param subparsers: subcommand parsers
    :param common: parser for common subcommand arguments
    """

    parser = subparsers.add_parser("hello", parents=[common])
    parser.set_defaults(commands=hello)
    return


def _report(subparsers, common):
    """ CLI adaptor for the api.hello command.

    :param subparsers: subcommand parsers
    :param common: parser for common subcommand arguments
    """

    parser = subparsers.add_parser("report", parents=[common])
    parser.set_defaults(commands=report)
    return


# Make the module executable.
if __name__ == "__main__":
    try:
        status = main()
    except Exception:
        logger.critical("shutting down due to fatal error")
        raise  # print stack trace
    else:
        raise SystemExit(status)
