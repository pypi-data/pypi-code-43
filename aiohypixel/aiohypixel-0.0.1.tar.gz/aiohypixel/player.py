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
Custom classes that are related to player lookups on the Hypixel API
"""

# TODO: Actually sort out this clusterfuck of stuff

from dataclasses import dataclass
from datetime import datetime
from math import sqrt, floor
from typing import Union, List, Dict, Tuple

from .shared import APIResponse, ImmutableProxy
from .stats import *

#: Locations where the player rank might be stored
POSSIBLE_RANK_LOC = ("packageRank", "newPackageRank", "monthlyPackageRank", "rank")

#: Level calculation stuff
EXP_FIELD = 0
LVL_FIELD = 0

BASE = 10000
GROWTH = 2500

HALF_GROWTH = 0.5 * GROWTH

REVERSE_PQ_PREFIX = -(BASE - 0.5 * GROWTH) / GROWTH
REVERSE_CONST = REVERSE_PQ_PREFIX * REVERSE_PQ_PREFIX
GROWTH_DIVIDES_2 = 2 / GROWTH

BEDWARS_EXP_PER_PRESTIGE = 489000
BEDWARS_LEVELS_PER_PRESTIGE = 100


def get_level(exp):
    return floor(1 + REVERSE_PQ_PREFIX + sqrt(REVERSE_CONST + GROWTH_DIVIDES_2 * exp))


def get_exact_level(exp):
    return get_level(exp) + get_percentage_to_next_lvl(exp)


def get_exp_from_lvl_to_next(level):
    return GROWTH * (level - 1) + BASE


def get_total_exp_to_lvl(level):
    lv = floor(level)
    x0 = get_total_exp_to_full_lvl(lv)
    if level == lv:
        return x0
    else:
        return (get_total_exp_to_full_lvl(lv + 1) - x0) * (level % 1) + x0


def get_total_exp_to_full_lvl(level):
    return (HALF_GROWTH * (level - 2) + BASE) * (level - 1)


def get_percentage_to_next_lvl(exp):
    lv = get_level(exp)
    x0 = get_total_exp_to_lvl(lv)
    return (exp - x0) / (get_total_exp_to_lvl(lv + 1) - x0)


def get_exp(EXP_FIELD, LVL_FIELD):
    exp = int(EXP_FIELD)
    exp += get_total_exp_to_full_lvl(LVL_FIELD + 1)
    return exp


@dataclass(frozen=True)
class Player:
    """
    This will describe a player
    """

    raw_data: APIResponse
    hypixel_id: int
    uuid: int
    username: str
    aliases: List[str]  # in chronological order
    one_time_achievements: List[str]  # also in chronological order
    achievments: ImmutableProxy
    mc_version: str
    rank: str
    was_staff: bool
    rank_colour: str
    rank_color: str  # for 'muricans
    outfit: ImmutableProxy
    voting: ImmutableProxy
    parkours: ImmutableProxy

    #: If it is `None`, it means the full player info wasn't requested
    stats: Tuple[ImmutableProxy] = None

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Player` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Player` object.
        """


class PlayerStats:
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`PlayerStats` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`PlayerStats` object.
        """


class PlayerInfo:
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`PlayerStats` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`PlayerStats` object.
        """


