import logging
import uuid

import ioc
from proton.handlers import MessagingHandler
from proton.reactor import Container
from proton.reactor import Selector

import aorta.messaging
import aorta.const
from aorta.messaging.runner import MessageRunner


class AortaClient(MessagingHandler):
    logger = logging.getLogger('aorta.client')

    @classmethod
    def run(cls, host, port, *args , **kwargs):
        return Container(cls(host, port, **kwargs)).run()

    def __init__(self, host, port, container_id=None, *args, **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.client_id = container_id or str(uuid.uuid4())
        self.channel = kwargs.pop('channel', None)
        self.runners = {
            'event': MessageRunner(ioc.require('EventListenerProvider')),
            'command': MessageRunner(ioc.require('CommandHandlerProvider')),
        }

    def on_start(self, event):
        """Setup the receivers and runtime environment for the
        client.
        """
        self.logger.info("Starting Aorta client.")
        if not self.channel:
            self.logger.error("No ingress message channel configured")
            return
        self.container = container = event.container
        container.container_id = self.client_id

        # Setup the connection with a predicate determined from
        # the registered message handlers.
        self.connection = connection = container.connect(
            f'amqp://{self.host}:{self.port}')
        self.receiver = container.create_receiver(connection,
            source=self.channel,
            options=self.get_selectors())

    def on_link_opened(self, event):
        self.logger.info("Established receiving link from remote source %s",
            event.link.remote_source.address)

    def on_message(self, event):
        message = aorta.messaging.factory(event.message)

        # This should not happen because we filter on specific AORTA_CLASS
        # values, meaning that we only receive messages that are produced
        # through the Aorta framework. We check just in case.
        if not message.is_aorta:
            self.logger.warning("Dropped message (id: %s): unknown format",
                message.get_message_id())
            return

        if message.isconsumable():
            # TODO: Configure the handler to not auto-accept message,
            # and accept a consumable message here.
            pass

        # TODO: Validate the message here; basic properties such as
        # AORTA_CLASS, AORTA_CANONICAL
        self.logger.debug("Accepted incoming message of class %s (id: %s)",
            message.message_class, message.get_message_id())
        try:
            runner = self.runners[message.message_class]
            result = runner.run(message)
        except Exception as e:
            self.logger.exception("Caught fatal %s",
                type(e).__name__)

        self.logger.debug("Ran %s handlers against %s %s (id: %s)",
            result, message.message_class, message.canonical,
            message.get_message_id())

    def get_selectors(self):
        """Return the predicate used to filter incoming messages."""
        message_classes = []
        if self.runners['event'].has_handlers():
            message_classes.append(aorta.messaging.EventMessage.message_class)
        if self.runners['command'].has_handlers():
            message_classes.append(aorta.messaging.CommandMessage.message_class)

        p = ''
        if len(message_classes) > 1:
            message_classes = ', '.join(map(repr, message_classes))
            p = f'{aorta.const.P_MESSAGE_CLASS} IN ({message_classes})'
        elif len(message_classes) == 1:
            p = f'{aorta.const.P_MESSAGE_CLASS} = \'{message_classes[0]}\''

        if p:
            p = Selector(p)

        return [p] if p else None
