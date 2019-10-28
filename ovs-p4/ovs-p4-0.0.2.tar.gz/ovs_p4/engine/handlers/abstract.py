from abc import abstractmethod


class AbstractService(object):

    def __init__(self, ovs_driver, db_conn):
        self.ovs_driver = ovs_driver
        self.db_conn = db_conn

    @abstractmethod
    def handle(self):
        pass