# coding: utf8
from __future__ import unicode_literals, print_function, division
import sys

from clldutils.path import Path
from clldutils.clilib import ArgumentParserWithLogging

from clldlucl import commands
assert commands


def main():  # pragma: no cover
    parser = ArgumentParserWithLogging('clldlucl')
    parser.add_argument("--project", help='clld app project dir', default=".", type=Path)
    parser.add_argument("--version", help='data version', default="1.0")
    sys.exit(parser.main())


if __name__ == '__main__':  # pragma: no cover
    main()
