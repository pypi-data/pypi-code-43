# mahdiyeh_mbca/util/number_manipulation.py
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

mahdiyeh_mbca.util.number_manipulation module.
===================================

This module provides functions to convert
numbers to different representations.

"""


def hex_to_int(hexadecimal: str) -> int:
    """
    Convert a hexadecimal number to integer.

    :param hexadecimal: the hex number to be converted.
    :rtype: int
    """
    return int(hexadecimal, 16)


def int_to_byte(number: int, word_bytes_width: int = 2,
                signed: bool = False) -> bytes:
    """
    Convert an integer to a 16 bit byte string (2 bytes).

    :param number: the integer to be converted.
    :param word_bytes_width: length of word in bytes.
    :param signed: flag for signed and unsigned conversion.
    :return: a 16 bit (2 bytes) binary string.
    :rtype: bytes
    """
    return number.to_bytes(word_bytes_width, byteorder="big", signed=signed)


def byte_to_int(byte: bytes, signed: bool) -> int:
    """
    Convert a 16 bit (2 bytes) number to an integer.

    :param byte: the binary number to be converted.
    :param signed: flag for signed and unsigned conversion.
    :return: an integer.
    :rtype int
    """
    return int.from_bytes(byte, byteorder="big", signed=signed)
