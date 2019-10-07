# pyOCD debugger
# Copyright (c) 2018-2019 Arm Limited
# Copyright (c) 2017 NXP
# Copyright (c) 2016 Freescale Semiconductor, Inc.
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

RCM_MR = 0x4007f010
RCM_MR_BOOTROM_MASK = 0x6

FLASH_ALGO = {
    'load_address' : 0x20000000,
    'instructions' : [
    0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
    0x4829b510, 0x60414927, 0x60814928, 0x22806801, 0x22204391, 0x60014311, 0x44484825, 0xf84cf000,
    0xd0002800, 0xbd102001, 0x47702000, 0xb5104820, 0x44484920, 0xf88ef000, 0xd1042800, 0x2100481c,
    0xf0004448, 0xbd10f948, 0x4c19b570, 0x444c4605, 0x4b184601, 0x68e24620, 0xf8b5f000, 0xd1052800,
    0x46292300, 0x68e24620, 0xf93ff000, 0xb570bd70, 0x460b460c, 0x46014606, 0xb084480d, 0x44484615,
    0xf8e4f000, 0xd10a2800, 0x90029001, 0x48082101, 0x462b9100, 0x46314622, 0xf0004448, 0xb004f96d,
    0x0000bd70, 0xd928c520, 0x40052000, 0x0000ffff, 0x00000004, 0x6b65666b, 0xd00b2800, 0x68c949dd,
    0x0f090109, 0xd007290f, 0x00494adb, 0x5a51447a, 0xe0030289, 0x47702004, 0x04892101, 0x2300b430,
    0x60416003, 0x02cc2101, 0x608160c4, 0x7a0d49d3, 0x40aa158a, 0x7ac96142, 0x61816103, 0x06892105,
    0x62016244, 0x2000bc30, 0x28004770, 0x6101d002, 0x47702000, 0x47702004, 0x48c94602, 0x210168c0,
    0x43080289, 0x60c849c6, 0x48c64770, 0x70012170, 0x70012180, 0x06097801, 0x7800d5fc, 0xd5010681,
    0x47702067, 0xd50106c1, 0x47702068, 0xd0fc07c0, 0x47702069, 0xd1012800, 0x47702004, 0x4604b510,
    0x48b94ab8, 0x48b96050, 0xd0014281, 0xe000206b, 0x28002000, 0x4620d107, 0xffd7f7ff, 0x46204603,
    0xffcaf7ff, 0xbd104618, 0xd1012800, 0x47702004, 0x4614b510, 0x60622200, 0x60e260a2, 0x61626122,
    0x61e261a2, 0x68c16021, 0x68816061, 0xf0006840, 0x60a0f953, 0x60e02008, 0x61606120, 0x200461a0,
    0x200061e0, 0xb5ffbd10, 0x4615b089, 0x466a460c, 0xf7ff9809, 0x462affd9, 0x9b044621, 0xf0009809,
    0x0007f90c, 0x9c00d130, 0x19659e01, 0x46311e6d, 0xf0004628, 0x2900f931, 0x1c40d002, 0x1e454370,
    0xd81d42ac, 0x20090221, 0x06000a09, 0x488d1809, 0x498e6041, 0x4288980c, 0x206bd001, 0x2000e000,
    0xd1112800, 0xf7ff9809, 0x4607ff80, 0x69009809, 0xd0002800, 0x2f004780, 0x19a4d102, 0xd9e142ac,
    0xf7ff9809, 0x4638ff69, 0xbdf0b00d, 0xd1012a00, 0x47702004, 0xb089b5ff, 0x461e4614, 0x466a460d,
    0xf7ff9809, 0x4632ff91, 0x9b034629, 0xf0009809, 0x0007f8c4, 0x9d00d12d, 0xd0262e00, 0x4871cc02,
    0x99036081, 0xd0022904, 0xd0072908, 0x022ae00e, 0x0a122103, 0x18510649, 0xe0076041, 0x60c1cc02,
    0x2107022a, 0x06090a12, 0x60411851, 0xf7ff9809, 0x4607ff3c, 0x69009809, 0xd0002800, 0x2f004780,
    0x9803d103, 0x1a361945, 0x9809d1d8, 0xff24f7ff, 0xb00d4638, 0x2800bdf0, 0x4a5dd005, 0x18890409,
    0x60514a58, 0x2004e721, 0xb5ff4770, 0x4614b08b, 0x460d461e, 0x980b466a, 0xff46f7ff, 0x46294622,
    0x980b9b05, 0xf879f000, 0xd1332800, 0x4629466a, 0xf7ff980b, 0x9d00ff39, 0x90089802, 0x42404269,
    0x424f4001, 0xd10142af, 0x183f9808, 0xd0202c00, 0x90090230, 0x42a61b7e, 0x4626d900, 0x99054630,
    0xf88af000, 0x2101022a, 0x06090a12, 0x493d1852, 0x9a09604a, 0x43100400, 0x608830ff, 0xf7ff980b,
    0x2800fee4, 0x9808d106, 0x19ad1ba4, 0x2c00183f, 0x2000d1e0, 0xbdf0b00f, 0xd1012b00, 0x47702004,
    0xb089b5ff, 0x461d4616, 0x466a460c, 0x98099f12, 0xfefaf7ff, 0x46214632, 0x98099b07, 0xf82df000,
    0xd11d2800, 0x2e009c00, 0x492ad01a, 0x18470638, 0x20010221, 0x06400a09, 0x48221809, 0x60876041,
    0x60c16829, 0xf7ff9809, 0x2800feb0, 0x9913d00a, 0xd0002900, 0x9914600c, 0xd0012900, 0x600a2200,
    0xbdf0b00d, 0x1a769907, 0x00890889, 0x9907194d, 0x2e00190c, 0xb00dd1dc, 0x2800bdf0, 0x2004d101,
    0xb4104770, 0x460c1e5b, 0xd101421c, 0xd002421a, 0x2065bc10, 0x68034770, 0xd804428b, 0x18896840,
    0x42881818, 0xbc10d202, 0x47702066, 0x2000bc10, 0x00004770, 0x40048040, 0x000003bc, 0x40020020,
    0xf0003000, 0x40020000, 0x44ffffff, 0x6b65666b, 0x4000ffff, 0x00ffffff, 0x460bb530, 0x20004601,
    0x24012220, 0x460de009, 0x429d40d5, 0x461dd305, 0x1b494095, 0x40954625, 0x46151940, 0x2d001e52,
    0xbd30dcf1, 0x40020004, 0x40020010, 0x00100008, 0x00200018, 0x00400030, 0x00800060, 0x010000c0,
    0x02000180, 0x04000300, 0x00000600, 0x00000000,
    ],

    'pc_init' : 0x20000021,
    'pc_unInit': 0x20000049,
    'pc_program_page': 0x2000008F,
    'pc_erase_sector': 0x20000069,
    'pc_eraseAll' : 0x2000004D,

    'static_base' : 0x20000000 + 0x00000020 + 0x000004ac,
    'begin_stack' : 0x20000000 + 0x00000800,
    'begin_data' : 0x20000000 + 0x00000A00,
    'page_size' : 0x00000800,
    'analyzer_supported' : True,
    'analyzer_address' : 0x1ffff000,  # Analyzer 0x1ffff000..0x1ffff600
    'page_buffers' : [0x20003000, 0x20004000],   # Enable double buffering
    'min_program_length' : 8,
}

class KE15Z7(Kinetis):

    memoryMap = MemoryMap(
        FlashRegion(    start=0,           length=0x40000,       blocksize=0x800, is_boot_memory=True,
            algo=FLASH_ALGO, flash_class=Flash_Kinetis),
        RamRegion(      start=0x1fffe000,  length=0x8000)
        )

    def __init__(self, link):
        super(KE15Z7, self).__init__(link, self.memoryMap)
        self._svd_location = SVDFile.from_builtin("MKE15Z7.svd")

    def create_init_sequence(self):
        seq = super(KE15Z7, self).create_init_sequence()

        seq.insert_after('create_cores',
            ('disable_rom_remap', self.disable_rom_remap)
            )

        return seq

    def disable_rom_remap(self):
        # Disable ROM vector table remapping.
        self.write32(RCM_MR, RCM_MR_BOOTROM_MASK)

