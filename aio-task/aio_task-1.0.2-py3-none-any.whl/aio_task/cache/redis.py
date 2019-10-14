""" Cache implementation based on aioredis for a redis storage. """
import asyncio
import logging

import aioredis

from aio_task.task import Task
from aio_task.cache import CacheABC


async def aquire_redis_connection(address, **kwargs):
    """ Get a redis client. """
    logging.debug(f"Connect to redis: {address}")
    try:
        return await aioredis.create_redis_pool(address, **kwargs)
    except Exception as exc:
        if "Could not connect" not in str(exc):
            raise exc
    logging.warning("Fail to connect to redis. Try again in a second...")
    await asyncio.sleep(1)
    return await aquire_redis_connection(address, **kwargs)


class Cache(CacheABC):
    """ Cache implementation. """

    def __init__(self, ttl, cache_conf):
        """ Use :func:`~Cache.create` to get an instance. """
        self.ttl = ttl
        self._cache_conf = cache_conf
        self.redis = None

    @classmethod
    async def create(cls, cache_conf):
        """ Create a new cache instance.

        :param dict cache_conf: see below
        :rtype: Cache

        ::

            cache_conf = {
                **kwargs,  # params forwarded to aioredis.create_redis_pool
                "ttl": int,  # optinal - to overwite default TTL
            }
        """
        logging.info("create redis cache.")
        try:
            ttl = cache_conf.pop("ttl")
        except KeyError:
            ttl = cls.TTL
        cache = cls(ttl, cache_conf)
        await cache.connect()
        return cache

    async def connect(self):
        """ Acquire a connection to redis pool. """
        logging.info("connect to redis.")
        self.redis = await aquire_redis_connection(**self._cache_conf)

    async def close(self):
        """ Shutdown the cache. """
        logging.info("close redis cache.")
        if self.redis is not None:
            self.redis.close()
            await self.redis.wait_closed()

    async def save_task(self, task, ttl=None):
        """ Store a task.

        :param int ttl: Time to keep task in cache, default TTL
        :param aio_task.task.Task task:
        """
        logging.debug("save task")
        await self.redis.set(task.task_id, task.dump(), expire=ttl or self.ttl)

    async def get_task(self, task_id):
        """ Get a task from its id.

        :param str task_id:
        :rtype: aio_task.task.Task
        :raises: ValueError if task not found
        """
        logging.debug("get task")
        data = await self.redis.get(task_id)
        if data is None:
            raise ValueError(task_id)

        return Task.load(data.decode())
