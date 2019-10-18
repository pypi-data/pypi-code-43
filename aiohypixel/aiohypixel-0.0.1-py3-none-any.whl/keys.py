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
Stuff for the keys endpoint
"""

__all__ = ("Key",)

from dataclasses import dataclass
from datetime import datetime

from .shared import APIResponse


@dataclass(frozen=True)
class Key:
    owner_uuid: str
    value: str  # The actual key
    total_queries: int
    queries_in_past_min: int

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Key` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Key` object.
        """
        return cls(
            owner_uuid=resp["ownerUuid"],
            value=resp["key"],
            total_queries=resp["totalQueries"],
            queries_in_past_min=resp.get("queriesInPastMin"),
        )
