from p4.tmp import p4config_pb2
from ovs_p4.engine.db.connector import DbConnector
import logging

from handlers.set_fwd_pipeline_config import SetForwardingPipelineConfigService
from handlers.get_fwd_pipeline_config import GetForwardingPipelineConfigService
from handlers.write import WriteService
from handlers.read import ReadService

from ovs_p4.drivers.ovs.ovs_driver import OvsDriver


LOG = logging.getLogger(__name__)


class P4Engine(object):

    def __init__(self):
        ovs_driver = OvsDriver()
        db_conn = DbConnector()
        self.set_fwd_pipeline_config = SetForwardingPipelineConfigService(ovs_driver, db_conn)
        self.get_fwd_pipeline_config = GetForwardingPipelineConfigService(ovs_driver, db_conn)
        self.write_service = WriteService(ovs_driver, db_conn)
        self.read_service = ReadService(ovs_driver, db_conn)

    def handle_set_forwarding_pipeline_config(self, request):

        p4_device_config = p4config_pb2.P4DeviceConfig()
        p4_device_config.ParseFromString(request.config.p4_device_config)

        if len(p4_device_config.device_data) > 0:
            device_data = p4_device_config.device_data

            self.set_fwd_pipeline_config.handle(pipeline_id=request.pipeline_id,
                                                p4info=request.config.p4info,
                                                device_config=device_data)
        else:
            LOG.error("Received 0 bytes device data! Stopping set forwarding pipeline action...")


    def handle_get_forwarding_pipeline_config(self, request):

        config = self.get_fwd_pipeline_config.handle(pipeline_id=request.pipeline_id,
                                                     response_type=request.response_type)
        return config

    def handle_write_request(self, request):
        self.write_service.handle(pipeline_id=request.pipeline_id,
                                  updates=request.updates)

    def handle_read_request(self, request):
        entities = self.read_service.handle(pipeline_id=request.pipeline_id,
                                            entities=request.entities)
        return entities

