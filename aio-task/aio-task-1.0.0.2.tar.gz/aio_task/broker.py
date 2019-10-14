""" Broker produce tasks that will be processed by consumers. """
import logging
from aio_task.task import Task
from aio_task.utils import load_cache, load_producer


class Broker:
    """ Task getter and producer. """

    def __init__(self):
        self.queue = None
        self.cache = None

    @classmethod
    async def create(cls, queue_type, queue_conf, cache_type, cache_conf):
        """ Create a new broker instance. """
        broker = cls()
        cache_klass = load_cache(cache_type)
        broker.cache = await cache_klass.create(cache_conf)

        queue_klass = load_producer(queue_type)
        broker.queue = await queue_klass.create(queue_conf)
        logging.info(f"broker ready. cache: {cache_type}, queue: {queue_type}")
        return broker

    async def close(self):
        """ Shutdown. """
        if self.queue is not None:
            await self.queue.close()
        if self.cache is not None:
            await self.cache.close()
        logging.info("broker closed")

    async def create_task(self, task_name, params=None):
        """ Create a new task.

        :param str task_name:
        :param dict params:

        :returns: A task_id
        :rtype: str
        :raises: ValueError is task_name is not referencing any task.
        """
        logging.debug(f"create task {task_name}")
        task = Task.new(task_name, params or {})
        await self.cache.save_task(task)
        await self.queue.push(task)
        return task.task_id

    async def get_task(self, task_id):
        """ Fetch a task

        :param task
        :rtype: Task
        :raises: ValueError is task_id is not referencing any task.
        """
        return await self.cache.get_task(task_id)
