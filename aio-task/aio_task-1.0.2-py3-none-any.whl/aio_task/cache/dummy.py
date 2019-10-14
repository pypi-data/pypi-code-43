""" Implemation of Cache interface with storing data in RAM - not persistant. """
import time
from aio_task.cache import CacheABC


class Cache(CacheABC):
    """ Not persitant Cache. """

    def __init__(self):
        self._cache = {}

    @classmethod
    async def create(cls, cache_conf):
        """ Create a new cache instance.

        :param dict cache_conf: not used
        :rtype: Cache
        """
        return cls()

    async def close(self):
        """ Shutdown the cache. """
        pass

    async def save_task(self, task, ttl=None):
        """ Store a task.

        :param int ttl: Time to keep task in cache, default TTL
        :param aio_task.task.Task task:
        """
        expired_at = time.time()
        expired_at += ttl or self.TTL
        self._cache[task.task_id] = (task, expired_at)

    async def get_task(self, task_id):
        """ Get a task from its id.

        :param str task_id:
        :rtype: aio_task.task.Task
        :raises: ValueError if task not found
        """
        try:
            task, expired_at = self._cache[task_id]
        except KeyError:
            raise ValueError(f"task not found {task_id}")
        if expired_at < time.time():
            self._cache.pop(task_id)
            raise ValueError(f"task not found {task_id}")
        return task
