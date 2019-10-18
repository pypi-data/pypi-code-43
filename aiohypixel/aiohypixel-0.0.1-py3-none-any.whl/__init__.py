#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Tmpod 2019
#
# This file is part of aiohypixel.
#
# aiohypixel is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aiohypixel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with aiohypixel. If not, see <https://www.gnu.org/licenses/>.
"""
This is an asynchronous Hypixel API wrapper written in Python.
Compatible with Python3.6 and up

NOTE: It's highly recommended that you setup logging for this module! A lot of
info that you may not want to miss is reported through there. Doing it for
aiohttp might also be a good idea (INFO level is generaly enough).
"""

# TODO: Add documentation to all models' fields.

from . import shared, session, player, guild, keys, boosters, friends, watchdogstats, stats

from .session import *
from .shared import *
from .player import *
from .stats import *
from .guild import *
from .boosters import *
from .keys import *
from .friends import *
from .watchdogstats import *
from .leaderboards import *
from .resources import *
from .skyblock import *


__author__ = "Tmpod"
__url__ = f"https://gitlab.com/{__author__}/aiohypixel/"
__version__ = "0.0.1"
__licence__ = "LGPL-3.0"
__copyright__ = f"Copyright (c) 2018-2019 {__author__}"
