import asyncio
import inspect
import threading
import logging
import os

from proton.handlers import MessagingHandler
from proton.reactor import ApplicationEvent
from proton.reactor import Container
from proton.reactor import EventInjector

from aorta.messaging import Message
from aorta.context import Context
import aorta.utils


class MessageConsumer(MessagingHandler):
    """A :class:`~proton.handlers.MessagingHandler` implementation that runs
    a handler function on incoming messages.
    """

    def __init__(self, handle, is_operational, spool=None, channels=None, logger=None):
        MessagingHandler.__init__(self, prefetch=1, auto_accept=False,
            auto_settle=False)
        self.injector = EventInjector()
        self.handle = handle
        self.is_operational = is_operational
        self.spool = spool or os.environ.get('AORTA_SPOOL_DIR','/var/spool/aorta')
        self.channels = channels or []
        self.logger = logger or logging.getLogger('aorta')
        self.links = []
        self.container = Container(self)
        self.thread = threading.Thread(target=self.container.run)
        self.loop = None

    def get_context(self, message):
        """Return a :class:`aorta.context.Context` instance representing the
        context of the incoming message.
        """
        return Context(
            user_id=message.user_id,
            correlation_id=message.correlation_id,
            message_id=message.id,
            logger=self.logger,
            spool=self.spool
        )

    def start(self):
        self.thread.start()

    def beat(self):
        """Beats the :class:`MessageConsumer`."""
        self.injector.trigger(ApplicationEvent('beat'))

    def teardown(self):
        self.injector.trigger(ApplicationEvent('teardown'))

    def on_start(self, event):
        """Invoked when the container is entering its main event loop."""
        assert callable(self.handle), "MessageConsumer.handle must be callable"
        assert callable(self.is_operational),\
            "MessageConsumer.is_operational must be callable"
        self.container = container = event.container
        if not self.channels:
            self.logger.warning("No channels configured for MessageConsumer")
        for dsn in self.channels:
            self.logger.debug("Creating AMQP link %s", dsn)
            link = container.create_receiver(dsn)
            link.flow(0)
            if self.is_operational():
                self.notify_ready(link)
            self.links.append(link)

        # Ensure that the EventInjector is selectable, so that callers
        # can publish ApplicationEvent instances.
        container.selectable(self.injector)

        # Ensure that we have an event loop for coroutines.
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def on_beat(self, event):
        pass

    def on_teardown(self, event):
        """Tear down all AMQP links and release resources."""
        self.injector.close()
        for link in self.links:
            self.logger.debug("Closing link %s", link.source.address)
            link.close()
        self.container.stop()

    def on_message(self, event):
        """Invoked when a message is received from a channel that the
        :class:`MessageConsumer` is subscribing to.
        """
        message = event.message
        link = event.link
        delivery = event.delivery
        if not Message.is_valid(event.message):
            self.logger.critical("Rejecting message %s", message.id)
            self.reject(delivery)
            return

        context =  self.get_context(message)

        # If the application is not operational, release the message and allow the
        # AMQP peer to retransmit at its own discretion.
        if not self.is_operational():
            self.logger.debug("System is not in operational state, releasing message %s",
                message.id)
            self.release(delivery, delivered=False)
            return

        # TODO: If a power failure or application crash occurs after
        # MessageConsumer.accept() returns, but before the handler is
        # ran, the message is lost.
        self.logger.debug("Accepting message %s from source %s",
            message.id, link.source.address)
        self.accept(delivery)
        try:
            self.run_handler(self.handle, context, message)
        except Exception as e:
            self.logger.exception("Message %s from source %s caused a fatal exception",
                message.id, link.source.address)

        # Increase the link credit by 1 so that the AMQP peer may send the
        # next message to the consumer.
        self.notify_ready(link)

    def run_handler(self, func, context, message):
        result = func(context, message)
        if inspect.iscoroutinefunction(func):
            fut = asyncio.ensure_future(result)
            loop.run_until_complete(fut)
            result = fut.result()
        return result

    def notify_ready(self, link):
        """Notify the AMQP peer that we are ready to receive the next
        enqueued message.
        """
        self.logger.debug("Increasing link credit by 1 for peer %s",
            link.source.address)
        link.flow(1)
