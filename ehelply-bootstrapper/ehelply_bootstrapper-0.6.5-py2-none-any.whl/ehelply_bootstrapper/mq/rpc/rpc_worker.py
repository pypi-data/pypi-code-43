from kombu import Connection, Queue, Message
from kombu.mixins import ConsumerProducerMixin


class RPCWorker(ConsumerProducerMixin):
    """
    Use this class to process RPC messages

    Only override the process_message function
    """
    def __init__(self, connection: Connection, queues: Queue):
        self.connection = connection
        self.queue = queues

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queue, callbacks=[self.on_message])]

    def on_message(self, body, message: Message):
        self.reply(self.process_message(body, message), message)
        message.ack()

    def reply(self, result: dict, message: Message):
        self.producer.publish(result, routing_key=message.properties['reply_to'])

    def process_message(self, body, message: Message) -> dict:
        print("Request: %s" % body)
        return {"no": "yes"}
