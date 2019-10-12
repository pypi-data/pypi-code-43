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
"""This module will generate a list of all extractor instances for KomiDL"""

from .extractors import *

_ALL_CLASSES = [
    klass
    for name, klass in globals().items()
    if name.endswith("EX")
]


def _gen_extractor_classes():
    return _ALL_CLASSES


def get_extractors():
    """Return a list of all extractors"""
    return [klass() for klass in _gen_extractor_classes()]
