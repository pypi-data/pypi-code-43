# -*- coding: utf-8 -*-

"""The WCraaS Discovery module is responsible for providing discovery services for the platform."""

import asyncio
import json
import logging
import aio_pika
import aiohttp

from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType
from aio_pika.patterns import RPC
from aio_pika.pool import Pool
from bs4 import BeautifulSoup
from typing import Dict, List
from yarl import URL

from wcraas_common import AMQPConfig, WcraasWorker
from wcraas_common.decorator import is_rpc


class DiscoveryWorker(WcraasWorker):
    """
    Discovery Worker for the WCraaS platform. Provides the `discover` RPC function.

    >>> from wcraas_discovery.config import Config
    >>> cn = DiscoveryWorker(*Config.fromenv())
    """

    def __init__(self, amqp: AMQPConfig, loglevel: int, *args, **kwargs):
        super().__init__(amqp, loglevel)
        self.logger = logging.getLogger("wcraas.discovery")
        self.logger.setLevel(loglevel)
        self._close = asyncio.Event()

    @is_rpc("discover")
    async def discover(self, url: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Faktory entrypoint for the discovery process.

        :param url: The url to scrape.
        :type url: string
        """
        self.logger.info(f"Received: {url}")

        async with self.http_session.get(url, ssl=False) as resp:
            if resp.status >= 400:
                self.logger.warn(f"Got error code {resp.status} for {url}")
            html_body = await resp.text()

        async with self._amqp_pool.acquire() as raw_channel:
            raw_exchange = await raw_channel.declare_exchange(
                "discovery_raw", ExchangeType.FANOUT
            )
            message = Message(
                json.dumps({"url": url, "html": html_body}).encode("utf-8"),
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            # routing_key has to be present but is irelevant
            await raw_exchange.publish(message, routing_key="")
        result = self.extract(html_body, url)
        self.logger.info(f"Done processing: {url}")
        return {"data": result}

    async def start(self) -> None:
        """
        Asynchronous runtime for the worker, responsible of managing and maintaining async context open.
        """
        async with aiohttp.ClientSession() as http_session:
            self.http_session = http_session
            await self.start_rpc()

    @staticmethod
    def extract(html_body: str, origin_url: str) -> Dict[str, List[str]]:
        """
        Given an html body and its origin URL, extract URLs and categorize them to inbound & outbound.

        :param html_body: HTML content of the craweld endpoint
        :type html_body: string
        :param origin_url: The URL (endpoint) from which the above body originates
        :type origin_url: string
        """
        inbound = set()
        outbound = set()
        origin = URL(origin_url).origin()
        soup = BeautifulSoup(html_body, "html.parser")
        for a_element in soup.find_all("a"):
            try:
                url = URL(a_element["href"])
            except KeyError:
                continue
            if url.is_absolute():
                url_origin = url.origin()
                if url_origin != origin:
                    outbound.add(str(url))
                    continue
            else:
                # tel, ftp etc
                if url.scheme not in ("http", "https", ""):
                    outbound.add(str(url))
                    continue
                url_origin = origin
            inbound.add(url_origin.join(URL(url.path)))
        return {
            "inbound": [str(el) for el in inbound],
            "outbound": [str(el) for el in outbound],
        }
