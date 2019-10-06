from kombu import Exchange
from ehelply_bootstrapper.mq.mqproducer import MQProducer
from ehelply_bootstrapper.mq.mqconsumer import MQConsumer
from ehelply_bootstrapper.mq.worker import Worker
from ehelply_bootstrapper.mq.rpc.rpc_producer import RPCProducer
from ehelply_bootstrapper.mq.rpc.rpc_consumer import RPCConsumer
from ehelply_bootstrapper.mq.rpc.rpc_worker import RPCWorker
from ehelply_bootstrapper.utils.connection_details import ConnectionDetails
from typing import Type
import threading
from typing import Callable
from kombu import Message


def make_connection_string(username: str, password: str, host: str, port: int) -> str:
    return "amqp://" + username + ":" + password + "@" + host + ":" + str(port) + "//"


def make_basic_exchange(name: str):
    return Exchange(name, type="direct")


def make_topic_exchange(name: str):
    return Exchange(name, type="topic")


class EventEmitter:
    """
    Use this class to emit messages on the message queue.

    This class uses the builder pattern to set it up, then call emit to send a message
    """

    def __init__(self, connection_details: ConnectionDetails):
        self.connection_string = make_connection_string(connection_details.username, connection_details.password, connection_details.host, connection_details.port)
        self.exchange: Exchange = Exchange('')
        self.routing: str = ''
        self.producer = None
        self.make_producer()

    def set_exchange(self, name, exchange_type="direct"):
        self.exchange = Exchange(name, type=exchange_type)
        self.make_producer()
        return self

    def set_routing(self, key):
        self.routing = key
        self.make_producer()
        return self

    def make_producer(self):
        self.producer = MQProducer(exchange=self.exchange, connection_string=self.connection_string,
                                   routing=self.routing)

    def emit(self, payload: dict):
        self.producer.publish(payload)
        return self


class RPCEmitter(EventEmitter):
    """
    Use this class to begin an RPC and call a callback after the response has been received
    """

    def __init__(self, connection_details: ConnectionDetails, callback: Callable[[dict, Message], None]=None):
        self.callback = callback
        super().__init__(connection_details)

    def make_producer(self):
        if self.callback:
            self.producer = RPCProducer(connection_string=self.connection_string,
                                        routing=self.routing, callback=self.callback)
        else:
            self.producer = RPCProducer(connection_string=self.connection_string,
                                        routing=self.routing)

    def set_callback(self, callback: Callable[[dict, Message], None]):
        self.callback = callback
        self.make_producer()
        return self

    def emit(self, payload: dict):
        self.producer.call(payload)
        return self


def mq_consumer_runner(connection_string: str, exchange: Exchange, queue_name: str, routing: str,
                       worker: Type[Worker]):
    consumer = MQConsumer(exchange=exchange)
    consumer.add_queue(queue_name, routing)
    consumer.run(connection_string=connection_string, worker=worker)


def rpc_consumer_runner(connection_string: str, routing: str, worker: Type[RPCWorker]):
    consumer = RPCConsumer(routing)
    consumer.run(connection_string=connection_string, worker=worker)


class EventHandler:
    """
    Use this class to process messages as they are taken off the bus

    This runs in a separate thread
    """
    def __init__(self, connection_details: ConnectionDetails):
        self.connection_string = make_connection_string(connection_details.username, connection_details.password, connection_details.host, connection_details.port)
        self.exchange: Exchange = Exchange('')
        self.routing: str = ''
        self.queue: str = ''
        self.consumer = None

    def set_exchange(self, name, exchange_type="direct"):
        self.exchange = Exchange(name, type=exchange_type)
        return self

    def set_queue(self, name):
        self.queue = name
        return self

    def set_routing(self, key):
        self.routing = key
        return self

    def run(self, worker: Type[Worker] = Worker):
        self.consumer = threading.Thread(target=mq_consumer_runner, args=(self.connection_string, self.exchange, self.queue, self.routing, worker))
        self.consumer.start()


class RPCHandler:
    """
    Use this class to process RPC messages and send a response back

    This runs in a separate thread
    """
    def __init__(self, connection_details: ConnectionDetails):
        self.connection_string = make_connection_string(connection_details.username, connection_details.password, connection_details.host, connection_details.port)
        self.routing: str = ''
        self.consumer = None

    def set_routing(self, key):
        self.routing = key
        return self

    def run(self, worker: Type[RPCWorker] = RPCWorker):
        self.consumer = threading.Thread(target=rpc_consumer_runner, args=(self.connection_string, self.routing, worker))
        self.consumer.start()
