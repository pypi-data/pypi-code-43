# mahdiyeh_mbca/util/cleaner.py
#
# This file is a part of:
# Azadeh Afzar - Mahdiyeh Mano Basic Computer Assembler in Python (AA-MMBCApy).
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

mahdiyeh_mbca.cleaner module.
========================

This module contains functions
to clean source code.

"""

# Python Standard Library
from typing import List
from typing import Set
from typing import Union


def clean_source(source_code: str) -> str:
    """
    Clean source code.

    :param source_code: original source code.
    :return: source code without redundant whitespaces and comments.
    :rtype: str
    """
    lines: List[str] = source_code.split("\n")
    remove_indexes: Union[Set[int], List[int]] = set()

    # create a (index, line) tuple to keep track of indexes.
    pairs: enumerate = enumerate(lines)
    for index, line in pairs:
        # remove comments.
        if ";" in line:
            line = line.split(";")[0]

        # add whitespace line index to remove set.
        if line.isspace():
            remove_indexes.add(index)

        # add empty line index to remove set.
        if line == "":
            remove_indexes.add(index)

        # remove leading and trailing whitespace in lines.
        lines[index] = line.strip()

    # turn set to list and then reverse the order of numbers
    # to prevent index out of range in next step.
    remove_indexes = list(remove_indexes)
    remove_indexes.sort(reverse=True)

    # remove whitespace or empty lines.
    for i in remove_indexes:
        del lines[i]

    # turn back list of lines into string.
    return "\n".join(lines)
