# -*- coding: utf-8 -*-

# py_tools_ds
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (division, print_function, absolute_import, unicode_literals)
from .version import __version__, __versionalias__   # noqa (E402 + F401)

__author__ = 'Daniel Scheffler'

# Validate GDAL version
try:
    import gdal
    import gdalnumeric
except ImportError:
    from osgeo import gdal
    from osgeo import gdalnumeric

try:
    getattr(gdal, 'Warp')
    getattr(gdal, 'Translate')
    getattr(gdalnumeric, 'OpenNumPyArray')
except AttributeError:
    import warnings
    warnings.warn("Your GDAL version is too old to support all functionalities of the 'py_tools_ds' package. "
                  "Please update GDAL!")
del gdal, gdalnumeric
