import logging
import time
import grpc
from concurrent import futures
from p4.v1 import p4runtime_pb2_grpc
from service import P4RuntimeService

LOG = logging.getLogger(__name__)


class P4RuntimeServer(object):

    def __init__(self):
        self.server = None

    def serve(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        p4runtime_pb2_grpc.add_P4RuntimeServicer_to_server(
            P4RuntimeService(), self.server
        )

        self.server.add_insecure_port('[::]:50051')
        self.server.start()

        LOG.info("The P4Runtime server has been started..")

        try:
            while True:
                time.sleep(1)
        except:
            self.server.stop(0)