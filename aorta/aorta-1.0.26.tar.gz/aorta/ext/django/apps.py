import os
import logging

import ioc
from django.apps import AppConfig
from django.conf import settings

from aorta.buf import BlockingBuffer
from aorta.buf import NullBuffer
from aorta.ext.django.lib.providers import DjangoEventListenerProvider
from aorta.ext.django.lib.providers import DjangoCommandHandlerProvider
from aorta.publisher import EventPublisher
from aorta.publisher import CommandPublisher


logger = logging.getLogger('django')


class AortaConfig(AppConfig):
    name = 'aorta.ext.django'
    verbose_name = "Aorta Messaging Framework"

    def get_egress_addr(self):
        """Returns the host address and port for egress messages
        e.g. commands, events. Looks first in Django settings for
        ``AORTA_EGRESS_HOST``, ``AORTA_HOST``, then in the
        operating system environment for similarly named variables.
        Same applies for port.
        """
        port = getattr(settings, 'AORTA_EGRESS_PORT', None)\
            or getattr(settings, 'AORTA_PORT', None)\
            or os.getenv('AORTA_EGRESS_PORT')\
            or os.getenv('AORTA_PORT')
        secure = getattr(settings, 'AORTA_SECURE', None)\
            or (os.getenv('AORTA_SECURE') == '1')\
            or str(port) == '5671'
        if port is None:
            port = 5671 if secure else 5672
        protocol = 'amqp'
        if secure:
            protocol = 'amqps'
        host = getattr(settings, 'AORTA_EGRESS_HOST', None)\
            or getattr(settings, 'AORTA_HOST', None)\
            or os.getenv('AORTA_EGRESS_HOST')\
            or os.getenv('AORTA_HOST')
        return f"{protocol}://{host}:{port}" if host else None

    def get_egress_channel(self):
        """Returns the destination at the AMQP peer to publish
        outgoing messages to.
        """
        return getattr(settings, 'AORTA_EGRESS_CHANNEL', None)\
            or os.getenv('AORTA_EGRESS_CHANNEL')

    def get_egress_buffer(self):
        """Returns the buffer implementation for egress messages."""
        if not self.egress_address or not self.egress_channel:
            logger.warning(
                "Unable to determine Aorta host, port or channel "
                "from settings and environment. Using NullBuffer; "
                "egress messages are not published.")
            return NullBuffer()

        return BlockingBuffer(self.egress_address)

    def ready(self):
        self.listeners = ioc.provide('EventListenerProvider',
            DjangoEventListenerProvider())
        self.handlers = ioc.provide('CommandHandlerProvider',
            DjangoCommandHandlerProvider())
        self.listeners.autodiscover()
        self.handlers.autodiscover()
        self.egress_address = self.get_egress_addr()
        self.egress_channel = self.get_egress_channel()
        self.egress_buffer = self.get_egress_buffer()
        self.gateway = ioc.provide('CommandGateway',
            CommandPublisher(backend=self.egress_buffer,
                address=self.egress_channel)
        )
        self.publisher = ioc.provide('EventPublisher',
            EventPublisher(backend=self.egress_buffer,
                address=self.egress_channel)
        )

