from Queue import Queue
import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from p4.tmp import p4config_pb2
from p4.v1.p4runtime_pb2 import GetForwardingPipelineConfigRequest

connections = []


class IterableQueue(Queue):
    _sentinel = object()

    def __iter__(self):
        return iter(self.get, self._sentinel)

    def close(self):
        self.put(self._sentinel)


class P4RuntimeClient:

    def __init__(self):
        self.address = '127.0.0.1:50051'
        self.device_id = 0
        self.channel = grpc.insecure_channel(self.address)
        self.client_stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)
        self.requests_stream = IterableQueue()
        self.stream_msg_resp = self.client_stub.StreamChannel(iter(self.requests_stream))
        connections.append(self)

    def build_device_config(self, config_file_path):
        device_config = p4config_pb2.P4DeviceConfig()
        device_config.reassign = True
        with open(config_file_path) as f:
            device_config.device_data = f.read()
        return device_config

    def set_forwarding_pipeline_config_request(self, pipeline_id, p4info, **kwargs):
        device_config = self.build_device_config(**kwargs)
        request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
        request.election_id.low = 1
        request.device_id = self.device_id
        request.pipeline_id = pipeline_id
        config = request.config

        config.p4info.CopyFrom(p4info)
        config.p4_device_config = device_config.SerializeToString()

        request.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
        self.client_stub.SetForwardingPipelineConfig(request)

    def get_forwarding_pipeline_config_request(self, pipeline_id, response_type):
        request = p4runtime_pb2.GetForwardingPipelineConfigRequest()
        request.device_id = self.device_id
        request.pipeline_id = pipeline_id

        enum = GetForwardingPipelineConfigRequest.ResponseType.DESCRIPTOR.values_by_name[response_type]
        request.response_type = enum.number

        response = self.client_stub.GetForwardingPipelineConfig(request)

        config = response.config

        return config

    def write_table_entry(self, pipeline_id, table_entry, update_type):
        request = p4runtime_pb2.WriteRequest()
        request.device_id = self.device_id
        request.election_id.low = 1
        request.pipeline_id = pipeline_id
        update = request.updates.add()
        update.type = update_type
        update.entity.table_entry.CopyFrom(table_entry)
        return self.client_stub.Write(request)

    def read_table_entries(self, pipeline_id, table_id):
        request = p4runtime_pb2.ReadRequest()
        request.device_id = self.device_id
        request.pipeline_id = pipeline_id
        entity = request.entities.add()
        table_entry = entity.table_entry
        table_entry.table_id = table_id
        for response in self.client_stub.Read(request):
                yield response
