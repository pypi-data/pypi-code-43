# mahdiyeh_mbca/test/test_assembler.py
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

# Python Standard Library
import unittest

# Mahdiyeh Mano Basic Computer Assembler
from mahdiyeh_mbca.assembler import Assembler
from mahdiyeh_mbca.util.number_manipulation import byte_to_int


class TestAssembler(unittest.TestCase):

    def setUp(self):
        self.array = None

    def tearDown(self):
        self.array = None

    @staticmethod
    def load_program(program) -> bytes:
        assembler = Assembler(program, 4096)
        return assembler.assembled

    def load_array_byte(self, index, signed) -> int:
        index = index * 2 + 2
        return byte_to_int(self.array[index:index + 2], signed)

    def test_assemble_rri_commands(self):
        program = """
            ORG 0
            CLA
            CLE
            CMA
            CME
            CIR
            CIL
            INC
            SPA
            SNA
            SZA
            SZE
            HLT
            END
        """
        self.array = self.load_program(program)

        self.assertEqual(0, byte_to_int(self.array[0:2], signed=False))
        self.assertEqual(0x7800, self.load_array_byte(0x0, signed=False))
        self.assertEqual(0x7400, self.load_array_byte(0x1, signed=False))
        self.assertEqual(0x7200, self.load_array_byte(0x2, signed=False))
        self.assertEqual(0x7100, self.load_array_byte(0x3, signed=False))
        self.assertEqual(0x7080, self.load_array_byte(0x4, signed=False))
        self.assertEqual(0x7040, self.load_array_byte(0x5, signed=False))
        self.assertEqual(0x7020, self.load_array_byte(0x6, signed=False))
        self.assertEqual(0x7010, self.load_array_byte(0x7, signed=False))
        self.assertEqual(0x7008, self.load_array_byte(0x8, signed=False))
        self.assertEqual(0x7004, self.load_array_byte(0x9, signed=False))
        self.assertEqual(0x7002, self.load_array_byte(0xA, signed=False))
        self.assertEqual(0x7001, self.load_array_byte(0xB, signed=False))

    def test_assemble_io_commands(self):
        program = """
            ORG 100
            INP
            OUT
            SKI
            SKO
            ION
            IOF
            END
        """
        self.array = self.load_program(program)

        self.assertEqual(0x100, byte_to_int(self.array[0:2], signed=False))
        self.assertEqual(0xF800, self.load_array_byte(0x100, signed=False))
        self.assertEqual(0xF400, self.load_array_byte(0x101, signed=False))
        self.assertEqual(0xF200, self.load_array_byte(0x102, signed=False))
        self.assertEqual(0xF100, self.load_array_byte(0x103, signed=False))
        self.assertEqual(0xF080, self.load_array_byte(0x104, signed=False))
        self.assertEqual(0xF040, self.load_array_byte(0x105, signed=False))

    def test_assemble_mri_commands(self):
        program = """
                 ORG 100
                 AND AAA
                 AND AAA I
                 ADD BBB
                 ADD BBB I
                 LDA CCC
                 LDA CCC I
                 STA DDD
                 STA DDD I
                 BUN EEE
                 BUN EEE I
                 BSA FFF
                 BSA FFF I
                 ISZ GGG
                 ISZ GGG I
            AAA, HEX 0
            BBB, HEX 1
            CCC, HEX 2
            DDD, HEX 4
            EEE, HEX 8
            FFF, HEX F
            GGG, DEC -23
                 END
        """
        self.array = self.load_program(program)

        self.assertEqual(0x100, byte_to_int(self.array[0:2], signed=False))
        self.assertEqual(0x010E, self.load_array_byte(0x100, signed=False))
        self.assertEqual(0x810E, self.load_array_byte(0x101, signed=False))
        self.assertEqual(0x110F, self.load_array_byte(0x102, signed=False))
        self.assertEqual(0x910F, self.load_array_byte(0x103, signed=False))
        self.assertEqual(0x2110, self.load_array_byte(0x104, signed=False))
        self.assertEqual(0xA110, self.load_array_byte(0x105, signed=False))
        self.assertEqual(0x3111, self.load_array_byte(0x106, signed=False))
        self.assertEqual(0xB111, self.load_array_byte(0x107, signed=False))
        self.assertEqual(0x4112, self.load_array_byte(0x108, signed=False))
        self.assertEqual(0xC112, self.load_array_byte(0x109, signed=False))
        self.assertEqual(0x5113, self.load_array_byte(0x10A, signed=False))
        self.assertEqual(0xD113, self.load_array_byte(0x10B, signed=False))
        self.assertEqual(0x6114, self.load_array_byte(0x10C, signed=False))
        self.assertEqual(0xE114, self.load_array_byte(0x10D, signed=False))

        self.assertEqual(0x0, self.load_array_byte(0x10E, signed=True))
        self.assertEqual(0x1, self.load_array_byte(0x10F, signed=True))
        self.assertEqual(0x2, self.load_array_byte(0x110, signed=True))
        self.assertEqual(0x4, self.load_array_byte(0x111, signed=True))
        self.assertEqual(0x8, self.load_array_byte(0x112, signed=True))
        self.assertEqual(0xF, self.load_array_byte(0x113, signed=True))
        self.assertEqual(-23, self.load_array_byte(0x114, signed=True))

    def test_invalid_command_throws_error(self):
        program = """
            ORG 100
            FOO
            END
        """
        assembler = Assembler(program, 4096, 16)
        with self.assertRaises(SyntaxError):
            array = assembler.assembled
            print(array)


if __name__ == '__main__':
    unittest.main()
