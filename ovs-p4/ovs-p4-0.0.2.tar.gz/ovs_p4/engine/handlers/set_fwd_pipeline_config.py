import logging
from abstract import AbstractService

LOG = logging.getLogger(__name__)


class SetForwardingPipelineConfigService(AbstractService):

    def __init__(self, ovs_driver, db_conn):
        AbstractService.__init__(self, ovs_driver, db_conn)

    def handle(self, **kwargs):
        LOG.info('Handle SetForwardingPipelineConfigService')
        p4info = kwargs['p4info']
        pipeline_id = kwargs['pipeline_id']
        device_config = kwargs['device_config']

        self.ovs_driver.load_config(pipeline_id, device_config)

        self.db_conn.write_pipeline(pipeline_id, device_config, p4info)


