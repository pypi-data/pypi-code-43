# mahdiyeh_mbca/disassembler.py
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

mahdiyeh_mbca.disassembler module.
========================

This module contains the disassembler class.

"""

# Python Standard Library
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

# Mahdiyeh Mano Basic Computer Assembler
from mahdiyeh_mbca.util.base import MemoryWord
from mahdiyeh_mbca.util.cleaner import clean_source
from mahdiyeh_mbca.util.instructions import io
from mahdiyeh_mbca.util.instructions import mri
from mahdiyeh_mbca.util.instructions import mri_identifier
from mahdiyeh_mbca.util.instructions import preudomstruction
from mahdiyeh_mbca.util.instructions import rri
from mahdiyeh_mbca.util.number_manipulation import byte_to_int
from mahdiyeh_mbca.util.number_manipulation import hex_to_int
from mahdiyeh_mbca.util.number_manipulation import int_to_byte


class Disassembler(MemoryWord):
    """Disassemble binary programs into assembly language for Mano Basic Computer."""

    def __init__(self, binary_program: bytes, word_count: int = 4096,
                 word_bits_width: int = 16) -> None:
        """
        Instantiate an disassembler object.

        :param binary_program: program binary object.
        :param word_count: target computer memory word count.
        :param word_bits_width: target computer memory word width in bits.
        :return: nothing.
        :rtype: None
        """
        # init parent class.
        super().__init__(word_count, word_bits_width)

        self.mri: Dict[str, int] = mri(self.address_lines_count)
        self.rri: Dict[str, int] = rri(self.address_lines_count)
        self.io: Dict[str, int] = io(self.address_lines_count)
        self.preudomstruction: List[str] = preudomstruction
        self.binary = binary_program

    @property
    def binary(self) -> bytes:
        """Return binary program."""
        return self._binary

    @binary.setter
    def binary(self, value: bytes) -> None:
        """Set binary program."""
        self._binary: bytes = value

    @property
    def binary_byte_count(self) -> int:
        return len(self.binary)

    def mock(self, word):
        mask: int = self.address_lines_count

        opcode: int = (word & (0xf << mask)) >> mask
        address: int = (word & ((1 << mask) - 1))
        indirect: bool = (opcode & 0x8) == 0x8
