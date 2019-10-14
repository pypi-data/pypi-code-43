""" Implement Queue for rabbitmq using aio_pika. """
import asyncio
from contextlib import suppress
import logging

import aio_pika
from aio_pika import Message as RMQMessage, DeliveryMode

from aio_task.task import Task
from aio_task.queue import Message as MessageBase, ProducerABC, ConsumerABC


async def acquire_connection(rabbitmq_url):
    """ Try to connect until success. Wait 1 seconds before retry.

    :param str rabbitmq_url: rabbitmq url to connect to.
    :returns: aio_pika.connection
    """
    try:
        connection = await aio_pika.connect(rabbitmq_url)
    except:
        logging.exception("Fail to connect to rabbitmq. Retry in a second...")
        await asyncio.sleep(1)
        return await acquire_connection(rabbitmq_url)
    return connection


class Producer(ProducerABC):
    """ Queue interface used to produce tasks. """

    def __init__(self, rabbitmq_url, routing_key):
        """ Use :func:`~Producer.create` to get an instance. """
        self.rabbitmq_url = rabbitmq_url
        self.routing_key = routing_key
        self.connection = None
        self.channel = None

    @classmethod
    async def create(cls, queue_conf):
        """ Create a new queue instance.

        :param dict queue_conf: see below
        :rtype: Queue

        ::

            queue_conf = {
                "url": str,  # rabbitmq url
                "routing_key": str,  # default "tasks_queue"
            }
        """
        logging.info("Create rabbitmq producer.")
        rabbitmq_url = queue_conf["url"]
        routing_key = queue_conf.get("routing_key", "tasks_queue")
        producer = cls(rabbitmq_url, routing_key)
        await producer.connect()
        return producer

    async def connect(self):
        """ Acquire required connections. """
        logging.debug("Connect to rabbitmq...")
        # Perform connection
        self.connection = await acquire_connection(self.rabbitmq_url)
        # Creating a channel
        self.channel = await self.connection.channel()

    async def close(self):
        """ Shutdown. """
        logging.info("Shutdown rabbitmq producer.")
        if self.connection is not None:
            await self.connection.close()

    async def push(self, task):
        """ Add a task to the queue.

        :param Task task:
        """
        logging.debug("push task")
        # prepare message
        message_body = task.dump().encode()
        message = RMQMessage(
            message_body,
            correlation_id=task.task_id,  # use to identify task if repeated
            delivery_mode=DeliveryMode.PERSISTENT
        )
        # Sending the message
        await self.channel.default_exchange.publish(
            message, routing_key=self.routing_key
        )


class Message(MessageBase):
    """ Items in queue. """

    def __init__(self, task, rmq_message):
        """
        :param aio_task.task.Task task:
        :param IncomingMessage rmq_message:
        """
        super().__init__(task)
        self.rmq_message = rmq_message


class Consumer(ConsumerABC):
    """ Queue interface used to consume tasks. """

    def __init__(self, rabbitmq_url, routing_key, callback):
        """ Use :func:`~Consumer.create` to get an instance.

        :param str rabbitmq_url: url to connect to rmq
        :param str routing_key: should be identical to the producer one
        :param coroutine callback:
        """
        self.rabbitmq_url = rabbitmq_url
        self.routing_key = routing_key
        self.callback = callback
        self.connection = None
        self.channel = None
        self._task = None

    @classmethod
    async def create(cls, queue_conf, callback):
        """ Create a new queue instance.

        :param dict queue_conf: See :func:`~Producer.create`
        :param callback: coroutine called on new message with Message as param.
        :rtype: Queue
        """
        logging.info("Create rabbitmq consumer.")
        rabbitmq_url = queue_conf["url"]
        routing_key = queue_conf.get("routing_key", "tasks_queue")
        consumer = cls(rabbitmq_url, routing_key, callback)
        await consumer.connect()
        return consumer

    async def connect(self):
        # Creating a channel
        logging.debug("Connect to rabbitmq.")
        self.connection = await acquire_connection(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

    async def close(self):
        """ Shutdown. """
        logging.info("Shutdown rabbitmq consumer.")
        if self._task is not None:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        if self.connection is not None:
            await self.connection.close()

    async def start(self):
        """ Start to consum messsages. """
        logging.info(f"start to consume tasks on {self.routing_key}.")
        # Declaring queue
        queue = await self.channel.declare_queue(self.routing_key,
                                                 durable=True)
        self._task = asyncio.ensure_future(queue.consume(self._msg_handler))

    async def ack(self, message):
        """ Acknoledge a message was processed → remove it from the queue.

        :param Message message: arg given to the callback
        """
        message.rmq_message.ack()

    async def _msg_handler(self, message):
        """ Handler on new message from queue

        :param IncomingMessage message:
        """
        logging.debug("receiv message")
        try:
            body = message.body.decode()
            task = Task.load(body)
            msg = Message(task, message)
            await self.callback(msg)
        except:
            logging.exception(f"Error processing {message}")
