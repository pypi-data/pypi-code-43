""" Implement Queue interface. """
import asyncio
import logging
from aio_task.queue import ProducerABC, ConsumerABC, Message


DUMMY_QUEUE = []


class Producer(ProducerABC):
    """ Dummy implementation for the producer interface. """

    @classmethod
    async def create(cls, queue_conf):
        """ Create a new queue instance.

        :param dict queue_conf:
        :rtype: Queue
        """
        return cls()

    async def close(self):
        """ Shutdown. """
        pass

    async def push(self, task):
        """ Add a task to the queue.

        :param Task task:
        """
        message = Message(task)
        DUMMY_QUEUE.append(message)
        await asyncio.sleep(0)


class Consumer(ConsumerABC):

    def __init__(self, callback):
        self._task = None
        self.callback = callback

    @classmethod
    async def create(cls, queue_conf, callback):
        """ Create a new queue instance that consumer messages.

        :param dict queue_conf:
        :param callback: coroutine called on new message with Message as param.
        :rtype: Queue
        """
        return cls(callback)

    async def close(self):
        """ Shutdown. """
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def start(self):
        """ Start to consume messages. """
        self._task = asyncio.ensure_future(self._worker())

    async def _worker(self):
        """ Consumer messages. """
        while True:
            try:
                try:
                    message = DUMMY_QUEUE[-1]
                except IndexError:
                    message = None
                else:
                    if not hasattr(message, "consumer"):
                        setattr(message, "consumer", self)
                        await self.callback(message)
            except:
                logging.exception("error processing a task.")
                if message is not None:
                    delattr(message, "consumer")
            finally:
                await asyncio.sleep(0.01)

    async def ack(self, message):
        """ Remove a message from queue. """
        try:
            DUMMY_QUEUE.remove(message)
        except ValueError:
            pass
