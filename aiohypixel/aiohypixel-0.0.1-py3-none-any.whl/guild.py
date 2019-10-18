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
Custom classes that are related to guild lookups on the Hypixel API
"""

__all__ = ("Guild", "GuildRank", "GuildMember", "GuildTag")

from dataclasses import dataclass
from datetime import datetime
from typing import Union, Dict, Tuple, List

from .shared import APIResponse, HypixelModel

LVL_EXP_NEEDED = [
    100000,
    150000,
    250000,
    500000,
    750000,
    1000000,
    1250000,
    1500000,
    2000000,
    2500000,
    2500000,
    2500000,
    2500000,
    2500000,
    3000000,
]


def get_guild_level(exp: int) -> int:
    level = 0
    i = 0
    while True:
        need = LVL_EXP_NEEDED[i]
        exp -= need

        if exp < 0:
            return level

        level += 1

        if i < len(LVL_EXP_NEEDED) - 1:
            i += 1


@dataclass(frozen=True)
class GuildRank(HypixelModel):
    name: str
    default: bool
    tag: Union[str, None]
    created_at: datetime
    priority: 1

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`GuildRank` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`GuildRank` object.
        """
        return cls(
            name=resp["name"],
            default=resp["default"],
            tag=resp["tag"],
            created_at=datetime.utcfromtimestamp(resp["created"] / 1000),
            priority=resp["priority"],
        )


@dataclass(frozen=True)
class GuildMember(HypixelModel):
    uuid: str
    rank: str
    joined_at: datetime
    quest_participation: int

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`GuildMember` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`GuildMember` object.
        """
        return cls(
            uuid=resp["uuid"],
            rank=resp["rank"],
            joined_at=datetime.utcfromtimestamp(resp["joined"] / 1000),
            quest_participation=resp.get("questParticipation", 0),
        )


@dataclass(frozen=True)
class GuildTag(HypixelModel):
    """Represents a guild tag"""

    text: str
    colour: str
    color: str

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`GuildTag` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`GuildTag` object.
        """
        return cls(text=resp["tag"], colour=resp["tagColor"], color=resp["tagColor"])


@dataclass(frozen=True)
class Guild(HypixelModel):
    """Describes a Hypixel guild"""

    raw_data: APIResponse
    id: str
    name: str
    coins: int
    total_coins: int
    created_at: datetime
    joinable: bool
    tag: Dict[str, str]
    exp: int
    level: int
    preferred_games: List[str]
    ranks: Tuple[GuildRank]
    members: Tuple[GuildMember]
    banner: dict  # The API is kinda messy on this one
    achievements: Dict[str, int]
    exp_by_game: Dict[str, int]

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Guild` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Guild` object.
        """
        return cls(
            raw_data=resp,
            id=resp["_id"],
            name=resp["name"],
            coins=resp["coins"],
            total_coins=resp["coinsEver"],
            created_at=datetime.utcfromtimestamp(resp["created"] / 1000),
            tag=GuildTag.from_api_response(resp),
            exp=resp["exp"],
            level=get_guild_level(resp["exp"]),
            joinable=resp.get("joinable", False),
            preferred_games=resp.get("preferredGames"),
            ranks=tuple(GuildRank.from_api_response(r) for r in resp["ranks"]),
            members=tuple(GuildMember.from_api_response(m) for m in resp["members"]),
            banner=resp.get("banner"),
            achievements=resp["achievements"],
            exp_by_game=resp["guildExpByGameType"],
        )
