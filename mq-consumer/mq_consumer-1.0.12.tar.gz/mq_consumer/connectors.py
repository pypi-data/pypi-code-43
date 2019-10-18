import sys

import pika
import pika.credentials
import pika.exceptions


class Connector:
    DIRECT_TYPE = 'direct'
    FANOUT_TYPE  = 'fanout'
    TOPIC_TYPE = 'topic'
    HEADERS_TYPE = 'headers'

    DELAY_TYPE = 'x-delayed-message'

    def __init__(self,
                 connection_parameters: pika.ConnectionParameters,
                 exchange: str,
                 queue: str,
                 routing_key: str = None,
                 prefetch_count: int = 1,
                 exchange_type: str = DIRECT_TYPE,
                 use_delay: bool = False):
        self.connection_parameters = connection_parameters
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue
        self.routing_key = routing_key or queue
        self.prefetch_count = prefetch_count
        self.connection = None
        self.channel = None
        self.declared_queue = None
        self.use_delay = use_delay

    def create_connection(self, declare=True):
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()
        if declare:
            self.declared_queue = self.channel.queue_declare(queue=self.queue, durable=True)
            if self.use_delay:
                exchange_type = self.DELAY_TYPE
                arguments = {"x-delayed-type": self.exchange_type}
            else:
                exchange_type = self.exchange_type
                arguments = None
            self.channel.exchange_declare(
                exchange=self.exchange, exchange_type=exchange_type, durable=True, arguments=arguments
            )
            self.channel.queue_bind(self.queue, self.exchange, routing_key=self.routing_key)
            if self.prefetch_count:
                self.channel.basic_qos(prefetch_count=self.prefetch_count)

    def close(self):
        if self.connection:
            self.connection.close()


class Reconnector(Connector):
    def __init__(self, connection_parameters: pika.ConnectionParameters, *args, **kwargs):
        connection_parameters.connection_attempts = sys.maxsize
        super().__init__(connection_parameters, *args, **kwargs)
