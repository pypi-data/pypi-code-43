""" Define Queue interface. """
from abc import ABC


class Message:
    """ Items in queue. """

    def __init__(self, task):
        self.task = task

    @property
    def task_name(self):
        return self.task.name

    @property
    def params(self):
        return self.task.params

    def set_task_result(self, result):
        """ Set result for a task. """
        self.task.set_result(result)


class Producer(ABC):
    """ Queue interface used to produce tasks. """

    @classmethod
    async def create(cls, queue_conf):
        """ Create a new queue instance.

        :param dict queue_conf:
        :rtype: Queue
        """
        pass

    async def close(self):
        """ Shutdown. """
        pass

    async def push(self, task):
        """ Add a task to the queue.

        :param Task task:
        """
        pass


class Consumer(ABC):
    """ Queue interface used to consume tasks. """

    @classmethod
    async def create(cls, queue_conf, callback):
        """ Create a new queue instance.

        :param dict queue_conf:
        :param callback: coroutine called on new message with Message as param.
        :rtype: Queue
        """
        pass

    async def close(self):
        """ Shutdown. """
        pass

    async def start(self):
        """ Start to consum messsages. """
        pass

    async def ack(self, message):
        """ Acknoledge a message was processed → remove it from the queue. """
        pass
