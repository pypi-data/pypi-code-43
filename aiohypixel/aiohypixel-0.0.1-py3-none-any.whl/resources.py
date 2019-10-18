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
Resources dataclasses
"""

__all__ = (
    "Achievements",
    "Quests",
    "Challenges",
    "GuildAchievements",
    "GuildPermissions",
    "SkyblockCollections",
    "SkyblockSkills",
)

from dataclasses import dataclass

from .shared import HypixelModel, APIResponse


@dataclass(frozen=True)
class Achievements(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Achievements` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Achievements` object.
        """


@dataclass(frozen=True)
class Quests(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Quests` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Quests` object.
        """


@dataclass(frozen=True)
class Challenges(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`Challenges` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`Challenges` object.
        """


@dataclass(frozen=True)
class GuildAchievements(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`GuildAchievements` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`GuildAchievements` object.
        """


@dataclass(frozen=True)
class GuildPermissions(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`GuildPermissions` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`GuildPermissions` object.
        """


@dataclass(frozen=True)
class SkyblockCollections(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`SkyblockCollections` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`SkyblockCollections` object.
        """


@dataclass(frozen=True)
class SkyblockSkills(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`SkyblockSkills` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`SkyblockSkills` object.
        """
