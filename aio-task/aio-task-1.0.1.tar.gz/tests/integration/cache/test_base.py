""" Default tests for a Cache. """
import os
import asyncio
import asynctest
from aio_task.task import Task
from aio_task.cache.dummy import Cache
from aio_task.cache.redis import Cache as Redis
from aio_task.cache.sentinel import Cache as Sentinel


class TestCache(asynctest.TestCase):
    """ Common tests for Cache. """

    async def setUp(self):
        self.cache = await Cache.create(None)

    async def tearDown(self):
        await self.cache.close()

    async def test_save_and_retreiv_task(self):
        """ Save and retreiv a task. """
        task = Task.new("name", {})
        await self.cache.save_task(task)
        data = await self.cache.get_task(task.task_id)
        self.assertEqual(hash(task), hash(data))

    async def test_get_unknow_task(self):
        """ Try to fetch a task that not exist in cache. """
        with self.assertRaises(ValueError):
            await self.cache.get_task("123-456")

    async def test_ttl_exipred(self):
        """ Get a task after ttl expied. """
        # Given
        task = Task.new("name", {})
        await self.cache.save_task(task, ttl=1)
        await self.cache.get_task(task.task_id)
        # When
        await asyncio.sleep(1)
        # Then
        with self.assertRaises(ValueError):
            await self.cache.get_task(task.task_id)


class TestRedis(TestCache):
    """ Common tests for Cache. """

    HOST = os.getenv("IP_HOST", "redis")
    HOST += ":6380"

    async def setUp(self):
        self.cache = await Redis.create({"address": f"redis://{self.HOST}"})

    async def tearDown(self):
        await self.cache.close()
        await self.flush_redis()

    async def flush_redis(self):
        """ Remove all data in redis. """
        import aioredis
        redis = await aioredis.create_redis_pool(f"redis://{self.HOST}")
        await redis.flushall()
        redis.close()
        await redis.wait_closed()


class TestSentinel(TestCache):
    """ Common tests for Cache. """

    HOST = os.getenv("IP_HOST", "sentinel")

    async def setUp(self):
        self.cache = await Sentinel.create({"sentinels": [
            (self.HOST, 26379)
        ]})

    async def tearDown(self):
        await self.cache.redis.flushall()
        await self.cache.close()
