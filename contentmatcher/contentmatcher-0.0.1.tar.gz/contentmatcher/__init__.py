#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2019 Brandon M. Pace
#
# This file is part of contentmatcher
#
# contentmatcher is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# contentmatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with contentmatcher.
# If not, see <https://www.gnu.org/licenses/>.

"""
The contentmatcher package provides a way to identify how much of a pattern is matched in other content.
It was originally created to match a list of function names extracted from a backtrace against known patterns.
"""


__author__ = "Brandon M. Pace"
__copyright__ = "Copyright 2019, Brandon M. Pace"
__license__ = "GNU LGPL 3+"
__maintainer__ = "Brandon M. Pace"
__status__ = "Development"
__version__ = "0.0.1"


from .classes import Pattern
