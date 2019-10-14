""" Define Cache interface. """
from abc import ABC


class Cache(ABC):
    """ Cache interface. """

    TTL = 86400  # default time to keep a task in a cache

    @classmethod
    async def create(cls, cache_conf):
        """ Create a new cache instance.

        :param dict cache_conf:
        :rtype: Cache
        """
        pass

    async def close(self):
        """ Shutdown the cache. """
        pass

    async def save_task(self, task, ttl=None):
        """ Store a task.

        :param int ttl: Time to keep task in cache, default TTL
        :param aio_task.task.Task task:
        """
        pass

    async def get_task(self, task_id):
        """ Get a task from its id.

        :param str task_id:
        :rtype: aio_task.task.Task
        :raises: ValueError if task not found
        """
        pass
