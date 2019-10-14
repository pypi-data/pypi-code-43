""" Worker unit tests. """
import asyncio
import logging

import asynctest

from aio_task.worker import Worker
from aio_task.broker import Broker


class TestWorker(asynctest.TestCase):
    """ Test worker implementation. """

    async def setUp(self):
        self.broker = await Broker.create(queue_type="dummy",
                                          queue_conf=None,
                                          cache_type="dummy",
                                          cache_conf=None)
        self.worker = await Worker.create(queue_type="dummy",
                                          queue_conf=None,
                                          cache_type="dummy",
                                          cache_conf=None)

    async def tearDown(self):
        await self.broker.close()
        await self.worker.close()

    async def test_register_handler(self):
        """ Register an handler for a task. """
        # Given
        handler = asynctest.CoroutineMock()
        # When
        self.worker.register_handler(handler, task_name="task1")
        await self.worker.start()
        # Then
        await self.broker.create_task("task1")
        await asyncio.sleep(0.1)
        handler.assert_called_once()

    async def test_register_two_handlers_for_a_task(self):
        """ Could not register two handler for a task. """
        # Given
        handler = asynctest.CoroutineMock()
        # When
        self.worker.register_handler(handler, task_name="task1")
        # Then
        with self.assertRaises(ValueError):
            self.worker.register_handler(handler, task_name="task1")

    async def test_register_task_after_start(self):
        """ Can not register a task after a start. """
        # Given
        handler = asynctest.CoroutineMock()
        # When
        await self.worker.start()
        # Then
        with self.assertRaises(RuntimeError):
            self.worker.register_handler(handler, task_name="task1")

    @asynctest.patch("logging.exception", asynctest.Mock())
    async def test_task_errored(self):
        """ Task raises an exception. """
        handler = asynctest.CoroutineMock()
        handler.side_effect = ValueError("Oops")
        self.worker.register_handler(handler, task_name="task")
        await self.worker.start()
        # When
        task_id = await self.broker.create_task("task")
        # Then
        await asyncio.sleep(0.1)
        task = await self.broker.get_task(task_id)
        self.assertEqual(task.result, {"exception": {"class": "ValueError",
                                                     "args": ("Oops",),
                                                     "str": "Oops"}})
        logging.exception.assert_called()

    @asynctest.patch("logging.error", asynctest.Mock())
    async def test_not_serializable_result(self):
        """ Task returns a non serializable result. """
        handler = asynctest.CoroutineMock()
        handler.return_value = set("OK")
        self.worker.register_handler(handler, task_name="task")
        await self.worker.start()
        # When
        task_id = await self.broker.create_task("task")
        # Then
        await asyncio.sleep(0.1)
        task = await self.broker.get_task(task_id)
        self.assertEqual(task.result["exception"]["str"],
                         "Task result is not serializable")
        logging.error.assert_called()
