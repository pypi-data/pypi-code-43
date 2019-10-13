from kombu import Connection, Exchange
from kombu.pools import producers


class MQProducer:
    """
    A class which sets up a `client` to emit events on to the message queue
    """

    def __init__(self, exchange: Exchange, connection_string: str, routing: str):
        self.exchange: Exchange = exchange
        self.routing: str = routing
        self.connection_string: str = connection_string

    def publish(self, payload):
        with producers[Connection(self.connection_string)].acquire(block=True) as producer:
            producer.publish(payload, exchange=self.exchange, routing_key=self.routing, serializer='json',
                             compression='zlib', declare=[self.exchange], retry=True)
