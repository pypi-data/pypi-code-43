from kombu import Connection, Producer, Queue, Consumer, Message
from typing import Callable


class RPCProducer:
    """
    This class will begin an RPC and process the received response
    """

    def __init__(self, connection_string: str, routing: str, callback: Callable[[dict, Message], None] = None):
        from ehelply_bootstrapper.mq.mq import make_basic_exchange
        self.exchange = make_basic_exchange("rpc")
        self.conn = Connection(connection_string)
        self.routing = routing
        self.callback = callback
        self.reply_queue = Queue(name="amq.rabbitmq.reply-to")

    def call(self, payload: dict, ):
        with Consumer(self.conn, self.reply_queue, callbacks=[self.on_message], no_ack=True):
            producer = Producer(exchange=self.exchange, channel=self.conn, routing_key=self.routing)
            properties = {
                "reply_to": "amq.rabbitmq.reply-to",
            }
            producer.publish(payload, **properties)
            self.conn.drain_events()

    def on_message(self, body: dict, message: Message):
        callback_function = self.default_callback
        if self.callback is not None:
            callback_function = self.callback
        callback_function(body, message)
        message.ack()

    @staticmethod
    def default_callback(body, message: Message):
        print("RPC Response:\n%s" % body)
