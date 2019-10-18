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
Skyblock related stuff
"""

__all__ = ("SkyblockAuction", "SkyblockNews", "SkyblockProfile", "SkyblockAuctionsIterator")

import collections
from dataclasses import dataclass

from .shared import HypixelModel, APIResponse


@dataclass(frozen=True)
class SkyblockAuction(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`SkyblockAuction` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`SkyblockAuction` object.
        """


@dataclass(frozen=True)
class SkyblockNews(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`SkyblockNews` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`SkyblockNews` object.
        """


@dataclass(frozen=True)
class SkyblockProfile(HypixelModel):
    """"""

    @classmethod
    def from_api_response(cls, resp: APIResponse):
        """
        Processes the raw API response into a :class:`SkyblockProfile` object.

        Args:
            resp:
                The API response to process.

        Returns:
            The processed :class:`SkyblockProfile` object.
        """


class SkyblockAuctionsIterator(collections.abc.AsyncIterator):
    """"""
