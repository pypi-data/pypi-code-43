import logging

from p4.tmp import p4config_pb2
from p4.v1.p4runtime_pb2 import GetForwardingPipelineConfigRequest, ForwardingPipelineConfig

from abstract import AbstractService

LOG = logging.getLogger(__name__)


class GetForwardingPipelineConfigService(AbstractService):

    def __init__(self, ovs_driver, db_conn):
        AbstractService.__init__(self, ovs_driver, db_conn)

    def handle(self, **kwargs):
        LOG.info('Handling GetForwardingPipelineConfigRequest')
        pipeline_id = kwargs['pipeline_id']
        response_type = kwargs['response_type']
        device_data = None
        p4info = None

        if response_type == GetForwardingPipelineConfigRequest.ALL:
            device_data = self.db_conn.get_device_config(pipeline_id)
            p4info = self.db_conn.get_p4info(pipeline_id)
        elif response_type == GetForwardingPipelineConfigRequest.P4INFO_AND_COOKIE:
            p4info = self.db_conn.get_p4info(pipeline_id)
        elif response_type == GetForwardingPipelineConfigRequest.DEVICE_CONFIG_AND_COOKIE:
            device_data = self.db_conn.get_device_config(pipeline_id)

        p4_device_config = None
        if device_data:
            p4_device_config = p4config_pb2.P4DeviceConfig()
            p4_device_config.device_data = device_data

        config = ForwardingPipelineConfig()
        if p4info:
            config.p4info.CopyFrom(p4info)
        if p4_device_config:
            config.p4_device_config = p4_device_config.SerializeToString()

        return config


