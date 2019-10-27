# -*- coding: utf-8 -*-

"""The WCraaS Common module aims to single-source reused code across WCraaS the platform."""

import asyncio
import logging
import aio_pika

from abc import ABC, abstractmethod

from aio_pika import connect_robust, ExchangeType
from aio_pika.patterns import RPC
from aio_pika.pool import Pool

from wcraas_common.config import AMQPConfig


__all__ = ("WcraasWorker",)


class WcraasWorker(ABC):
    """
    Base class for WCraaS Worker classes, aiming to single-source AMQP boilerplate.
    """

    __slots__ = (
        "amqp",
        "logger",
        "loglevel",
        "_amqp_pool",
        "_close",
    )

    def __init__(self, amqp: AMQPConfig, loglevel: int, *args, **kwargs):
        self.amqp = amqp
        self.logger = logging.getLogger("wcraas.common")
        self.logger.setLevel(loglevel)
        self.loglevel = loglevel
        self._amqp_pool = self.create_channel_pool()
        self._close = asyncio.Event()

    def _discover_callable(self):
        for attr in dir(self):
            if attr.startswith("__"):
                continue
            obj = getattr(self, attr)
            if not callable(obj):
                continue
            yield obj

    def _discover(self, attribute):
        return [
            obj
            for obj in self._discover_callable()
            if getattr(obj, attribute, False)
        ]

    def create_channel_pool(self, pool_size: int = 2, channel_size: int = 10) -> Pool:
        """
        Given the max connection pool size and the max channel size create a channel Pool.

        :param pool_size: Max size for the underlying connection Pool.
        :type pool_size: integer
        :param channel_size: Max size for the channel Pool.
        :type channel_size: integer
        """

        async def get_connection():
            return await connect_robust(
                host=self.amqp.host,
                port=self.amqp.port,
                login=self.amqp.user,
                password=self.amqp.password,
            )

        connection_pool = Pool(get_connection, max_size=pool_size)

        async def get_channel() -> aio_pika.Channel:
            async with connection_pool.acquire() as connection:
                return await connection.channel()

        return Pool(get_channel, max_size=channel_size)

    async def start_rpc(self) -> None:
        """
        Asynchronous runtime for the worker, responsible of managing and maintaining async context open.
        """
        async with self._amqp_pool.acquire() as rpc_channel:
            rpc = await RPC.create(rpc_channel)
            for func in self._discover("is_rpc"):
                await rpc.register(func.rpc_command, func, auto_delete=True)
            await self._close.wait()

    async def start_consume(self):
        async with self._amqp_pool.acquire() as sub_channel:
            await sub_channel.set_qos(prefetch_count=1)
            for func in self._discover("is_consume"):
                queue_name = func.consume_queue
                exchange = await sub_channel.declare_exchange(queue_name, ExchangeType.FANOUT)
                queue = await sub_channel.declare_queue(exclusive=True)
                await queue.bind(exchange)
                await queue.consume(self.store)
                self.logger.info(f"Registered {queue_name} ...")
            await self._close.wait()

    @abstractmethod
    async def start(self):
        """
        Asynchronous runtime for the worker, responsible of managing and maintaining async context open.
        """
        pass

    def run(self) -> None:
        """
        Helper function implementing the synchronous boilerplate for initilization and teardown.
        """
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            self.logger.info("[x] Received ^C ! Exiting ...")
        finally:
            self._close.set()
            loop.shutdown_asyncgens()

    def __repr__(self):
        return f"{self.__class__.__name__}(amqp={self.amqp}, loglevel={self.loglevel})"
