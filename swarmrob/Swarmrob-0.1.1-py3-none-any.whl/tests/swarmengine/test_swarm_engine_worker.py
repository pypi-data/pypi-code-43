import socket
import jsonpickle
from unittest import TestCase
from unittest.mock import patch

from swarmrob.swarmengine import swarm_engine_worker
from swarmrob.services import service
from swarmrob.utils.errors import DockerException


class TestSwarmEngineWorkerInit(TestCase):
    def test_init(self):
        worker = swarm_engine_worker.Worker("foo", "lo")
        self.assertEqual("127.0.0.1", worker.advertise_address)
        self.assertEqual("lo", worker.interface)
        self.assertEqual(socket.gethostname(), worker.hostname)
        self.assertIsNotNone(worker.uuid)
        self.assertEqual("foo", worker.swarm_uuid)
        self.assertIsNone(worker._remote_logger)
        self.assertIsNotNone(worker._container_list)

    def test_init_with_worker_uuid(self):
        worker = swarm_engine_worker.Worker("foo", "lo", "bar")
        self.assertEqual("bar", worker.uuid)


class TestSwarmEngineWorkerStartRemoteLogger(TestCase):
    def setUp(self):
        self.worker = default_setup()

    def test_start_remote_logger(self):
        self.assertTrue(self.worker.start_remote_logger("lo", 0))
        self.assertIsNotNone(self.worker._remote_logger)

    def test_start_remote_logger_hostname_none(self):
        self.assertFalse(self.worker.start_remote_logger(None, 0))
        self.assertIsNone(self.worker._remote_logger)

    def test_start_remote_logger_port_none(self):
        self.assertFalse(self.worker.start_remote_logger("lo", None))
        self.assertIsNone(self.worker._remote_logger)


class DockerInterfaceDummy:
    class Container:
        def __init__(self, status='running'):
            self.status = status

        def reload(self):
            pass

        def kill(self):
            self.status = 'exited'

    def __init__(self):
        self.run = False
        self.join = False

    def run_container_in_background(self, service_definition, remote_logger, network):
        if service_definition is None or remote_logger is None or network is None:
            raise DockerException()
        self.run = True
        return DockerInterfaceDummy.Container()

    def join_docker_swarm(self, master_address, interface, join_token):
        if master_address is None or interface is None or join_token is None:
            raise DockerException()
        self.join = True


@patch('swarmrob.dockerengine.docker_interface.DockerInterface', DockerInterfaceDummy)
class TestSwarmEngineWorkerStartService(TestCase):
    def setUp(self):
        self.worker = default_setup()
        self.service = service.Service("foo", "bar")

    def test_start_service(self):
        self.worker.start_remote_logger("lo", 0)
        self.assertTrue(self.worker.start_service(jsonpickle.encode(self.service), 'foo_network'))
        self.assertEqual(1, len(self.worker._container_list))

    def test_start_service_remote_logger_not_started(self):
        self.assertFalse(self.worker.start_service(jsonpickle.encode(self.service), 'foo_network'))

    def test_start_service_service_none(self):
        self.worker.start_remote_logger("lo", 0)
        self.assertFalse(self.worker.start_service(None, 'foo_network'))

    def test_start_service_network_none(self):
        self.worker.start_remote_logger("lo", 0)
        self.assertFalse(self.worker.start_service(jsonpickle.encode(self.service), None))


@patch('swarmrob.dockerengine.docker_interface.DockerInterface', DockerInterfaceDummy)
class TestSwarmEngineWorkerJoinDockerSwarm(TestCase):
    def setUp(self):
        self.worker = default_setup()

    def test_join_docker_swarm(self):
        try:
            self.worker.join_docker_swarm("127.0.0.1", "join_token")
        except RuntimeError:
            self.fail()

    def test_join_docker_swarm_master_address_none(self):
        try:
            self.worker.join_docker_swarm(None, "join_token")
            self.fail(msg="Errors should throw a RuntimeError")
        except RuntimeError:
            pass

    def test_join_docker_swarm_join_token_none(self):
        try:
            self.worker.join_docker_swarm("127.0.0.1", None)
            self.fail(msg="Errors should throw a RuntimeError")
        except RuntimeError:
            pass


@patch('swarmrob.dockerengine.docker_interface.DockerInterface', DockerInterfaceDummy)
class TestSwarmEngineWorkerStopAllServices(TestCase):
    def setUp(self):
        self.worker = default_setup()

    def test_stop_all_services(self):
        self.assertEqual(0, self.worker.stop_all_services())

    def test_stop_all_services_two_added(self):
        self.worker.start_remote_logger("lo", 0)
        service1 = service.Service("foo1", "bar")
        service2 = service.Service("foo2", "bar")
        self.worker.start_service(jsonpickle.encode(service1), 'foo_network')
        self.worker.start_service(jsonpickle.encode(service2), 'foo_network')
        self.assertEqual(2, self.worker.stop_all_services())


class TestSwarmEngineWorkerCheckHardware(TestCase):
    def setUp(self):
        self.worker = default_setup()

    def test_check_hardware(self):
        srv = service.Service()
        srv.add_volume("/var", "/var")
        srv.add_device("/dev", "/dev")
        self.assertEqual(1, self.worker.check_hardware(jsonpickle.encode(srv)))

    def test_check_hardware_non_existent(self):
        srv = service.Service()
        srv.add_volume("/non_existent", "/non_existent")
        srv.add_device("/non_existent", "/non_existent")
        self.assertEqual(0, self.worker.check_hardware(jsonpickle.encode(srv)))

    def test_check_hardware_service_definition_empty(self):
        self.assertEqual(1, self.worker.check_hardware(jsonpickle.encode(service.Service())))

    def test_check_hardware_service_definition_none(self):
        self.assertEqual(1, self.worker.check_hardware(None))


class TestGetUsage(TestCase):
    def setUp(self):
        self.worker = default_setup()

    def test_get_cpu_usage(self):
        self.assertTrue(0 <= self.worker.get_cpu_usage())

    def test_get_vram_usage(self):
        self.assertTrue(0 <= self.worker.get_vram_usage())

    def test_get_swap_ram_usage(self):
        self.assertTrue(0 <= self.worker.get_swap_ram_usage())

    def test_get_bandwidth(self):
        self.assertTrue(0 <= self.worker.get_bandwidth("repository"))


class TestGetRemainingImageDownloadSize(TestCase):
    def setUp(self):
        self.worker = default_setup()

    def test_get_remaining_image_download_size(self):
        self.assertTrue(0 <= self.worker.get_remaining_image_download_size("image_tag"))


class TestGetInfoAsJson(TestCase):
    def setUp(self):
        self.worker = default_setup()

    def test_get_info_as_json(self):
        self.assertIsNotNone(self.worker.get_info_as_json())


class TestInfoClasses(TestCase):

    def test_worker_info(self):
        worker_info = swarm_engine_worker.WorkerInfo("foo", "bar", "127.0.0.1", "baz")
        self.assertEqual("foo", worker_info.uuid)
        self.assertEqual("bar", worker_info.hostname)
        self.assertEqual("127.0.0.1", worker_info.advertise_address)
        self.assertEqual("baz", worker_info.swarm_uuid)
        self.assertEqual([], worker_info.services)

    def test_service_info(self):
        service_info = swarm_engine_worker.ServiceInfo("foo", "image", "bar", "running")
        self.assertEqual("foo", service_info.id)
        self.assertEqual("image", service_info.image)
        self.assertEqual("bar", service_info.name)
        self.assertEqual("running", service_info.status)


def default_setup():
    return swarm_engine_worker.Worker("foo", "lo")
