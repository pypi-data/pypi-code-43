# -*- coding: utf-8 -*-
# Copyright (c) 2019 by Lars Klitzke, Lars.Klitzke@gmail.com
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from datetime import datetime

from . import location
from . import io
from . import visualization
from . import api
from . import osm

def convert_timestamp(unix_timestamp):
    """
    Convert the given Unix timestamp into a datetime object.

    Args:
        unix_timestamp (str|int):   The timestamp as unix timestamp.

    """

    if isinstance(unix_timestamp, str):
        unix_timestamp = int(unix_timestamp)

    return datetime.utcfromtimestamp(unix_timestamp / 1E6)
