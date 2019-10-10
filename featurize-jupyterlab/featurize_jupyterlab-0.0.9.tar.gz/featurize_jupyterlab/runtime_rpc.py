import grpc
from .proto import minetorch_pb2_grpc
from .proto import minetorch_pb2


def retry(number):
    def decorator(func):
        def __decorator(*args, **kwargs):
            nonlocal number
            for _ in range(number - 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    continue
            return func(*args, **kwargs)
        return __decorator
    return decorator


class RuntimeRpc():
    """
    TODO: The very first RPC call after forking the child process will fail 100%,
    it will be ok for the second call by retry, not sure why but we can dump the
    network traffic to see what really happens.

    TODO: This should work when there is no network, all the rpc call should be
    persisted and queued in local disk. Maybe provide a @queue decorator.
    """

    def __init__(self, addr, experiment_id):
        self.channel = grpc.insecure_channel(addr)
        self.stub = minetorch_pb2_grpc.MinetorchStub(self.channel)
        self.experiment_id = experiment_id

    @retry(3)
    def create_graph(self, graph_name):
        message = minetorch_pb2.Graph(
            experiment_id=self.experiment_id,
            graph_name=graph_name
        )
        return self.stub.CreateGraph(message)

    @retry(3)
    def add_point(self, graph_name, y):
        message = minetorch_pb2.Point(
            experiment_id=self.experiment_id,
            graph_name=graph_name,
            y=y
        )
        return self.stub.AddPoint(message)

    @retry(3)
    def heyYo(self, experiment_id, status):
        message = minetorch_pb2.HeyMessage(
            # TODO: we can get ip from server, don't need this
            ip_addr='client ip addr',
            status=status,
            experiment_id=experiment_id
        )
        return self.stub.HeyYo(message)

    @retry(3)
    def log(self, experiment_id, record):
        message = minetorch_pb2.Log(
            experiment_id=experiment_id,
            log=record.msg,
            level=record.levelname
        )
        return self.stub.SendLog(message)
