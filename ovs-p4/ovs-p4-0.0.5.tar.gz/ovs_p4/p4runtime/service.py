import logging
import grpc
from p4.v1 import p4runtime_pb2_grpc
from ovs_p4.engine.engine import P4Engine
from p4.v1.p4runtime_pb2 import SetForwardingPipelineConfigResponse, WriteResponse, GetForwardingPipelineConfigResponse, ReadResponse

LOG = logging.getLogger(__name__)


class P4RuntimeService(p4runtime_pb2_grpc.P4RuntimeServicer):

    def __init__(self):
        self.engine = P4Engine()

    def SetForwardingPipelineConfig(self, request, context):
        # try:
        self.engine.handle_set_forwarding_pipeline_config(request)
        # except Exception as e:
        # LOG.error("Exception caught: %s" % e.message)
        # context.set_code(grpc.StatusCode.INTERNAL)
        # context.set_details("Internal gRPC error!")

        context.set_code(grpc.StatusCode.OK)
        context.set_details('OK!')
        return SetForwardingPipelineConfigResponse()

    def GetForwardingPipelineConfig(self, request, context):
        config = None
        try:
            config = self.engine.handle_get_forwarding_pipeline_config(request)
        except Exception as e:
            LOG.error("Exception caught: %s" % e.message)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal gRPC error!")
        context.set_code(grpc.StatusCode.OK)
        context.set_details('OK!')
        return GetForwardingPipelineConfigResponse(config=config)

    def Write(self, request, context):
        try:
            self.engine.handle_write_request(request)
        except Exception as e:
            LOG.error("Exception caught: %s" % e.message)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e.message)
        context.set_code(grpc.StatusCode.OK)
        context.set_details('OK!')
        return WriteResponse()

    def Read(self, request, context):
        response = ReadResponse()
        entities = None
        try:
            entities = self.engine.handle_read_request(request)
        except Exception as e:
            LOG.error("Exception caught: %s" % e.message)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e.message)
        context.set_code(grpc.StatusCode.OK)
        context.set_details('OK!')

        for e in entities:
            entity = response.entities.add()
            entity.table_entry.CopyFrom(e)

        yield response

    def StreamChannel(self, request_iterator, context):
        # TODO: simple logic so far
        context.set_code(grpc.StatusCode.OK)