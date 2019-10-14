""" Broker unit tests. """
import logging
import asyncio

import asynctest

from aio_task.broker import Broker
from aio_task.worker import Worker


async def create_dummy_worker():
    return await Worker.create(queue_type="dummy",
                               queue_conf=None,
                               cache_type="dummy",
                               cache_conf=None)


class TestBroker(asynctest.TestCase):
    """ Test broker implementation. """
    use_default_loop = True

    async def setUp(self):
        self.broker = await Broker.create(queue_type="dummy",
                                          queue_conf=None,
                                          cache_type="dummy",
                                          cache_conf=None)
        self.worker = await create_dummy_worker()
        self.worker2 = None

    async def tearDown(self):
        await self.broker.close()
        await self.worker.close()
        if self.worker2 is not None:
            await self.worker2.close()

    async def test_create_task(self):
        """ Create a sample task. """
        # Given
        async def addition(x, y):
            return x + y

        self.worker.register_handler(addition)
        await self.worker.start()
        # When
        task_id = await self.broker.create_task("addition", {"x": 1, "y": 1})
        await asyncio.sleep(1)
        # Then
        task = await self.broker.get_task(task_id)
        self.assertEqual(task.result, 2)

    @asynctest.patch("logging.error", asynctest.Mock())
    async def test_create_task_without_consumer(self):
        """ Create a task but no handler was registred for the task. """
        await self.worker.start()
        # When
        task_id = await self.broker.create_task("addition", {"x": 1, "y": 1})
        # Then
        await asyncio.sleep(1)
        task = await self.broker.get_task(task_id)

        self.assertEqual(task.result["exception"]["str"],
                         "can not processed addition, no handler...")

        logging.error.assert_called()

    async def test_retry_delivery_on_consumer_error(self):
        """ If a consumer crash during the task processing,
        it's processed by another consumer.
        """
        # Given
        handler = asynctest.CoroutineMock()
        handler.return_value = 42
        # worker stop when queue receiv a message
        self.worker.queue.callback = asynctest.CoroutineMock()
        self.worker.queue.callback.side_effect = RuntimeError("out of memory")

        self.worker.register_handler(handler, task_name="handler")
        await self.worker.start()
        # When
        task_id = await self.broker.create_task("handler", {})
        await asyncio.sleep(1)
        # Then
        task = await self.broker.get_task(task_id)
        self.assertFalse(task.done)
        # When
        # another worker
        self.worker2 = await create_dummy_worker()
        self.worker2.register_handler(handler, task_name="handler")
        await self.worker2.start()
        # Then
        await asyncio.sleep(1)
        task = await self.broker.get_task(task_id)

        self.assertTrue(task.done)
        handler.assert_awaited_once()

    async def test_loadbalancing_accross_consumers(self):
        """ Two time consuming tasks are processing by the two consumers. """
        # Given
        handler1 = asynctest.CoroutineMock()
        handler1.return_value = asyncio.sleep(1)

        handler2 = asynctest.CoroutineMock()
        handler2.return_value = asyncio.sleep(1)

        self.worker.register_handler(handler1, task_name="new_op")
        await self.worker.start()

        self.worker2 = await create_dummy_worker()
        self.worker2.register_handler(handler2, task_name="new_op")
        await self.worker2.start()
        # When
        task1_id = await self.broker.create_task("new_op", {})
        task2_id = await self.broker.create_task("new_op", {})
        await asyncio.sleep(1.1)
        # Then
        task1 = await self.broker.get_task(task1_id)
        self.assertTrue(task1.done)
        handler1.assert_awaited_once()

        task2 = await self.broker.get_task(task2_id)
        self.assertTrue(task2.done)
        handler2.assert_awaited_once()
