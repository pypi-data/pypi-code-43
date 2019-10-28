import logging
import BTrees.OOBTree
import ZODB, ZODB.FileStorage
import transaction

from model import ForwardingPipelineConfig

LOG = logging.getLogger(__name__)


class DbConnector(object):

    def __init__(self):
        storage = ZODB.FileStorage.FileStorage('ovs-p4.fs')
        self.db = ZODB.DB(storage)

        self.pipelines = self.initialize()

    def initialize(self):
        conn = self.db.open()
        root = conn.root()
        root.pipelines = BTrees.OOBTree.BTree()
        transaction.commit()
        conn.close()
        return root.pipelines

    def write_pipeline(self, id, device_config, p4info):
        LOG.info("Writing P4Info to database...")
        conn = self.db.open()
        try:
            if id in self.pipelines:
                config = self.pipelines.get(id)
                transaction.begin()
                config.update_device_config(device_config)
                config.update_p4info(p4info)
                transaction.commit()
            else:
                transaction.begin()
                config = ForwardingPipelineConfig(device_config=device_config,
                                                  p4info=p4info)
                self.pipelines[id] = config
                transaction.commit()
        except Exception as e:
            transaction.abort()
            conn.close()
            raise e
        LOG.info("Writing P4Info to database succeeded.")
        LOG.debug("Pipelines: %s" % self.pipelines[id])

    def get_pipeline(self, id):
        LOG.info("Retrieving the P4 pipeline from database...")
        conn = self.db.open()
        try:
            if id in self.pipelines:
                return self.pipelines[id]
        except Exception as e:
            transaction.abort()
            conn.close()
            raise e
        LOG.info("Retrieving the P4 pipeline succeeded.")

    def get_device_config(self, id):
        LOG.info("Retrieving the device config from database...")
        pipeline = self.get_pipeline(id)
        device_config = pipeline.device_config
        LOG.info("Retrieving the device config succeeded.")
        LOG.debug("Device config:\n%s" % device_config)
        return device_config

    def get_p4info(self, id):
        LOG.info("Retrieving P4Info from database...")
        pipeline = self.get_pipeline(id)
        p4info = pipeline.p4info
        LOG.info("Retrieving P4Info succeeded.")
        LOG.debug("P4Info of the P4 pipeline[id=%s]:\n%s" % (id, p4info))
        return p4info