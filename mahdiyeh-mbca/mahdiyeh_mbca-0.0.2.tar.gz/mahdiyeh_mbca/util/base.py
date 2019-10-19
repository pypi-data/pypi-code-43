# mahdiyeh_mbca/util/base.py
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

mahdiyeh_mbca.util.base module.
========================

This module contains general purpose classes.

"""

# Python Standard Library
from math import ceil
from math import log


class MemoryWord(object):
    """Memory word class to enforce mano memory relation rules."""

    def __init__(self, word_count: int = 4096, word_bits_width: int = 16) -> None:
        """Initialize a memory word instance."""
        self.word_bits_width = word_bits_width
        self.word_count = word_count

    @property
    def word_count(self) -> int:
        """Return memory word count."""
        return self._word_count

    @word_count.setter
    def word_count(self, value: int) -> None:
        """Set memory word count."""
        # check type and value.
        if not (type(value) == int and value >= 4096):
            raise ValueError("Word count must be an integer more than or equal to "
                             f"4096, you have passed: {value}")
        # in mano basic computer 4 bits of each instruction stored in memory
        # are reserved for the opcodes, thus address line width must be exactly
        # 4 bits less than the word width, minimum address line width is
        # calculated with log(number of cells, 2), if it isn't an integer number,
        # to find minimum width, round up (ceil) the value to next integer.
        if ceil(log(value, 2)) != self.word_bits_width - 4:
            raise ValueError("Address line width isn't 4 bits less than word width.")

        # assign word
        self._word_count: int = value

    @property
    def word_bits_width(self) -> int:
        """Return memory word width in bits."""
        return self._word_bits_width

    @word_bits_width.setter
    def word_bits_width(self, value: int) -> None:
        """Set memory word width in bits."""
        # check type and value.
        if not (type(value) == int and value >= 16):
            raise ValueError("Cell width must be an integer more than or equal to "
                             f"16, you have passed: {value}")
        # check width to be a multiplicative of 8 bits (1 byte).
        if value % 8 != 0:
            raise ValueError("Cell width multiplicative of 8 bits (1 byte), "
                             f"you have passed: {value}")
        # assign word width
        self._word_bits_width: int = value

    @property
    def word_bytes_width(self) -> int:
        """Return memory word width in bytes."""
        return int(float(self._word_bits_width) / 8)

    @property
    def address_lines_count(self) -> int:
        """Return memory address line count."""
        return ceil(log(self.word_count, 2))

    @property
    def memory_bits_space(self) -> int:
        """Return memory space in bits."""
        return self.word_count * self.word_bits_width

    @property
    def memory_bytes_space(self) -> int:
        """Return memory space in bytes."""
        return int(float(self.memory_bits_space) / 8)
