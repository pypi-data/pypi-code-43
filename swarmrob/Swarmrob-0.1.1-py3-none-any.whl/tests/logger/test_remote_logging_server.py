from unittest import TestCase

from swarmrob.logger import remote_logging_server
from swarmrob.utils.errors import NetworkException


class TestRemoteLoggingServerInit(TestCase):
    def test_remote_logging_server_init(self):
        logging_server = remote_logging_server.RemoteLoggingServer("lo")
        self.assertEqual("lo", logging_server.interface)
        self.assertIsNotNone(logging_server.tcp_server)
        self.assertIsNotNone(logging_server.hostname)
        self.assertIsNotNone(logging_server.port)
        logging_server.tcp_server.server_close()

    def test_remote_logging_server_none_interface(self):
        try:
            logging_server = remote_logging_server.RemoteLoggingServer(None)
            logging_server.tcp_server.server_close()
        except NetworkException:
            self.fail("Given None as interface means the default interface should be used")

    def test_remote_logging_server_non_existent_interface(self):
        try:
            remote_logging_server.RemoteLoggingServer("non_existent")
            self.fail("Not being able to initialize the remote logging server should throw a NetworkException")
        except NetworkException:
            pass
