from kombu import Connection, Exchange, Queue
from ehelply_bootstrapper.mq.worker import Worker
from typing import List
from typing import Type


class MQConsumer:
    """
    A class which sets up a server to read events as they are taken off the message queue
    """

    def __init__(self, exchange: Exchange):
        self.exchange: Exchange = exchange
        self.queues: List[Queue] = []

    def add_queue(self, name: str, routing: str):
        self.queues.append(Queue(name, self.exchange, routing_key=routing))

    def run(self, connection_string: str, worker: Type[Worker] = Worker, heartbeat=4):
        with Connection(connection_string, heartbeat) as connection:
            worker(connection, self.queues).run()
