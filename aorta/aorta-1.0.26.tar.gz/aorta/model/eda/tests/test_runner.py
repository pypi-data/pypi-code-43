import unittest

import aorta
import ioc
from aorta.messaging import EventMessage
from aorta.messaging.runner import MessageRunner
from aorta.messaging.middleware import MiddlewareRunner

from .listeners import FailingEventListener
from .listeners import FailingOnFinishedEventListener
from .listeners import FailingOnExceptionEventListener
from .listeners import HandledEventListener


class EventRunnerTestCase(unittest.TestCase):
    provider_class = aorta.eda.EventListenerProvider
    runner_class = MessageRunner

    def setUp(self):
        self.provider = self.provider_class()
        self.provider.add(HandledEventListener)
        self.provider.add(FailingEventListener)
        self.provider.add(FailingOnFinishedEventListener)
        self.provider.add(FailingOnExceptionEventListener)

        self.runner = self.runner_class(self.provider)

        ioc.provide('aorta.MiddlewareRunner', MiddlewareRunner())

    def tearDown(self):
        ioc.teardown()

    def test_run_valid_event_message_without_handlers_returns_false(self):
        message = EventMessage(body={'foo': 'bar', 'baz': 'taz'})
        message.set_object_type('UnhandledEvent')
        self.assertFalse(self.runner.run(message))

    def test_run_valid_event_message_with_handlers_returns_true(self):
        message = EventMessage(body={'foo': 'bar', 'baz': 'taz'})
        message.set_object_type('HandledEvent')
        self.assertTrue(self.runner.run(message))

    def test_exception_in_handle_does_not_kill_everything(self):
        message = EventMessage(body={'foo': 'bar', 'baz': 'taz'})
        message.set_object_type('FailingEvent')
        self.assertTrue(self.runner.run(message))

    def test_exception_in_on_finished_does_not_kill_everything(self):
        message = EventMessage(body={'foo': 'bar', 'baz': 'taz'})
        message.set_object_type('FailingOnFinishedEvent')
        self.assertTrue(self.runner.run(message))

    def test_exception_in_on_exception_does_not_kill_everything(self):
        message = EventMessage(body={'foo': 'bar', 'baz': 'taz'})
        message.set_object_type('FailingOnExceptionEvent')
        self.assertTrue(self.runner.run(message))
