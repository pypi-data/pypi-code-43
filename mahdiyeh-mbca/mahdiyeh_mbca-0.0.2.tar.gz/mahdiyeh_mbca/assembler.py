# mahdiyeh_mbca/assembler.py
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

mahdiyeh_mbca.assembler module.
========================

This module contains the assembler class.

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
from mahdiyeh_mbca.util.instructions import preudomstruction
from mahdiyeh_mbca.util.instructions import rri
from mahdiyeh_mbca.util.number_manipulation import hex_to_int
from mahdiyeh_mbca.util.number_manipulation import int_to_byte

# Type aliases
AdrsTable = Dict[str, int]
CacheUni = Union[bytes, AdrsTable]
ParsedLine = Tuple[Optional[str], str, Optional[str], bool]


class Assembler(MemoryWord):
    """Assemble programs for Mano Basic Computer."""

    def __init__(self, source_code: str, word_count: int = 4096,
                 word_bits_width: int = 16) -> None:
        """
        Instantiate an assembler object.

        :param source_code: assembly language code.
        :param word_count: target computer memory word count.
        :param word_bits_width: target computer memory word width in bits.
        :return: nothing.
        :rtype: None
        """
        # init parent class.
        super().__init__(word_count, word_bits_width)
        self._source_code_hash: Dict[str, int] = {"AdrsTable": 0, "Assembled": 0}

        self.mri: Dict[str, int] = mri(self.address_lines_count)
        self.rri: Dict[str, int] = rri(self.address_lines_count)
        self.io: Dict[str, int] = io(self.address_lines_count)
        self.preudomstruction: List[str] = preudomstruction
        self.source = source_code

    @property
    def source(self) -> str:
        """Contain source code for assembling."""
        return self._source

    @source.setter
    def source(self, value: str) -> None:
        """Clean and analyze new source code before assembling."""
        value = clean_source(value)
        self._source: str = value

    @property
    def address_table(self) -> AdrsTable:
        """
        Create address table for the label names in the source code.

        :return: address table that maps a label name with an address in memory.
        :rtype: Dict[int, int]
        """
        current_hash: int = hash(self.source)

        if current_hash != self._source_code_hash["AdrsTable"]:
            self._source_code_hash["AdrsTable"] = current_hash
            self.address_table = self._create_address_table()

        return self._address_table

    @address_table.setter
    def address_table(self, value: AdrsTable) -> None:
        """Set address table for the label names in the source code."""
        self._address_table: AdrsTable = value

    @property
    def assembled(self) -> bytes:
        """
        Return Assembled source code.

        :return: byte string containing assembled program.
        :rtype: bytes
        """
        current_hash: int = hash(self.source)

        if current_hash != self._source_code_hash["Assembled"]:
            self._source_code_hash["Assembled"] = current_hash
            self.assembled = self._assemble()

        return self._assembled

    @assembled.setter
    def assembled(self, value: bytes) -> None:
        """Set Assembled source code."""
        self._assembled: bytes = value

    def _create_address_table(self) -> AdrsTable:
        """Create address table for the label names in the source code."""
        table: Dict[str, int] = dict()
        location: int = 0

        for label, command, operand, indirect in self._precompile_lines():
            if command == "ORG":
                location = hex_to_int(operand)
                continue

            if label:
                table[label] = location

            location += 1

        return table

    def _assemble(self) -> bytes:
        """Assemble source code into machine binary instruction codes."""
        address_table: Dict[str, int] = self.address_table
        array_size = self.word_count * 2 + 2
        binary_array: bytearray = bytearray(array_size)
        index: int

        location: int = 0
        program_start: Optional[int] = None

        for label, command, operand, indirect in self._precompile_lines():
            if command == "ORG":
                location = hex_to_int(operand)
                if program_start is None:
                    binary_array[0:self.word_bytes_width] = int_to_byte(
                            location, signed=False
                    )
                    program_start = location
                continue

            elif command == "HEX":
                instruction = int_to_byte(hex_to_int(operand), signed=True)

            elif command == "DEC":
                instruction = int_to_byte(int(operand), signed=True)

            elif command in self.mri:
                instruction = self.mri[command] | address_table[operand]

                if indirect:
                    # for indirect mri commands, change msb to 1.
                    instruction |= 0x8 << self.address_lines_count

                instruction = int_to_byte(instruction, signed=False)

            elif command in self.rri:
                instruction = int_to_byte(self.rri[command], signed=False)

            elif command in self.io:
                instruction = int_to_byte(self.io[command], signed=False)

            else:
                raise SyntaxError("Unrecognized command: {}".format(command))

            # find array index in bytes array for this location
            # based on word bytes length.
            index = location * self.word_bytes_width + self.word_bytes_width
            binary_array[index:index + self.word_bytes_width] = instruction
            # go to next location
            location += 1

        return bytes(binary_array)

    def _precompile_lines(self) -> Iterable[ParsedLine]:
        """Read lines from source code an parse them."""
        lines: List[str] = self.source.split("\n")

        for line in lines:
            if line == "END":
                # End of program.
                break

            yield self._parse_line(line)

    @staticmethod
    def _parse_line(line: str) -> ParsedLine:
        """Parse a line."""
        parts: List[str] = line.split(",")
        label: Optional[str] = None
        if len(parts) == 2:
            label = parts.pop(0)
            line = parts.pop(0).strip()

        parts = line.split()
        command: str = parts.pop(0)
        operand: Optional[str] = None
        indirect = False
        if parts:
            operand = parts.pop(0)
            indirect = (parts and parts[0] == "I")

        return label, command, operand, indirect
