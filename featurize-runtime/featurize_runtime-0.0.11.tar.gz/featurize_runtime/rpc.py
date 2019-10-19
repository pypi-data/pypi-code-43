import grpc
from featurize_jupyterlab import minetorch_pb2_grpc
from featurize_jupyterlab import minetorch_pb2
from functools import wraps


def retry(number):
    def decorator(func):
        @wraps(func)
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

    def __init__(self, addr, identity):
        self.channel = grpc.insecure_channel(addr)
        self.stub = minetorch_pb2_grpc.MinetorchStub(self.channel)
        self.identity =identity

    @retry(3)
    def create_graph(self, graph_name):
        message = minetorch_pb2.Graph(
            identity=self.identity,
            graph_name=graph_name,
        )
        return self.stub.CreateGraph(message)

    @retry(3)
    def add_point(self, graph_name, x, y):
        message = minetorch_pb2.Point(
            identity=self.identity,
            graph_name=graph_name,
            x=x,
            y=y
        )
        return self.stub.AddPoint(message)

    @retry(3)
    def heyYo(self, identity, status):
        message = minetorch_pb2.HeyMessage(
            # TODO: we can get ip from server, don't need this
            ip_addr='client ip addr',
            status=status,
            identity=identity
        )
        return self.stub.HeyYo(message)

    @retry(3)
    def log(self, identity, record):
        message = minetorch_pb2.Log(
            identity=identity,
            log=record.msg,
            level=record.levelname
        )
        return self.stub.SendLog(message)
