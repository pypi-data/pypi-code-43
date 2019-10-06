from kombu import Connection, Queue
from typing import Type
from ehelply_bootstrapper.mq.rpc.rpc_worker import RPCWorker


class RPCConsumer:
    """
    This class receives an RPC call, processes it, and sends a response back
    """

    def __init__(self, routing: str):
        from ehelply_bootstrapper.mq.mq import make_basic_exchange
        exchange = make_basic_exchange("rpc")
        self.request_queue = Queue(name="rpc", exchange=exchange, routing_key=routing)

    def run(self, connection_string: str, worker: Type[RPCWorker] = RPCWorker, heartbeat=4):
        with Connection(connection_string, heartbeat) as connection:
            worker(connection, self.request_queue).run()
