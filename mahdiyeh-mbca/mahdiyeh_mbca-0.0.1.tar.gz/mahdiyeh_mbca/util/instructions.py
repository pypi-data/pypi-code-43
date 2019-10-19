# mahdiyeh_mbca/util/instructions.py
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

mahdiyeh_mbca._instructions module.
========================

This module contains Mano basic computer
instruction sets.

"""

# Python Standard Library
from typing import Dict
from typing import List
from typing import Tuple

# instruction table for (resolve references, i bit valid, opcode, operand)
RawInstructionList = List[int]
InstructionTuple = Tuple[int, int, int, int]
InstructionTable = Dict[str, InstructionTuple]

# raw tables (resolve reference, i bit valid, opcode, operand)
# Memory reference instructions raw table
_mri: Dict[str, RawInstructionList] = {
    "AND": [1, 1, 0x0, 0x000],
    "ADD": [1, 1, 0x1, 0x000],
    "LDA": [1, 1, 0x2, 0x000],
    "STA": [1, 1, 0x3, 0x000],
    "BUN": [1, 1, 0x4, 0x000],
    "BSA": [1, 1, 0x5, 0x000],
    "ISZ": [1, 1, 0x6, 0x000],
}

# Register reference instructions raw table
_rri: Dict[str, RawInstructionList] = {
    "CLA": [0, 0, 0x7, 0x800],
    "CLE": [0, 0, 0x7, 0x400],
    "CMA": [0, 0, 0x7, 0x200],
    "CME": [0, 0, 0x7, 0x100],
    "CIR": [0, 0, 0x7, 0x080],
    "CIL": [0, 0, 0x7, 0x040],
    "INC": [0, 0, 0x7, 0x020],
    "SPA": [0, 0, 0x7, 0x010],
    "SNA": [0, 0, 0x7, 0x008],
    "SZA": [0, 0, 0x7, 0x004],
    "SZE": [0, 0, 0x7, 0x002],
    "HLT": [0, 0, 0x7, 0x001],
}

# Input / output raw table
_io: Dict[str, RawInstructionList] = {
    "INP": [0, 0, 0xF, 0x800],
    "OUT": [0, 0, 0xF, 0x400],
    "SKI": [0, 0, 0xF, 0x200],
    "SKO": [0, 0, 0xF, 0x100],
    "ION": [0, 0, 0xF, 0x080],
    "IOF": [0, 0, 0xF, 0x040],
}

# Preudomstruction raw table
preudomstruction: List[str] = [
    "ORG",
    "HEX",
    "DEC",
    "END"
]

#  Memory reference instruction Identifier
mri_identifier: List[int] = [
    0x0, 0x8,
    0x1, 0x9,
    0x2, 0xA,
    0x3, 0xB,
    0x4, 0xC,
    0x5, 0xD,
    0x6, 0xE
]


def create_table(mnemonics: Dict[str, RawInstructionList],
                 address_lines_count: int) -> InstructionTable:
    """Modify raw tables to be compatible with the computer address line count."""
    for mnemonic in mnemonics:
        mnemonics[mnemonic][3] = mnemonics[mnemonic][3] << (address_lines_count - 12)

    return {mnemonic: tuple(mnemonics[mnemonic]) for mnemonic in mnemonics}


# Memory reference instructions
def mri(address_lines_count: int) -> Dict[str, int]:
    """Create memory reference instructions dictionary."""
    table: InstructionTable = create_table(_mri, address_lines_count)
    return {i: (table[i][2] << address_lines_count) | table[i][3] for i in table}


# Register reference instructions
def rri(address_lines_count: int) -> Dict[str, int]:
    """Create register reference instructions dictionary."""
    table: InstructionTable = create_table(_rri, address_lines_count)
    return {i: (table[i][2] << address_lines_count) | table[i][3] for i in table}


# Input / output
def io(address_lines_count: int) -> Dict[str, int]:
    """Create io reference instructions dictionary."""
    table: InstructionTable = create_table(_io, address_lines_count)
    return {i: (table[i][2] << address_lines_count) | table[i][3] for i in table}
