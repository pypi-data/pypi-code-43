# File Version : 2.3.0.106
# Flash OS Routines (Automagically Generated)
# Copyright (c) 2017-2019 ARM Limited
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


flash_algo = {
    'load_address' : 0x08000000,

    # Flash algorithm as a hex string
    'instructions': [
    0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
    0x4603b510, 0xbd102000, 0x20004601, 0xb5104770, 0xf0002400, 0x4604fabc, 0xbd104620, 0x4604b570,
    0x46202500, 0xfabdf000, 0x46284605, 0xb5f8bd70, 0x460f4605, 0x26004614, 0x46284621, 0xfabaf000,
    0x46304606, 0xb5f8bdf8, 0x460d4604, 0x46274616, 0x46294632, 0xf0004620, 0x4607fac9, 0xbdf84638,
    0x4604b5f8, 0x4616460d, 0x46322700, 0x46204629, 0xfad3f000, 0x46384607, 0x0000bdf8, 0x47706001,
    0x600a6802, 0x21004770, 0x1c49e000, 0x43424a12, 0xd8fa428a, 0xb5304770, 0x460b4602, 0xe014480f,
    0x1c527815, 0x4060022c, 0xe00c2100, 0x03e42401, 0x2c004004, 0x0044d003, 0x406c4d09, 0x0044e000,
    0x1c4cb2a0, 0x2908b2e1, 0x461cdbf0, 0xb2ab1e5d, 0xd1e52c00, 0x0000bd30, 0x00000d05, 0x0000ffff,
    0x00001021, 0x4669b538, 0xf7ff483e, 0x210fffc9, 0x98000209, 0x28004008, 0x2001d101, 0x2000e000,
    0x46204604, 0xb510bd38, 0x4837b08a, 0x78004448, 0xd15f2800, 0xffe6f7ff, 0x40482101, 0x44494932,
    0xa8037208, 0xaa05a904, 0x9200ab06, 0x90029101, 0xa908aa07, 0xf000a809, 0x4604f93f, 0xd1482c00,
    0x7900a808, 0x44494928, 0xa8087048, 0x70887800, 0x7f004668, 0x466870c8, 0x71087e00, 0x7d004668,
    0x46687148, 0x71887c00, 0x7b004668, 0x20ff71c8, 0x46087248, 0x28017840, 0x4608d127, 0x28007880,
    0x4608d106, 0x28e278c0, 0x2000d102, 0xe01c7248, 0x44484815, 0x28027880, 0x4813d109, 0x78c04448,
    0xd10428e4, 0x49102002, 0x72484449, 0x480ee00d, 0x78804448, 0xd1082805, 0x4448480b, 0x28e778c0,
    0x2005d103, 0x44494908, 0x20017248, 0x44494906, 0xbf007008, 0x44484804, 0xbd10b00a, 0x44484802,
    0x47707800, 0x40210400, 0xfffff9e0, 0xb085b5f0, 0x460c4606, 0x20004617, 0x25009003, 0x49cf0170,
    0x90011840, 0x2000bf00, 0xa9029000, 0x30109801, 0xff36f7ff, 0x0fc09802, 0x2c009000, 0x9800d002,
    0xd1042800, 0xd1042c00, 0x28009800, 0x2001d101, 0x2000e000, 0x2d004605, 0x9803d109, 0xd90042b8,
    0x2001e007, 0xff1ff7ff, 0x1c409803, 0x2d009003, 0xbf00d0d9, 0x21014628, 0xb0054048, 0xb5febdf0,
    0x460e4605, 0x24002700, 0x49b40168, 0x90011840, 0x4669bf00, 0xf7ff9801, 0x9800ff03, 0x2c000fc4,
    0x42b7d106, 0xe005d900, 0xf7ff2001, 0x1c7ffefc, 0xd0ee2c00, 0x4620bf00, 0x40482101, 0xb5f7bdfe,
    0x4614460e, 0x25002700, 0x4621bf00, 0xf7ff9800, 0x6820fee7, 0x07000f00, 0x07492105, 0xd1014288,
    0xe0002001, 0x46052000, 0xd1062d00, 0xd90042b7, 0x2001e005, 0xfed7f7ff, 0x2d001c7f, 0xbf00d0e5,
    0x21014628, 0xbdfe4048, 0xb083b5f3, 0x24004607, 0xf7ff2600, 0x2800ff73, 0xf7ffd003, 0x7a00ff04,
    0xf7ffe003, 0x2101feef, 0x90024048, 0x28009802, 0x2500d102, 0xe0074e89, 0x28019802, 0x2501d103,
    0x36204e86, 0x2401e000, 0xd1422c00, 0x00c9217d, 0xf7ff4628, 0x4604ff94, 0xd13a2c00, 0x0fc007f8,
    0x40482101, 0x98019001, 0xd0022800, 0x4478487c, 0x4638e000, 0x46309000, 0x9900300c, 0xfe8ef7ff,
    0x30104628, 0x40822201, 0x48764611, 0xfe86f7ff, 0x46302101, 0xf7ff3008, 0x4a73fe81, 0x46282100,
    0xff34f7ff, 0x2c004604, 0x9801d112, 0xd0072800, 0x31f521ff, 0x98009a04, 0xff81f7ff, 0xe0074604,
    0x31f521ff, 0x300c4630, 0xf7ff9a04, 0x4604ff78, 0x4620bf00, 0xbdf0b005, 0xb083b5ff, 0x460e4605,
    0x20004617, 0x99019001, 0xa9021c48, 0xff8cf7ff, 0x2c004604, 0x21ffd131, 0x98020209, 0x0a004008,
    0x98027028, 0x02097030, 0x40089802, 0x980c0c01, 0x20ff7001, 0x90013001, 0x1c489901, 0xf7ff4669,
    0x4604ff73, 0xd1172c00, 0x020921ff, 0x40089800, 0x70380a00, 0xb2c19800, 0x70019806, 0x0409210f,
    0x40089800, 0x980d0c01, 0x210f7001, 0x98000509, 0x0d014008, 0x7001980e, 0x4620bf00, 0xbdf0b007,
    0x4942b508, 0x4478483e, 0xf7ff38f8, 0x4669fe17, 0xf7ff483e, 0xbd08ff49, 0x4604b538, 0x447d4d3c,
    0x4628493c, 0xfe0af7ff, 0x1d284621, 0xfe06f7ff, 0x48384669, 0xff38f7ff, 0xb538bd38, 0x4d344604,
    0x3d22447d, 0x46284934, 0xfdf8f7ff, 0x1d284621, 0xfdf4f7ff, 0x48304669, 0xff26f7ff, 0xb538bd38,
    0x4d2b4604, 0x3d46447d, 0x4628492b, 0xfde6f7ff, 0x1d284621, 0xfde2f7ff, 0x48274669, 0xff14f7ff,
    0xb5f8bd38, 0x460e4605, 0x447c4c21, 0x49233c6c, 0xf7ff4620, 0x21fffdd3, 0x1d203107, 0xfdcef7ff,
    0x46204629, 0xf7ff3008, 0x4631fdc9, 0x300c4620, 0xfdc4f7ff, 0x48194669, 0xfef6f7ff, 0xb5f8bdf8,
    0x460e4605, 0x447c4c12, 0x49153ca8, 0xf7ff4620, 0x21fffdb5, 0x1d203107, 0xfdb0f7ff, 0x46204629,
    0xf7ff3008, 0x4631fdab, 0x300c4620, 0xfda6f7ff, 0x480b4669, 0xfed8f7ff, 0x0000bdf8, 0x40230000,
    0x0000033e, 0x40231008, 0x00003a98, 0x0a000100, 0x0000022e, 0x1c000100, 0x14000100, 0x06000100,
    0x05000100, 0x4606b570, 0x2500460c, 0x4630e00a, 0xff72f7ff, 0x2d004605, 0xe005d000, 0x36ff36ff,
    0x1e643602, 0xd1f22c00, 0x4628bf00, 0xb510bd70, 0x21402400, 0x06802005, 0xffe4f7ff, 0x46204604,
    0xb570bd10, 0x25004604, 0xf7ff4620, 0x4605ff55, 0xbd704628, 0x4604b570, 0x2600460d, 0x46204629,
    0xff7ff7ff, 0x46304606, 0xb570bd70, 0x21014604, 0x481b0249, 0xf0004478, 0x4919f853, 0x39084479,
    0xf7ff4620, 0x4605ff8c, 0xbd704628, 0x4603b5f8, 0x2100460c, 0x25001858, 0x2d009300, 0xbf00d10c,
    0x5c57e006, 0x5c769e00, 0xd00042b7, 0x1c49e002, 0xd3f642a1, 0x1858bf00, 0xb5f0bdf8, 0x460c4603,
    0x46252000, 0x2100461e, 0x5c77e005, 0xd0014297, 0xe0022001, 0x42a91c49, 0xbf00d3f7, 0x0000bdf0,
    0x000000cc, 0xc004e001, 0x29041f09, 0x078bd2fb, 0x8002d501, 0x07c91c80, 0x7002d000, 0x29004770,
    0x07c3d00b, 0x7002d002, 0x1e491c40, 0xd3042902, 0xd5020783, 0x1c808002, 0xe7e31e89, 0xe7ee2200,
    0xe7df2200, 0xffffff00, 0xffffffff, 0x0000ffff, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x00000000, 0x00000000
    ],

    # Relative function addresses
    'pc_init': 0x08000021,
    'pc_unInit': 0x08000029,
    'pc_program_page': 0x0800004f,
    'pc_erase_sector': 0x0800003d,
    'pc_eraseAll': 0x0800002f,

    'static_base' : 0x08000000 + 0x00000020 + 0x00000ca4,
    'begin_stack' : 0x08002100,
    'begin_data' : 0x08002100 + 0x40,
    'page_size' : 0x200,
    'analyzer_supported' : False,
    'analyzer_address' : 0x00000000,
    'page_buffers' : [0x08002140, 0x08002340],   # Enable double buffering
    'min_program_length' : 0x200,

    # Flash information
    'flash_start': 0x14000000,
    'flash_size': 0x8000,
    'sector_sizes': (
        (0x0, 0x200),
    )
}
