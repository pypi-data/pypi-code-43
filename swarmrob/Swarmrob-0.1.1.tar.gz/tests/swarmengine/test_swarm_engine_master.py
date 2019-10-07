import socket
import jsonpickle
from unittest import TestCase
from unittest.mock import patch

from swarmrob.swarmengine import swarm_engine_master, swarm_engine, swarm, swarm_engine_worker
from swarmrob.utils import network
from swarmrob.utils.errors import NetworkException


class TestSwarmEngineMasterInit(TestCase):
    def setUp(self):
        self.master, _ = default_setup()

    def test_init(self):
        self.assertEqual("127.0.0.1", self.master.advertise_address)
        self.assertEqual(socket.gethostname(), self.master.hostname)
        self.assertEqual("lo", self.master.interface)
        self.assertIsNotNone(self.master.uuid)
        self.assertIsNone(self.master.swarm_uuid)
        self.assertIsNone(self.master._remote_logging_server)


class TestSwarmEngineMasterRegisterWorkerAtMaster(TestCase):
    def setUp(self):
        self.master, self.worker = default_setup()

    def test_register_worker_at_master(self):
        init_master(self.master)
        swarm_uuid_as_json = jsonpickle.encode("foo")
        worker_as_json = jsonpickle.encode(self.worker)
        self.assertIsNotNone(self.master.register_worker_at_master(swarm_uuid_as_json, worker_as_json))

    def test_register_worker_at_master_not_initialized(self):
        swarm_uuid_as_json = jsonpickle.encode("foo")
        worker_as_json = jsonpickle.encode(self.worker)
        try:
            self.master.register_worker_at_master(swarm_uuid_as_json, worker_as_json)
            self.fail(msg="Registering a worker when the master is not initialized should throw a RuntimeError")
        except RuntimeError:
            pass

    def test_register_worker_at_master_swarm_uuid_none(self):
        init_master(self.master)
        worker_as_json = jsonpickle.encode(self.worker)
        try:
            self.master.register_worker_at_master(None, worker_as_json)
            self.fail(msg="Registering a worker without swarm_uuid should throw a RuntimeError")
        except RuntimeError:
            pass

    def test_register_worker_at_master_worker_none(self):
        init_master(self.master)
        swarm_uuid_as_json = jsonpickle.encode("foo")
        try:
            self.master.register_worker_at_master(swarm_uuid_as_json, None)
            self.fail(msg="Registering a worker that is None should throw a RuntimeError")
        except RuntimeError:
            pass


class TestSwarmEngineMasterUnregisterWorkerAtMaster(TestCase):
    def setUp(self):
        self.master, self.worker = default_setup()

    def test_unregister_worker_at_master(self):
        init_master(self.master)
        swarm_uuid_as_json = jsonpickle.encode("foo")
        worker_as_json = jsonpickle.encode(self.worker)
        worker_uuid_as_json = jsonpickle.encode(self.worker.uuid)
        self.assertIsNotNone(self.master.register_worker_at_master(swarm_uuid_as_json, worker_as_json))
        self.assertTrue(self.master.unregister_worker_at_master(swarm_uuid_as_json, worker_uuid_as_json))

    def test_unregister_worker_at_master_worker_not_registered(self):
        init_master(self.master)
        swarm_uuid_as_json = jsonpickle.encode("foo")
        worker_uuid_as_json = jsonpickle.encode(self.worker.uuid)
        self.assertFalse(self.master.unregister_worker_at_master(swarm_uuid_as_json, worker_uuid_as_json))

    def test_unregister_worker_at_master_master_not_initialized(self):
        swarm_uuid_as_json = jsonpickle.encode("foo")
        worker_uuid_as_json = jsonpickle.encode(self.worker.uuid)
        try:
            self.assertFalse(self.master.unregister_worker_at_master(swarm_uuid_as_json, worker_uuid_as_json))
            self.fail(msg="Unregistering a worker on an uninitialized master should throw a RuntimeError")
        except RuntimeError:
            pass

    def test_unregister_worker_at_master_swarm_uuid_none(self):
        init_master(self.master)
        swarm_uuid_as_json = jsonpickle.encode("foo")
        worker_as_json = jsonpickle.encode(self.worker)
        worker_uuid_as_json = jsonpickle.encode(self.worker.uuid)
        self.assertIsNotNone(self.master.register_worker_at_master(swarm_uuid_as_json, worker_as_json))
        self.assertFalse(self.master.unregister_worker_at_master(None, worker_uuid_as_json))

    def test_unregister_worker_at_master_worker_none(self):
        init_master(self.master)
        swarm_uuid_as_json = jsonpickle.encode("foo")
        worker_as_json = jsonpickle.encode(self.worker)
        self.assertIsNotNone(self.master.register_worker_at_master(swarm_uuid_as_json, worker_as_json))
        self.assertFalse(self.master.unregister_worker_at_master(swarm_uuid_as_json, None))


class TestSwarmEngineMasterGetSwarmStatusAsJson(TestCase):
    def setUp(self):
        self.master, self.worker = default_setup()

    def test_get_swarm_status_as_json(self):
        init_master(self.master)
        s = jsonpickle.decode(self.master.get_swarm_status_as_json())
        self.assertEqual("foo", s.uuid)

    def test_get_swarm_status_as_json_master_not_initialized(self):
        self.assertIsNone(jsonpickle.decode(self.master.get_swarm_status_as_json()))


class LoggingServerDummy:
    def __init__(self, interface=None):
        network_info = network.NetworkInfo(interface)
        self.interface = network_info.interface
        self.hostname = 'dummy_hostname'
        self.port = '1234'

    def start(self):
        pass


@patch('swarmrob.logger.remote_logging_server.RemoteLoggingServer', LoggingServerDummy)
class TestSwarmEngineMasterStartRemoteLoggingServer(TestCase):
    def setUp(self):
        self.master, self.worker = default_setup()

    def test_start_remote_logging_server(self):
        self.master.start_remote_logging_server()

    def test_start_remote_logging_server_non_existent_interface(self):
        try:
            master = swarm_engine_master.Master("non_existent", "127.0.0.1")
            master.start_remote_logging_server()
            self.fail()
        except NetworkException:
            pass

    def test_start_remote_logging_server_default_interface_using_none(self):
        master = swarm_engine_master.Master(None, "127.0.0.1")
        master.start_remote_logging_server()


@patch('swarmrob.logger.remote_logging_server.RemoteLoggingServer', LoggingServerDummy)
class TestSwarmEngineMasterStartRemoteLoggingServer(TestCase):
    def setUp(self):
        self.master, self.worker = default_setup()

    def test_get_remote_logging_server_info(self):
        self.master.start_remote_logging_server()
        hostname, port = self.master.get_remote_logging_server_info()
        self.assertIsNotNone(hostname)
        self.assertIsNotNone(port)

    def test_get_remote_logging_server_info_remote_logger_not_started(self):
        hostname, port = self.master.get_remote_logging_server_info()
        self.assertIsNone(hostname)
        self.assertIsNone(port)


def init_master(master):
    swarm_engine.SwarmEngine().swarm = swarm.Swarm("foo", master)


def default_setup():
    swarm_engine.SwarmEngine().swarm = None
    swarm_engine.SwarmEngine()._remote_logging_server = None
    master = swarm_engine_master.Master("lo", "127.0.0.1")
    worker = swarm_engine_worker.Worker("foo", "lo", "bar")
    return master, worker
