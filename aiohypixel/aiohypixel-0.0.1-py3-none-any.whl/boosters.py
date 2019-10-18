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
Stuff for the boosters endpoint
"""

__all__ = ("Booster",)

from dataclasses import dataclass
from datetime import datetime
from typing import Union, Tuple

from .shared import APIResponse, GAME_TYPES_TABLE, HypixelModel


@dataclass(frozen=True)
class Booster(HypixelModel):
    """
    Represents a 
    """

    purchaser_uuid: str
    amount: int
    original_length: int
    current_length: int
    game_type: int
    game: str
    activated_at: datetime
    stacked: Union[bool, Tuple[str], None]  # not sure what this is... I'll get back here soon

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Booster` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Booster` object.
        """
        return cls(
            purchaser_uuid=resp["purchaserUuid"],
            amount=resp["amount"],
            original_length=resp["originalLength"],
            current_length=resp["length"],
            game_type=resp["gameType"],
            game=GAME_TYPES_TABLE.get(resp["gameType"]),
            activated_at=datetime.utcfromtimestamp(resp["dateActivated"] / 1000),
            stacked=resp.get("stacked"),
        )
