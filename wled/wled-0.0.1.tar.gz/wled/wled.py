# -*- coding: utf-8 -*-
"""Asynchronous Python client for WLED."""
import asyncio
import json
import socket
from typing import Any, List, Mapping, Optional

import aiohttp
import async_timeout
from yarl import URL

from .__version__ import __version__
from .exceptions import WLEDConnectionError, WLEDError


class WLED:
    """Main class for handling connections with WLED."""

    def __init__(
        self,
        host: str,
        base_path: str = "/json",
        loop: asyncio.events.AbstractEventLoop = None,
        password: str = None,
        port: int = 80,
        request_timeout: int = 3,
        session: aiohttp.client.ClientSession = None,
        tls: bool = False,
        username: str = None,
        verify_ssl: bool = True,
        user_agent: str = None,
    ) -> None:
        """Initialize connection with WLED."""
        self._loop = loop
        self._session = session
        self._close_session = False

        self.base_path = base_path
        self.host = host
        self.password = password
        self.port = port
        self.socketaddr = None
        self.request_timeout = request_timeout
        self.tls = tls
        self.username = username
        self.verify_ssl = verify_ssl
        self.user_agent = user_agent

        if user_agent is None:
            self.user_agent = f"PythonWLED/{__version__}"

        if self.base_path[-1] != "/":
            self.base_path += "/"

    async def _request(
        self,
        uri: str,
        method: str = "GET",
        data: Optional[Any] = None,
        json_data: Optional[dict] = None,
        params: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Handle a request to a WLED device."""
        scheme = "https" if self.tls else "http"
        url = URL.build(
            scheme=scheme, host=self.host, port=self.port, path=self.base_path
        ).join(URL(uri))

        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
        }

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self._loop)
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    auth=auth,
                    data=data,
                    json=json_data,
                    params=params,
                    headers=headers,
                    ssl=self.verify_ssl,
                )
        except asyncio.TimeoutError as exception:
            raise WLEDConnectionError(
                "Timeout occurred while connecting to WLED device."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise WLEDConnectionError(
                "Error occurred while communicating with WLED device."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            if content_type == "application/json":
                raise WLEDError(response.status, json.loads(contents.decode("utf8")))
            raise WLEDError(response.status, {"message": contents.decode("utf8")})

        if "application/json" in content_type:
            return await response.json()

        return await response.text()

    async def state(self, state: Optional[bool] = None) -> bool:
        """Return if device state is on or not."""
        if state is not None:
            await self._request("state", method="POST", json_data={"on": state})
            return state

        response = await self._request("state")
        return response["on"]

    async def version(self) -> str:
        """Return the current version of WLED on the device."""
        response = await self._request("info")
        return response["ver"]

    async def effects(self) -> List[str]:
        """Return the list of effects this WLED device supports."""
        effects = await self._request("eff")
        effects.sort()
        return effects

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "WLED":
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
