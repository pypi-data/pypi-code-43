# pyOCD debugger
# Copyright (c) 2006-2013,2018 Arm Limited
# SPDX-License-Identifier: Apache-2.0
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

from ..family.target_kinetis import Kinetis
from ..family.flash_kinetis import Flash_Kinetis
from ...core.memory_map import (FlashRegion, RamRegion, MemoryMap)
from ...debug.svd.loader import SVDFile

FLASH_ALGO = { 'load_address' : 0x20000000,
               'instructions' : [
    0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
    0x09032200, 0xd373428b, 0x428b0a03, 0x0b03d358, 0xd33c428b, 0x428b0c03, 0xe012d321, 0x430b4603,
    0x2200d47f, 0x428b0843, 0x0903d374, 0xd35f428b, 0x428b0a03, 0x0b03d344, 0xd328428b, 0x428b0c03,
    0x22ffd30d, 0xba120209, 0x428b0c03, 0x1212d302, 0xd0650209, 0x428b0b03, 0xe000d319, 0x0bc30a09,
    0xd301428b, 0x1ac003cb, 0x0b834152, 0xd301428b, 0x1ac0038b, 0x0b434152, 0xd301428b, 0x1ac0034b,
    0x0b034152, 0xd301428b, 0x1ac0030b, 0x0ac34152, 0xd301428b, 0x1ac002cb, 0x0a834152, 0xd301428b,
    0x1ac0028b, 0x0a434152, 0xd301428b, 0x1ac0024b, 0x0a034152, 0xd301428b, 0x1ac0020b, 0xd2cd4152,
    0x428b09c3, 0x01cbd301, 0x41521ac0, 0x428b0983, 0x018bd301, 0x41521ac0, 0x428b0943, 0x014bd301,
    0x41521ac0, 0x428b0903, 0x010bd301, 0x41521ac0, 0x428b08c3, 0x00cbd301, 0x41521ac0, 0x428b0883,
    0x008bd301, 0x41521ac0, 0x428b0843, 0x004bd301, 0x41521ac0, 0xd2001a41, 0x41524601, 0x47704610,
    0x0fcae05d, 0x4249d000, 0xd3001003, 0x40534240, 0x469c2200, 0x428b0903, 0x0a03d32d, 0xd312428b,
    0x018922fc, 0x0a03ba12, 0xd30c428b, 0x11920189, 0xd308428b, 0x11920189, 0xd304428b, 0xd03a0189,
    0xe0001192, 0x09c30989, 0xd301428b, 0x1ac001cb, 0x09834152, 0xd301428b, 0x1ac0018b, 0x09434152,
    0xd301428b, 0x1ac0014b, 0x09034152, 0xd301428b, 0x1ac0010b, 0x08c34152, 0xd301428b, 0x1ac000cb,
    0x08834152, 0xd301428b, 0x1ac0008b, 0xd2d94152, 0x428b0843, 0x004bd301, 0x41521ac0, 0xd2001a41,
    0x46634601, 0x105b4152, 0xd3014610, 0x2b004240, 0x4249d500, 0x46634770, 0xd300105b, 0xb5014240,
    0x46c02000, 0xbd0246c0, 0xb510480a, 0x44484908, 0xf8ecf000, 0xd1042800, 0x21004806, 0xf0004448,
    0x4a05f9b1, 0x230168d1, 0x4319029b, 0xbd1060d1, 0x6b65666b, 0x00000004, 0xf0003000, 0x4c0cb570,
    0x444c4605, 0x4b0b4601, 0x68e24620, 0xf894f000, 0xd1052800, 0x46292300, 0x68e24620, 0xf956f000,
    0x68ca4905, 0x029b2301, 0x60ca431a, 0x0000bd70, 0x00000004, 0x6b65666b, 0xf0003000, 0x4905b510,
    0x60082000, 0x44484804, 0xf8e8f000, 0xd0002800, 0xbd102001, 0x40048100, 0x00000004, 0x460cb570,
    0x4606460b, 0x480d4601, 0x4615b084, 0xf0004448, 0x2800f8f5, 0x9001d10a, 0x21019002, 0x91004807,
    0x4622462b, 0x44484631, 0xf96af000, 0x68ca4904, 0x029b2301, 0x60ca431a, 0xbd70b004, 0x00000004,
    0xf0003000, 0x47702000, 0xd0032800, 0xd801290f, 0xd0012a04, 0x47702004, 0x47702000, 0xd1012800,
    0x47702004, 0x1e5bb410, 0x421c460c, 0x421ad101, 0xbc10d002, 0x47702065, 0x428b6803, 0x6840d804,
    0x18181889, 0xd2024288, 0x2066bc10, 0xbc104770, 0x47702000, 0x42884903, 0x206bd001, 0x20004770,
    0x00004770, 0x6b65666b, 0x2170480a, 0x21807001, 0x78017001, 0xd5fc0609, 0x06817800, 0x2067d501,
    0x06c14770, 0x2068d501, 0x07c04770, 0x2069d0fc, 0x00004770, 0x40020000, 0x4605b5f8, 0x460c4616,
    0xf7ff4618, 0x2800ffd7, 0x2304d12b, 0x46214632, 0xf7ff4628, 0x0007ffb3, 0x19a6d123, 0x68e91e76,
    0x91004630, 0xfe3cf7ff, 0xd0032900, 0x1c409e00, 0x1e764346, 0xd81342b4, 0x4478480a, 0x60046800,
    0x20094909, 0xf7ff71c8, 0x4607ffbf, 0x280069a8, 0x4780d000, 0xd1032f00, 0x190468e8, 0xd9eb42b4,
    0xbdf84638, 0x0000026a, 0x40020000, 0x4604b510, 0xf7ff4608, 0x2800ff9f, 0x2c00d106, 0x4904d005,
    0x71c82044, 0xffa0f7ff, 0x2004bd10, 0x0000bd10, 0x40020000, 0xd00c2800, 0xd00a2a00, 0xd21a2908,
    0x447b000b, 0x18db791b, 0x0705449f, 0x0d0b0907, 0x2004110f, 0x68c04770, 0x6840e00a, 0x6880e008,
    0x6800e006, 0x2000e004, 0x6900e002, 0x6940e000, 0x20006010, 0x206a4770, 0x00004770, 0xd0142800,
    0x68c9490c, 0x0e094a0c, 0x447a0049, 0x03095a51, 0x2200d00d, 0x60416002, 0x60812102, 0x61426102,
    0x61820249, 0x461060c1, 0x20044770, 0x20644770, 0x00004770, 0x40048040, 0x0000019a, 0xd1012a00,
    0x47702004, 0x461cb5ff, 0x4615b081, 0x2304460e, 0x98014622, 0xff22f7ff, 0xd1190007, 0xd0162c00,
    0x4478480c, 0x600e6801, 0x6800cd02, 0x490a6041, 0x71c82006, 0xff38f7ff, 0x98014607, 0x28006980,
    0x4780d000, 0xd1022f00, 0x1f241d36, 0x4638d1e8, 0xbdf0b005, 0x00000162, 0x40020000, 0xd0022800,
    0x20006181, 0x20044770, 0x00004770, 0xb081b5ff, 0x460e4614, 0x23044605, 0xfef0f7ff, 0xd12a2800,
    0x686868a9, 0xfd7cf7ff, 0x42719000, 0x40014240, 0x42b7424f, 0x9800d101, 0x2c00183f, 0x1bbdd01a,
    0xd90042a5, 0x490d4625, 0x447908a8, 0x600e6809, 0x2201490b, 0x0a0271ca, 0x728872ca, 0x72489804,
    0xfef2f7ff, 0xd1062800, 0x1b649800, 0x183f1976, 0xd1e42c00, 0xb0052000, 0x0000bdf0, 0x000000da,
    0x40020000, 0xd1012800, 0x47702004, 0x4803b510, 0x71c22240, 0xf7ff7181, 0xbd10fed7, 0x40020000,
    0xd1012b00, 0x47702004, 0x461cb5f8, 0x460e4615, 0x9f082304, 0xfea2f7ff, 0xd1192800, 0xd0172d00,
    0x447a4a0f, 0x60066810, 0x2102480e, 0x990671c1, 0x681172c1, 0x60886820, 0xfeb6f7ff, 0xd0082800,
    0x29009907, 0x600ed000, 0xd0012f00, 0x60392100, 0x1f2dbdf8, 0x1d361d24, 0xd1e12d00, 0x0000bdf8,
    0x00000062, 0x40020000, 0x00040002, 0x00080000, 0x00100000, 0x00200000, 0x00400000, 0x00000000,
    0x00000000, 0x00200000, 0x40020004, 0x00000000,
    ],

    'pc_init' : 0x2000027D,
    'pc_unInit': 0x200002E5,
    'pc_program_page': 0x2000029D,
    'pc_erase_sector': 0x2000023D,
    'pc_eraseAll' : 0x20000209,

    'static_base' : 0x20000000 + 0x00000020 + 0x0000060c,
    'begin_stack' : 0x20000000 + 0x00000800,
    'begin_data' : 0x20000000 + 0x00000A00,
    'page_buffers' : [0x20000a00, 0x20001200],   # Enable double buffering
    'min_program_length' : 4,
    'analyzer_supported' : True,
    'analyzer_address' : 0x1ffff800
  }

class KW01Z4(Kinetis):

    memoryMap = MemoryMap(
        FlashRegion(    start=0,           length=0x20000,      blocksize=0x400, is_boot_memory=True,
            algo=FLASH_ALGO, flash_class=Flash_Kinetis),
        RamRegion(      start=0x1ffff000,  length=0x4000)
        )

    def __init__(self, transport):
        super(KW01Z4, self).__init__(transport, self.memoryMap)
        self._svd_location = SVDFile.from_builtin("MKW01Z4.svd")

