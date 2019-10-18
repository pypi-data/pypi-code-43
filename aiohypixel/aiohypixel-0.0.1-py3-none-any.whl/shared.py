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
Custom exceptions related to the Hypixel API and other misc stuff
"""

__all__ = (
    "GAME_TYPES_TABLE",
    "APIResponse",
    "AiohypixelException",
    "UnsuccessfulRequest",
    "PlayerNotFound",
    "GuildIDNotValid",
    "HypixelAPIError",
    "InvalidAPIKey",
    "ImmutableProxy",
    "is_uuid",
)

import abc
import inspect
import typing
import uuid

#: Mapping for decoding game types (https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/misc/GameType.md)
GAME_TYPES_TABLE = {
    2: {"type_name": "QUAKECRAFT", "db_name": "Quake", "pretty_name": "Quake"},
    3: {"type_name": "WALLS", "db_name": "Walls", "pretty_name": "Walls"},
    4: {"type_name": "PAINTBALL", "db_name": "Paintball", "pretty_name": "Paintball"},
    5: {
        "type_name": "SURVIVAL_GAMES",
        "db_name": "HungerGames",
        "pretty_name": "Blitz Survival Games",
    },
    6: {"type_name": "TNTGAMES", "db_name": "TNTGames", "pretty_name": "TNT Games"},
    7: {"type_name": "VAMPIREZ", "db_name": "VampireZ", "pretty_name": "VampireZ"},
    13: {"type_name": "WALLS3", "db_name": "Walls3", "pretty_name": "Mega Walls"},
    14: {"type_name": "ARCADE", "db_name": "Arcade", "pretty_name": "Arcade"},
    17: {"type_name": "ARENA", "db_name": "Arena", "pretty_name": "Arena"},
    20: {"type_name": "UHC", "db_name": "UHC", "pretty_name": "UHC Champions"},
    21: {"type_name": "MCGO", "db_name": "MCGO", "pretty_name": "Cops and Crims"},
    23: {"type_name": "BATTLEGROUND", "db_name": "Battleground", "pretty_name": "Warlords"},
    24: {"type_name": "SUPER_SMASH", "db_name": "SuperSmash", "pretty_name": "Smash Heroes"},
    25: {"type_name": "GINGERBREAD", "db_name": "GingerBread", "pretty_name": "Turbo Kart Racers"},
    26: {"type_name": "HOUSING", "db_name": "Housing", "pretty_name": "Housing"},
    51: {"type_name": "SKYWARS", "db_name": "SkyWars", "pretty_name": "SkyWars"},
    52: {"type_name": "TRUE_COMBAT", "db_name": "TrueCombat", "pretty_name": "Crazy Walls"},
    54: {"type_name": "SPEED_UHC", "db_name": "SpeedUHC", "pretty_name": "Speed UHC"},
    55: {"type_name": "SKYCLASH", "db_name": "SkyClash", "pretty_name": "SkyClash"},
    56: {"type_name": "LEGACY", "db_name": "Legacy", "pretty_name": "Classic Games"},
    57: {"type_name": "PROTOTYPE", "db_name": "Prototype", "pretty_name": "Prototype"},
    58: {"type_name": "BEDWARS", "db_name": "Bedwars", "pretty_name": "Bed Wars"},
    59: {
        "type_name": "MURDER_MYSTERY",
        "db_name": "MurderMystery",
        "pretty_name": "Murder Mystery",
    },
    60: {"type_name": "BUILD_BATTLE", "db_name": "BuildBattle", "pretty_name": "Build Battle"},
    61: {"type_name": "DUELS", "db_name": "Duels", "pretty_name": "Duels"},
}

#: Dummy type to represent an response from the Hypiel API.
APIResponse = typing.NewType("APIResponse", typing.Dict[str, typing.Any])


class AiohypixelException(Exception):
    """
    Base exception class from which all other exceptions by this library are subclassed.
    """


class UnsuccessfulRequest(AiohypixelException):
    """
    Raised when the "success" key from a request is False
    """


class PlayerNotFound(UnsuccessfulRequest):
    """
    Raised if a player/UUID is not found. This exception can usually be ignored.
    You can catch this exception with ``except aiohypixel.PlayerNotFoundException:`` 
    """


class GuildIDNotValid(UnsuccessfulRequest):
    """
    Raised if a Guild is not found using a Guild ID. This exception can usually be ignored.
    You can catch this exception with ``except aiohypixel.GuildIDNotValid:`` 
    """


class HypixelAPIError(UnsuccessfulRequest):
    """
    Raised if something's gone very wrong with the API. 
    """


class InvalidAPIKey(UnsuccessfulRequest):
    """
    Raised if the given API Key is invalid
    """


def find(func, iterable):
    for i in iterable:
        if func(i):
            return i
    return None


def get(iterable, **attrs):
    def predicate(elem):
        for attr, val in attrs.items():
            nested = attr.split("__")
            obj = elem
            for attribute in nested:
                obj = getattr(obj, attribute)

            if obj != val:
                return False
        return True

    return find(predicate, iterable)


def is_uuid(item: typing.Union[str, uuid.UUID]) -> bool:
    """
    Checks if the given string is a valid UUID.

    Args:
        item:
            The hexadecimal string to check. 
    """
    if isinstance(item, str):
        try:
            uuid.UUID(item)
            return True
        except ValueError:  # in case of a malformed hex UUID string
            return False

    return isinstance(item, uuid.UUID)


class ImmutableProxy:
    """"""


class HypixelModel(abc.ABC):
    """
    Base for all models.
    """

    @abc.abstractclassmethod
    def from_api_response(cls, resp: APIResponse):
        ...