def process_raw_player(json_data: APIResponse, partial: bool = False) -> Player:
    """
    This handles the raw json returned by the API and creates a Player object
    Pass the `partial` param as True to get a PartialPlayer object instead.
    """
    # Basic player info
    processed_data = {
        "hypixel_id": json_data["_id"],
        "uuid": json_data["uuid"],
        "username": json_data["displayname"],
        "aliases": [*json_data["knownAliases"].values()],
        "raw_data": json_data,
    }

    # Last used MC version
    processed_data.update({"mc_version": json_data.get("mcVersionRp")})

    # Rank
    for l in POSSIBLE_RANK_LOC:
        if l in json_data:
            if l == "rank" and json_data[l] == "NORMAL":
                was_staff = True
            else:
                was_staff = False
                if json_data[l].upper() == "NONE":
                    continue
                rank = (
                    json_data[l]
                    .title()
                    .replace("_", " ")
                    .replace("Mvp", "MVP")
                    .replace("Vip", "VIP")
                    .replace("Superstar", "MVP++")
                    .replace("Youtuber", "YouTube")
                    .replace(" Plus", "+")
                )
    processed_data.update({"rank": rank, "was_staff": was_staff})

    # Calculating player's Network EXP
    processed_data.update({"level": get_level(json_data["networkExp"])})

    # Voting stats
    # Just processing the time snowflakes
    # Doing a cheeky workaround :D
    json_data["voting"] = ImmutableProxy(
        {
            k: datetime.utcfromtimestamp(v / 1000) if k.startswith("last") else v
            for k, v in json_data.get("voting", {})
        }
    )
    # That can be translated to:
    # for k, v in json_data.get("voting", {}):
    #     if k.startswith("last"):
    #         json_data.get("voting", {})[k] = datetime.utcfromtimestamp(v / 1000)

    # Parkours
    # More cheeky trickery
    p_actions = {
        "timeStart": lambda t: datetime.utcfromtimestamp(t / 1000),
        "timeTook": lambda t: t / 1000,
    }
    json_data["parkours"] = ImmutableProxy(
        [ImmutableProxy({k: p_actions.get(k, lambda x: x)(v) for k, v in l}) for a in l]
        for l in json_data.get("parkourCompletions", {})
    )

    # That can be translated to:
    # p_tmp = {}
    # for lobby in json_data.get("parkourCompletions", {}):
    #     new_attemps = []
    #     for attempt in lobby:
    #         new_attempt = {}
    #         for key, value in attempt:
    #             new_attempt[key] = p_actions.get(key, lambda x: x)(value)
    #         new_attempts.append(new_attempt)
    #     p_tmp[lobby] = new_attemps

    # json_data["parkours"] = ImmutableProxy(p_tmp)

    # Current outfit
    processed_data.update(
        {
            "outfit": {
                k.lower(): v.title().replace("_", " ") for k, v in json_data.get("outfit", {})
            }
            or None
        }
    )

    if partial:
        return Player(**processed_data)

    processed_data.update({"stats": process_raw_player_stats(json_data.get("stats", {}))})

    return Player(**processed_data)


### Stats ###

# This is extracted from Plancke's php stuff

BW_XP_PER_PRESTIGE = 489000
BW_LVLS_PER_PRESTIGE = 100


def get_bw_lvl(exp: int) -> int:

    prestige = exp // BW_XP_PER_PRESTIGE
    exp = exp % BW_XP_PER_PRESTIGE

    if prestige > 5:
        over = prestige % 5
        exp += over * BW_XP_PER_PRESTIGE
        prestige -= over

    if exp < 500:
        return 0 + (prestige * BW_LVLS_PER_PRESTIGE)
    if exp < 1500:
        return 1 + (prestige * BW_LVLS_PER_PRESTIGE)
    if exp < 3500:
        return 2 + (prestige * BW_LVLS_PER_PRESTIGE)
    if exp < 5500:
        return 3 + (prestige * BW_LVLS_PER_PRESTIGE)
    if exp < 9000:
        return 4 + (prestige * BW_LVLS_PER_PRESTIGE)

    exp -= 9000

    return (exp / 5000 + 4) + (prestige * BW_LVLS_PER_PRESTIGE)


def process_raw_player_stats(
    json_data: APIResponse, game: Union[str, None] = None
) -> Tuple[ImmutableProxy]:
    """This will process the JSON data into a tuple of game stats"""
    # Processing bedwars exp
    json_data.get("Bedwars", {})["level"] = get_bw_lvl(json_data.get("Bedwars", {})["Experience"])

    ...  # Process more stuff in the future ig

    return tuple(ImmutableProxy(d) for _, d in json_data.items())
