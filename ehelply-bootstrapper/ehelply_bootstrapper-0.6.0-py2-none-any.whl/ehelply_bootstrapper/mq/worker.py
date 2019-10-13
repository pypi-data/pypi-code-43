from kombu import Connection, Queue, Message
from kombu.mixins import ConsumerMixin
from typing import List


class Worker(ConsumerMixin):
    """
    An object which is responsible for handling messages as they come in

    ...

    Methods
    -------
    process_message(body, message: Message)
        This method should be overridden to implement desired behaviour
    """

    def __init__(self, connection: Connection, queues: List[Queue]):
        self.connection = connection
        self.queues = queues

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues,
                         callbacks=[self.on_message])]

    def on_message(self, body, message: Message):
        self.process_message(body, message)
        message.ack()

    def process_message(self, body, message: Message):
        print('Got message: {0}'.format(body))
