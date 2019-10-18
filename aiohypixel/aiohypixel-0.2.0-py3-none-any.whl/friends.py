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
Stuff for the friends endpoint
"""

__all__ = ("Friend",)

from dataclasses import dataclass
from datetime import datetime

from .shared import APIResponse, HypixelModel


@dataclass(frozen=True)
class Friend(HypixelModel):
    sender_uuid: str
    receiver_uuid: str
    started_at: datetime

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Friend` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Friend` object.
        """
        return cls(
            sender_uuid=resp["uuidSender"],
            receiver_uuid=resp["uuidReceiver"],
            started_at=datetime.utcfromtimestamp(resp["started"] / 1000),
        )
