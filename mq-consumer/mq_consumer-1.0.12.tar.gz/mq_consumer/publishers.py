import logging

import pika
import pika.exceptions

from .connectors import Connector, Reconnector
from . import dumpers


class Publisher:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.create_connection()

    def publish(self, **params):
        self.connector.channel.basic_publish(**params)

    def send_message(self, message, content_type='text/plain', delay=0, properties=None):
        dumper = dumpers.get_dumper(content_type)
        if dumper is None:
            raise RuntimeError("Can't dumper by content type %s" % content_type)
        message = dumper(message)
        properties = properties or {}
        properties.update({
            'delivery_mode': 2,
            'content_type': content_type
        })
        if delay != 0:
            assert self.connector.use_delay, u'Publisher must have delay support'
            properties.update({
                'headers': {
                    'x-delay': delay
                }
            })
        params = {
            "exchange": self.connector.exchange,
            "routing_key": self.connector.routing_key,
            "body": message,
            "properties": pika.BasicProperties(**properties)
        }
        self.publish(**params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connector.close()


class ReconPublisher(Publisher):
    def __init__(self, connector: Reconnector, logger: logging.Logger = None):
        assert isinstance(connector, Reconnector), 'connector must be Reconnector instance'
        self.logger = logger
        super().__init__(connector)

    def publish(self, **params):
        while True:
            try:
                super(ReconPublisher, self).publish(**params)
                break
            except pika.exceptions.AMQPError:
                if self.logger:
                    self.logger.exception('RabbitMQ publisher exception')
                self.connector.create_connection()


class JSONPublisher(Publisher):
    def send_message(self, message, delay=0, properties=None):
        return super().send_message(
            message, content_type="application/json", delay=delay, properties=properties,
        )
