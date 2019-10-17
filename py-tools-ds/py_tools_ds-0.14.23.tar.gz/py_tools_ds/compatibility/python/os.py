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

from __future__ import absolute_import
import os
import errno
from six import PY3

__author__ = "Daniel Scheffler"


def makedirs(name, exist_ok=False, **kwargs):
    if PY3:
        os.makedirs(name, exist_ok=exist_ok, **kwargs)
    else:
        try:
            os.makedirs(name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
