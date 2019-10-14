""" Default tests for a Queue. """
import os
import asyncio
import asynctest
from aio_task.task import Task
from aio_task.queue.dummy import Producer, Consumer
from aio_task.queue.rabbitmq import (Producer as RMQProducer,
                                     Consumer as RMQConsumer)


class TestQueue(asynctest.TestCase):
    """ Common tests for Queue. """
    use_default_loop = True

    async def setUp(self):
        self.coro_mock = asynctest.CoroutineMock()
        self.producer = await Producer.create(None)
        self.consumer = await Consumer.create(None, self.callback)
        await self.consumer.start()

    async def tearDown(self):
        await self.producer.close()
        await self.consumer.close()

    async def callback(self, message):
        """ Sample callback. """
        await self.coro_mock(message)
        await self.consumer.ack(message)

    async def test_push_message(self):
        """ Simple test pushing a message. """
        task = Task.new("dummy", {})
        # When
        await self.producer.push(task)
        # Then
        await asyncio.sleep(1)
        self.coro_mock.assert_called_once()

    async def test_push_multiple_messages(self):
        """ Push several messages. """
        task = Task.new("dummy", {})
        # When
        await asyncio.gather(*[self.producer.push(task) for _ in range(10)])
        # Then
        await asyncio.sleep(1)
        self.assertEqual(self.coro_mock.await_count, 10)

    async def test_not_ack_messages(self):
        """ Callback have to ack the message to process other one. """
        self.consumer.callback = self.coro_mock
        task = Task.new("dummy", {})
        # When
        await asyncio.gather(*[self.producer.push(task) for _ in range(10)])
        # Then
        await asyncio.sleep(1)
        self.assertEqual(self.coro_mock.await_count, 1)


class TestRabbitmq(TestQueue):
    """ Common tests for Queue. """
    use_default_loop = True

    HOST = os.getenv("IP_HOST", "rabbitmq")

    async def setUp(self):
        self.coro_mock = asynctest.CoroutineMock()
        self.config = {"url": f"amqp://guest:guest@{self.HOST}:5672",
                       "routing_key": "tasks_queue"}
        self.producer = await RMQProducer.create(self.config)
        self.consumer = await RMQConsumer.create(self.config, self.callback)
        await self.consumer.start()

    async def tearDown(self):
        await self.producer.close()
        await self.consumer.close()
        await self.purge_queue()

    async def purge_queue(self):
        """ Clean queue. """
        from aio_pika import connect

        connection = await connect(self.config["url"])
        channel = await connection.channel()
        # Clean queue
        queue = await channel.declare_queue(
            self.config["routing_key"],
            durable=True
        )
        await queue.purge()
        await connection.close()
