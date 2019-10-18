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
This defines a connection to the Hypixel API. 
All requests will pass through here and this will handle everything for you
"""

# TODO: Clean up logging messages.

__all__ = ("HypixelSession",)

import aiohttp
import asyncio
import logging
import typing
from random import choice
import re
from uuid import UUID

# NOTE: I should probably ditch the wildcard import
from .shared import *
from .player import *
from .guild import *
from .boosters import *
from .keys import *
from .friends import *
from .watchdogstats import *
from .resources import *
from .skyblock import *
from .leaderboards import *

#: This is the base URL for all the requests regarding the Hypixel API.
BASE_API_URL = "https://api.hypixel.net/"

#: This is the message sent when you try to do a request with an invalid key.
INVALID_KEY_MESSAGE = "Invalid API key!"

#: Mojang name lookup endpoint
MOJANG_PROFILE_API_URL = "https://api.mojang.com/users/profiles/minecraft/"

#: This is th length of a UUID. 32 hex digits + 4 dashes.
UUID_LENGTH = (32, 36)

#: This is the boundaries of char lenghts for Minecraft usernames.
MC_NAME_LENGTH = (3, 16)

#: MongoDB _id string pattern. The API uses Mongo's IDs for guilds.
MONGO_ID_RE = re.compile(r"^[a-f\d]{24}$", re.I)


class HypixelSession:
    """
    Represents a connection to the Hypixel API.
    You can perform a check on your API keys with the :meth:`check_keys` method.
    """

    #: This is the base URL for all the requests regarding the Hypixel API. Also see :const:`BASIC_API_URL`.
    DEFAULT_BASE_API_URL: str = BASE_API_URL

    __slots__ = ("logger", "_api_keys", "api_url", "max_key_wait_time", "loop", "http_client")

    def __init__(
        self,
        api_keys: typing.Iterable[str],
        *,
        api_url: str = None,
        max_key_wait_time: typing.Union[int, float] = 10,
        loop: asyncio.AbstractEventLoop = None,
    ) -> None:
        """
        Args:
            api_keys:
                The collection of API keys to use for making requests.
            api_url:
                The base API URL to use. Defaults to :attr:`DEFAULT_BASE_API_URL`.
            max_key_wait_time:
                The maximum time in seconds the requester will wait for an available key.
                After that, :exc:asyncio.TimeoutError is raised.
                Defaults to 10.
            loop:
                The event loop to use for any asynchronous task.
        """
        #: Client logger.
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Starting a new session...")

        #: Pool of API keys to use when doing requests.
        self._api_keys = asyncio.Queue()
        # Filling the queue
        for k in api_keys:
            self._api_keys.put_nowait(k)

        #: Base API URL to use
        self.api_url = api_url or self.DEFAULT_BASE_API_URL
        #: Maximum time (in seconds) allowed for the requester to wait for an available key before raising an error.
        self.max_key_wait_time = max_key_wait_time
        #: Event loop to use for any asynchronous process.
        self.loop = loop or asyncio.get_event_loop()
        #: Client to use for making requests to the API.
        self.http_client = aiohttp.ClientSession(loop=self.loop)

        self.logger.debug("Session fully initialized!")

    @property
    def api_keys(self):
        """Set of all available keys in the pool."""
        # Ik this isn't that great...
        return set(self._api_keys._queue)

    async def _request(self, endpoint: str, params: dict = {}):
        """
        Fetches the JSON response from the passed endpoint with the given params.

        Args:
            endpoint:
                The endpoint to make the request to.
            params:
                The query-string parameters to pass.

        Returns:
            The JSON response received from the API.

        Raises:
            asyncio.TimeoutError:
                In case an available key cannot be found in less time than :attr:`max_key_wait_time` seconds.
            InvalidAPIKey:
                If the API key used was rejected.
                When this happens, the invalid API key will be removed from the internal key pool.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        self.logger.debug(
            "Starting to fetch JSON from the **%s** endpoint with these params: %s",
            endpoint,
            params,
        )

        self.logger.debug("Chosing key...")
        key = await asyncio.wait_for(self._api_keys.get(), timeout=self.max_key_wait_time)

        if "key" not in params:
            params["key"] = key

        self.logger.debug("Chose: `%s`\nNow doing the actual fetching...", params["key"])

        trash_key = False
        try:
            async with self.http_client.get(f"{BASE_API_URL}{endpoint}", params=params) as resp:
                resp.raise_for_status()
                result = await resp.json()

            if not result["success"]:
                # NOTE: Maybe keep trying until a key is valid?
                if result["cause"] == INVALID_KEY_MESSAGE:
                    trash_key = True
                    self.logger.error("Request failed due to invalid API key! Removing it...")
                    raise InvalidAPIKey

                self.logger.error("Request failed! Cause: %s", result["cause"])
                raise UnsuccessfulRequest(result["cause"])

            self.logger.debug("Request was successful! Returning result...")
            return result
        except KeyError:
            raise HypixelAPIError("Something went wrong with the Hypixel API! Try again later.")
        finally:
            if not trash_key:
                self._api_keys.put_nowait(key)

    async def check_keys(
        self, keys: typing.Union[str, typing.Iterable[str]]
    ) -> typing.Iterable[str]:
        """
        Validates the given keys by using the '/key' endpoint, wrapped by :meth:`get_key`.

        Args:
            keys:
                Collection of keys to check.

        Returns:
            Collection of invalid keys.

        Raises:
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        self.logger.debug("Checking API keys: %s", keys)

        rejected_keys = set()

        for k in keys:
            try:
                # Not even caring about the return value
                await self.get_key(k)
            except InvalidAPIKey:
                rejected_keys.add(k)

        self.logger.debug(
            "Finished checking API keys. Encoutered %s error%s!",
            len(rejected_keys) or "no",
            "s" if rejected_keys else "",
        )
        return rejected_keys

    ## Deprecated this since it doesn't make sense with the queue aproach I'm going with
    ## I might add separate methods for adding or removing keys later.
    # async def edit_keys(
    #     self, new_keys: typing.Iterable[str], validate_keys: bool = True
    # ) -> typing.Union[typing.Set[str], None]:

    #     """
    #     Allows you to edit your registered keys for this session.
    #     You can optionally perform a check on the keys, and if so,
    #     any invaid key will not be added and instead be returned a collection of all invalid keys.

    #     Args:
    #         new_keys:
    #             The collection of keys to check.
    #         validate_keys:
    #             Wheather to perform validation checks on the keys or not.

    #     Returns:
    #         Collection of invalid keys.

    #     Raises:
    #         HypixelAPIError:
    #             In case the API didn't give an OK response.
    #         UnsuccessfulRequest:
    #             If the API rejected the request for some unkonwn reason.
    #     """

    #     self.logger.debug("Attempting to change the API key pool...")

    #     invalid_keys = None

    #     if validate_keys:
    #         invalid_keys = await self.check_keys(new_keys)

    #     self.api_keys = self.api_keys - invalid_keys

    #     self.logger.info("Changed the API key pool to: %s", self.api_keys)

    #     return invalid_keys

    async def name_to_uuid(self, query: str) -> str:
        """
        Gets the UUID for the player with the given name.
        Uses the Mojang API.

        Args:
            query:
                The username you want to lookup the UUID of.

        Returns:
            The player's UUID.

        Raises:
            aiohttp.ClientResponseError:
                In case something goes wrong with the request.
        """
        self.logger.debug("Fetching UUID from name: %s", query)

        async with self.http_client.get(f"{MOJANG_PROFILE_API_URL}{query}") as resp:
            resp.raise_for_status()
            return (await resp.json())["id"]

    async def uuid_to_name(self, query: str) -> str:
        """
        Gets the name for the player with the given UUID.
        Uses the Mojang API for that.

        Args:
            query:
                The player UUID to get the name of.

        Returns:
            The player's name.

        Raises:
            aiohttp.ClientResponseError:
                In case something goes wrong with the request.
        """
        self.logger.debug("Fetching name from UUID: %s", query)

        async with self.http_client.get(f"{MOJANG_PROFILE_API_URL}{query}") as resp:
            resp.raise_for_status()
            return (await resp.json())["name"]

    async def get_player_by_name(self, name: str) -> typing.Union[Player, None]:
        """"""

    async def get_player_by_uuid(self, uuid: typing.Union[UUID, str]) -> typing.Union[Player, None]:
        """"""

    async def get_player(self, query: typing.Union[str, UUID]) -> typing.Union[Player, None]:
        """
        Gets a full player object (general info + game stats) with the given query.

        Args:
            query:
                Either the UUID or username of the player you want to get.

        Returns:
            The requested player data or `None` if the player wasn't found.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        if is_uuid(query):
            return await self.get_player_by_uuid(query)

        return await self.get_player_by_name(query)

    async def get_player_stats(self, query: str) -> typing.Union[PlayerStats, None]:
        """
        Gets a player's stats with the given query.

        Args:
            query:
                Either the UUID or username of the player you want to get the stats for.

        Returns:
            The requested player stats or `None` if the player wasn't found.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        if is_uuid(query):
            query_type = "uuid"
        else:
            query_type = "name"

        result = await self._request("player", params={query_type: query})

        if result["player"] is None:
            return

        return PlayerStats.from_api_response(result["player"]["stats"])

    async def get_player_info(self, query: str) -> typing.Union[PlayerInfo, None]:
        """
        Gets a player object with just the network info that does not relate to any stats.

        Args:
            query:
                Either the UUID or username of the player you want to get info for.

        Returns:
            The requested player info or `None` if the player wasn't found.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        if is_uuid(query):
            query_type = "uuid"
        else:
            query_type = "name"

        result = await self._request("player", params={query_type: query})

        if result["player"] is None:
            return

        return PlayerInfo.from_api_response(result["player"])

    # NOTE: maybe split this into two separate methods?
    async def get_guild_id(self, query: str) -> typing.Union[str, None]:
        """"""

    async def get_guild_by_id(self, guild_id: str) -> typing.Union[Guild, None]:
        """"""

    async def get_guild_by_name(self, name: str) -> typing.Union[Guild, None]:
        """"""

    async def get_guild(self, query: str) -> typing.Union[Guild, None]:
        """
        Gets a guild object from the given query.

        Args:
            query:
                Either the ID or name of the guild you want to get.

        Returns:
            The requested guild or `None` if not found.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """

        if is_uuid(query):
            return await self.get_guild_by_id(query)

        return await self.get_guild_by_name(query)

    # NOTE: Maybe rename to 'get_player_guild'?
    async def get_guild_by_player_uuid(
        self, uuid: typing.Union[UUID, str]
    ) -> typing.Union[Guild, None]:
        """"""

    async def get_guild_by_player_name(self, name: str) -> typing.Union[Guild, None]:
        """"""

    async def get_guild_by_player(
        self, query: typing.Union[str, UUID]
    ) -> typing.Union[Guild, None]:
        """
        Gets a guild object to which the player with the given name/UUID belongs to.

        Args:
            query:
                Either the ID or name of the player you want to get guild for.

        Returns:
            The requested guild or `None` if not found.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        if is_uuid(query):
            return await self.get_guild_by_player_uuid(query)

        return await self.get_guild_by_player_name(query)

    async def get_key(self, key: typing.Union[UUID, str]) -> Key:
        """
        Gets a Key object from the passed query.

        Args:
            key:
                The key to get.

        Returns:
            The requested key.

        Raises:
            InvalidAPIKey:
                If the requested key does not exist.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
                """
        if not is_uuid(key):
            raise InvalidAPIKey(f"{key} isn't a valid UUID and so it isn't a valid key!")

        result = await self._request("key", params={"key": key})

        return Key.from_api_response(result["record"])

    async def get_friends_by_name(self, name: str) -> typing.List[Friend]:
        """"""

    async def get_friends_by_uuid(self, uuid: typing.Union[UUID, str]) -> typing.List[Friend]:
        """"""

    # NOTE: Maybe implement an async iterator for this?
    async def get_friends(self, query: typing.Union[str, UUID]) -> typing.List[Friend]:
        """
        Gets a tuple of Friend objects that the player with the given name/UUID has.

        Args:
            query:
                Either the UUID or the username of the player you want to get the friends for.

        Returns:
            A list of friends the given player has.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
                """
        if is_uuid(uuid):
            return await self.get_friends_by_uuid(query)

        return await self.get_friends_by_name(query)

    async def get_boosters(self) -> typing.Tuple[typing.List[Booster], dict]:
        """
        Gets a tuple of Booster objects denoting the currently active boosters on the Hypixel Network.

        Returns:
            A list containing the currently active boosters as well as the boosters state.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        result = await self._request("boosters")

        boosters = [Booster.from_api_response(b) for b in result.get("boosters", ())]

        # NOTE: Maybe tidy up this with an enum or smth?
        return boosters, result.get("boosterState")

    async def get_watchdog_stats(self) -> WatchdogStats:
        """
        Gets the current WatchDog stats.

        Returns:
            The current Watchdog stats.

        Raises:
            InvalidAPIKey:
                If the used API key isn't valid.
            HypixelAPIError:
                In case the API didn't give an OK response.
            UnsuccessfulRequest:
                If the API rejected the request for some unkonwn reason.
        """
        result = await self._request("watchdogstats")

        return WatchdogStats.from_api_response(result)

    async def get_leaderboards(self) -> Leaderboards:
        """"""

    async def get_player_count(self) -> int:
        """"""

    async def get_achievements_resource(self) -> Achievements:
        """"""

    async def get_quests_resource(self) -> Quests:
        """"""

    async def get_challenges_resource(self) -> Challenges:
        """"""

    async def get_guild_achievements_resource(self) -> GuildAchievements:
        """"""

    async def get_guild_permissions_resource(self) -> GuildPermissions:
        """"""

    async def get_skyblock_collections_resource(self) -> SkyblockCollections:
        """"""

    async def get_skyblock_skills_resource(self) -> SkyblockSkills:
        """"""

    async def get_skyblock_player_auctions_by_uuid(
        self, uuid: typing.Union[UUID, str]
    ) -> typing.List[SkyblockAuction]:
        """"""

    async def get_skyblock_profile_auctions(
        self, uuid: typing.Union[UUID, str]
    ) -> typing.List[SkyblockAuction]:
        """"""

    async def get_skyblock_auction(self, uuid: typing.Union[UUID, str]) -> SkyblockAuction:
        """"""

    async def get_all_skyblock_auctions(self) -> SkyblockAuctionsIterator:
        """"""

    async def get_all_skyblock_auctions_page(self, index: int) -> typing.List[SkyblockAuction]:
        """"""

    async def get_skyblock_news(self) -> typing.List[SkyblockNews]:
        """"""

    async def get_skyblock_profile(self) -> SkyblockProfile:
        """"""
