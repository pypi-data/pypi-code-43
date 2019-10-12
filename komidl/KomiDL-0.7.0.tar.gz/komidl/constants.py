# KomiDL - A gallery downloader
# Copyright (C) 2019 DNSheng
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""This module contains constants used by KomiDL"""

VERSION = "0.7.0"

# Length of statusbar
STATUSBAR_LEN = 65

USER_AGENT = "komidl/0.1"

# Default formats provided by shutil
ARCHIVE_FORMATS = {"zip", "tar", "gztar", "bztar"}

# Strictly static image formats, used by the PDF export
IMAGE_FORMATS = {"jpg", "png", "jpeg", "tiff", "bmp", "webp", "svg"}

# Common image/video formats that can be downloaded by KomiDL
# Ordered by expected frequency, thus a tuple is used instead of a set
COMMON_FORMATS = ("jpg", "png", "gif", "gifv", "jpeg", "tiff", "bmp", "webp",
                  "svg")

# ISO 639-1 Codes
LANG_TO_ISO = {"Japanese": "JA", "English": "EN", "Chinese": "ZH",
               "French": "FR", "Spanish": "ES", "Korean": "KR", "German": "DE",
               "Russian": "RU", "Italian": "IT", "Portuguese": "PT"}

# ISO 639-1 Codes to common abbreviations
ISO_LANG_SET = {"ja": ("ja", "jp", "jap",), "en": ("en", "eng", "us", "gb",),
                "zh": ("zh", "cn",), "es": ("es", "mx", "sp",),
                "de": ("de", "ger",), "ru": ("ru", "rus",),
                "pt": ("pt", "br",)}

KOMIDL_LOGO = ("   +++++++++++++++++++++++++++++   \n"
               " +++:-------------------------:+++ \n"
               "+++`.//+++++++++++++++++++++//.`+++\n"
               "++/`+/          `+`          /+`/++\n"
               "++/`++::::::::- `+:::::::::::++`/++\n"
               "++/`++++++++++: `+.          /+`/++\n"
               "++/`++////////- `+:----------++`/++\n"
               "++/`+/          `+.          /+`/++\n"
               "++/`++:::::::::::+:::////////++`/++\n"
               "++/`+/          `+` :++++++++++`/++\n"
               "++/`++--//////- `+` :++++++++++`/++\n"
               "++/`+/  /+++++: `+` :++++++++++`/++\n"
               "++/`+/  ::::::- `+` -::::::::++`/++\n"
               "++/`+/          `+`          /+`/++\n"
               "+++`./+++++++++++++++++++++++/.`+++\n"
               " +++:-------------------------:+++ \n"
               "   +++++++++++++++++++++++++++++   ")
