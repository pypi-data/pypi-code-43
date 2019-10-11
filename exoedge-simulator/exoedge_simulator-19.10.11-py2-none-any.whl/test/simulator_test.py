# pylint: disable=C0325
import os
import sys
import time
import unittest
from murano_client.client import MuranoClient
from exoedge.config_io import ConfigIO
from exoedge.config_applications import ConfigApplications
from exoedge.data_in import DataIn
from exoedge.configs import ConfigWatcher
from exoedge import logger
from six.moves import queue

test_dir = os.path.dirname(os.path.abspath(__file__))


class SimulatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for lgr in logger.getExoEdgeLoggers():
            lgr.setLevel(10)
    @classmethod
    def tearDownClass(cls):
        pass
    def setUp(self):
        test_case_timeout = 5.0
        test_name = self.id().split('.')[-1]
        print("setting up for test: {}".format(test_name))

        self.test_q = queue.Queue()
        def tell_function_override(data):
            """ utilize the tell_function_override feature in murano_client """
            print("tell_function_override called with: {}".format(data))
            self.test_q.put(data)

        self.client = MuranoClient(
            murano_host='https://dne.m2.exosite.io/',
            watchlist=['config_io'],
            tell_function_override=tell_function_override,
            murano_id=test_name
        )
        self.client.start_client()

        self.config_io = ConfigIO(
            device=self.client,
            config_io_file=os.path.join(test_dir, 'assets', test_name+'.json'),
            debug='DEBUG'
        )
        self.config_applications = ConfigApplications(
            device=self.client,
            restart_channels_event=self.config_io.event_new_config,
            config_applications_file=os.path.join(
                test_dir, test_name+'config_applications.json'
            )
        )
        self.watcher = ConfigWatcher(
            device=self.client,
            config_mgr_list=[
                self.config_io,
                self.config_applications,
                DataIn(
                    config_io=self.config_io,
                    device=self.client,
                )
            ]
        )
        self.watcher.start()

        start = time.time()
        while self.test_q.qsize() < 1:
            if time.time()-start >= test_case_timeout:
                break
            time.sleep(0.1)
        # pop config_io object
        print("popping config_io object from self.test_q: {}".format(self.test_q.get()))

    def tearDown(self):
        self.watcher.stop()
        self.client.stop_all()

