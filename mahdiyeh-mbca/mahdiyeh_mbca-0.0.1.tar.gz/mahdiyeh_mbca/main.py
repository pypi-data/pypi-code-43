#!/usr/bin/env python3

# mahdiyeh_mbca/main.py
#
# This file is a part of:
# Azadeh Afzar - Mahdiyeh Mono Basic Computer Assembler in Python (AA-MMBCApy).
#
# Copyright (C) 2019 Azadeh Afzar
# Copyright (C) 2019 Mohammad Mahdi Baghbani Pourvahid
#
# GNU AFFERO GENERAL PUBLIC LICENSE
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ZLIB LICENSE
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgement in the product documentation would be
# appreciated but is not required.
#
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
#
# 3. This notice may not be removed or altered from any source distribution.
#

"""
Azadeh Afzar - Mahdiyeh Mano Basic Computer Assembler.

mahdiyeh_mbca.main module.
===================================

This module enabled assembler to be run from the terminal.

"""

# Python Standard Library
import argparse
import sys
from typing import Tuple

# Mahdiyeh Mano Basic Computer Assembler
from mahdiyeh_mbca._version import __version__
from mahdiyeh_mbca.assembler import Assembler


def main(argv: Tuple[str] = tuple(sys.argv[1:])) -> None:
    """Execute program in terminal (cli application)."""
    parser: argparse.ArgumentParser = create_parser()
    args: argparse.Namespace = parser.parse_args(list(argv))

    with open(args.file, "r") as file:
        program: str = file.read()

    assembler = Assembler(program)
    assembled = assembler.assembled

    with open(args.output, "wb") as file:
        file.write(assembled)


def create_parser() -> argparse.ArgumentParser:
    """Create a parser."""
    description: str = "Azadeh Afzar - Mahdiyeh Mono Basic Computer Assembler\n"
    epilog: str = "Saying Java is Good Because it works on all operation systems\n" \
                  + "is like saying anal sex is good because it works on all " \
                  + "genders!\n" \
                  + "A quote from Dennis MacAlistair Ritchie."

    # create parser
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description=description,
            epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter
    )

    help_file: str = "source code file path"
    parser.add_argument("-f", "--file", type=str, help=help_file)

    help_output: str = "file path for writing the assembled program into it"
    parser.add_argument("-o", "--output", type=str, help=help_output)

    # display version
    version: str = "Azadeh Afzar - Mahdiyeh Mono Basic Computer Assembler " \
                   + f"v{__version__}"
    parser.add_argument("-V", "--version", action="version", version=version)

    return parser


if __name__ == "__main__":
    main()
