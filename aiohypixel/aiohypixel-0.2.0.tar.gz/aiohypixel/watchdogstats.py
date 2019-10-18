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
Stuff for the Watchdog Stats endpoint
"""

__all__ = ("WatchdogStats",)

from dataclasses import dataclass

from .shared import APIResponse


@dataclass(frozen=True)
class WatchdogStats:
    total: int
    rolling_daily: int
    last_minute: int
    staff_total: int
    staff_rolling_daily: int

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`WatchdogStats` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`WatchdogStats` object.
        """
        return cls(
            total=resp["watchdog_total"],
            rolling_daily=resp["watchdog_rollingDaily"],
            last_minute=resp["watchdog_lastMinute"],
            staff_total=resp["staff_total"],
            staff_rolling_daily=resp["staff_rollingDaily"],
        )
