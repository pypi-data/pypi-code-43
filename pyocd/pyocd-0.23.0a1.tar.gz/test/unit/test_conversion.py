# mbed CMSIS-DAP debugger
# Copyright (c) 2015 Paul Osborne <osbpau@gmail.com>
# Copyright (c) 2018-2019 Arm Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyocd.utility.conversion import (
    byte_list_to_u32le_list,
    u32le_list_to_byte_list,
    u16le_list_to_byte_list,
    byte_list_to_u16le_list,
    u32_to_float32,
    float32_to_u32,
    u32_to_hex8le,
    u64_to_hex16le,
    hex8_to_u32be,
    hex16_to_u64be,
    hex8_to_u32le,
    hex16_to_u64le,
    byte_to_hex2,
    hex_to_byte_list,
    hex_decode,
    hex_encode,
)
from pyocd.utility.mask import align_up
from pyocd.gdbserver.gdbserver import (
    escape,
    unescape,
)
import pytest
import six

# pylint: disable=invalid-name
class TestConversionUtilities(object):
    def test_byte_list_to_u32le_list_empty(self):
        assert byte_list_to_u32le_list([]) == []
        
    def test_byteListToU32leList(self):
        data = range(32)
        assert byte_list_to_u32le_list(data) == [
            0x03020100,
            0x07060504,
            0x0B0A0908,
            0x0F0E0D0C,
            0x13121110,
            0x17161514,
            0x1B1A1918,
            0x1F1E1D1C,
        ]
    
    def test_byte_list_to_u32le_list_unaligned(self):
        assert byte_list_to_u32le_list([1]) == [0x00000001]
        assert byte_list_to_u32le_list([1, 2, 3]) == [0x00030201]
        assert byte_list_to_u32le_list([1, 2, 3, 4, 5]) == [0x04030201, 0x00000005]

        assert byte_list_to_u32le_list([1], pad=0xcc) == [0xcccccc01]
        assert byte_list_to_u32le_list([1, 2, 3], pad=0xdd) == [0xdd030201]
        assert byte_list_to_u32le_list([1, 2, 3, 4, 5], pad=0xff) == [0x04030201, 0xffffff05]

    def test_byte_list_to_u32le_list_bytearray(self):
        assert byte_list_to_u32le_list(bytearray(b'abcd')) == [0x64636261]
        assert byte_list_to_u32le_list(bytearray(b'a')) == [0x00000061]

    def test_u32leListToByteList(self):
        data = [
            0x03020100,
            0x07060504,
            0x0B0A0908,
            0x0F0E0D0C,
            0x13121110,
            0x17161514,
            0x1B1A1918,
            0x1F1E1D1C,
        ]
        assert u32le_list_to_byte_list(data) == list(range(32))

    def test_u16leListToByteList(self):
        data = [0x3412, 0xFEAB]
        assert u16le_list_to_byte_list(data) == [
            0x12,
            0x34,
            0xAB,
            0xFE
        ]

    def test_byteListToU16leList(self):
        data = [0x01, 0x00, 0xAB, 0xCD, ]
        assert byte_list_to_u16le_list(data) == [
            0x0001,
            0xCDAB,
        ]

    def test_u32BEToFloat32BE(self):
        assert u32_to_float32(0x012345678) == 5.690456613903524e-28

    def test_float32beToU32be(self):
        assert float32_to_u32(5.690456613903524e-28) == 0x012345678

    def test_u32ToHex8le(self):
        assert u32_to_hex8le(0x0102ABCD) == "cdab0201"

    def test_u64ToHex16le(self):
        assert u64_to_hex16le(0x0102ABCD171819EF) == "ef191817cdab0201"

    def test_hex8ToU32be(self):
        assert hex8_to_u32be("0102ABCD") == 0xCDAB0201

    def test_hex16ToU64be(self):
        assert hex16_to_u64be("0102ABCD171819EF") == 0xEF191817CDAB0201

    def test_hex8ToU32le(self):
        assert hex8_to_u32le("0102ABCD") == 0x0102ABCD

    def test_hex16ToU64le(self):
        assert hex16_to_u64le("0102ABCD171819EF") == 0x0102ABCD171819EF

    def test_byteToHex2(self):
        assert byte_to_hex2(0xC3) == "c3"

    def test_hexToByteList(self):
        assert hex_to_byte_list("ABCDEF1234") == [0xAB, 0xCD, 0xEF, 0x12, 0x34]

    def test_hexDecode(self):
        assert hex_decode('ABCDEF1234') == b'\xab\xcd\xef\x12\x34'

    def test_hexEncode(self):
        assert hex_encode(b'\xab\xcd\xef\x12\x34') == b'abcdef1234'

    @pytest.mark.parametrize(("args", "result"), [
            ((0, 1024), 0),
            ((1, 1024), 1024),
            ((0, 3), 0),
            ((100, 3), 102),
        ])
    def test_align_up(self, args, result):
        assert result == align_up(*args)

# Characters that must be escaped.
ESCAPEES = (0x23, 0x24, 0x2a, 0x7d) # == ('#', '$', '}', '*')

# Test the gdbserver binary data escape/unescape routines.
class TestGdbEscape(object):
    # Verify all chars that shouldn't be escaped pass through unmodified.
    @pytest.mark.parametrize("data",
        [six.int2byte(x) for x in range(256) if (x not in ESCAPEES)])
    def test_escape_passthrough(self, data):
        assert escape(data) == data
    
    @pytest.mark.parametrize(("data", "expected"), [
            (b'#', b'}\x03'),
            (b'$', b'}\x04'),
            (b'}', b'}]'),
            (b'*', b'}\x0a')
        ])
    def test_escape_1(self, data, expected):
        assert escape(data) == expected
    
    def test_escape_2(self):
        assert escape(b'1234#09*xyz') == b'1234}\x0309}\x0axyz'
    
    # Verify all chars that shouldn't be escaped pass through unmodified.
    @pytest.mark.parametrize("data",
        [six.int2byte(x) for x in range(256) if (x not in ESCAPEES)])
    def test_unescape_passthrough(self, data):
        assert unescape(data) == [six.byte2int(data)]
    
    @pytest.mark.parametrize(("expected", "data"), [
            (0x23, b'}\x03'),
            (0x24, b'}\x04'),
            (0x7d, b'}]'),
            (0x2a, b'}\x0a')
        ])
    def test_unescape_1(self, data, expected):
        assert unescape(data) == [expected]
    
    def test_unescape_2(self):
        assert unescape(b'1234}\x0309}\x0axyz') == \
            [0x31, 0x32, 0x33, 0x34, 0x23, 0x30, 0x39, 0x2a, 0x78, 0x79, 0x7a]
