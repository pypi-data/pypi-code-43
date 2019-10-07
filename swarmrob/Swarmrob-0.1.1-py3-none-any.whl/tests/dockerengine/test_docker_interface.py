import time
import docker.errors
from unittest import TestCase
from swarmrob.dockerengine import docker_interface
from swarmrob.logger import remote_logger
from swarmrob.services import service
from swarmrob.utils.errors import DockerException


class TestDockerInterfaceInit(TestCase):
    def test_init(self):
        interface = docker_interface.DockerInterface()
        self.assertIsNotNone(interface._docker_env)


class TestDockerInterfaceCheckVolumes(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_check_volumes_existing_volume(self):
        srv = service.Service()
        srv.add_volume("/tmp", "/tmp")
        volume_vector = self.interface.check_volumes(srv)
        self.assertEqual([1], volume_vector)

    def test_check_volumes_not_existing_volume(self):
        srv = service.Service()
        srv.add_volume("/non_existent", "/non_existent")
        volume_vector = self.interface.check_volumes(srv)
        self.assertEqual([0], volume_vector)

    def test_check_volumes_none(self):
        volume_vector = self.interface.check_volumes(None)
        self.assertEqual([], volume_vector)

    def test_check_volumes_empty(self):
        srv = service.Service()
        volume_vector = self.interface.check_volumes(srv)
        self.assertEqual([], volume_vector)

    def test_check_volumes_all_existing(self):
        srv = service.Service()
        srv.add_volume("/root", "/root")
        srv.add_volume("/tmp", "/tmp")
        srv.add_volume("/var", "/var")
        volume_vector = self.interface.check_volumes(srv)
        self.assertEqual([1, 1, 1], volume_vector)


class TestDockerInterfaceCheckDevices(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_check_devices_existing_device(self):
        srv = service.Service()
        srv.add_device("/dev", "/dev")
        device_vector = self.interface.check_devices(srv)
        self.assertEqual([1], device_vector)

    def test_check_devices_not_existing_device(self):
        srv = service.Service()
        srv.add_device("/dev/non_existent", "/dev/non_existent")
        volume_vector = self.interface.check_devices(srv)
        self.assertEqual([0], volume_vector)

    def test_check_devices_none(self):
        volume_vector = self.interface.check_devices(None)
        self.assertEqual([], volume_vector)

    def test_check_devices_empty(self):
        srv = service.Service()
        volume_vector = self.interface.check_devices(srv)
        self.assertEqual([], volume_vector)


class TestDockerInterfaceRunContainerInBackground(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_run_container_in_background(self):
        try:
            self.interface.init_docker_swarm("lo")
            logger = remote_logger.RemoteLogger(None, None, None, None)
            srv = service.Service("foo", "hello-world")
            self.interface.create_network("bar")
            time.sleep(1)
            self.assertIsNotNone(self.interface.run_container_in_background(srv, logger, "bar"))
        except DockerException:
            self.fail()

    def test_run_container_in_background_none_logger(self):
        try:
            self.interface.init_docker_swarm("lo")
            srv = service.Service("foo", "hello-world")
            self.interface.create_network("bar")
            time.sleep(1)
            self.assertIsNotNone(self.interface.run_container_in_background(srv, None, "bar"))
        except DockerException:
            self.fail()

    def test_run_container_in_background_none_network(self):
        try:
            self.interface.init_docker_swarm("lo")
            logger = remote_logger.RemoteLogger(None, None, None, None)
            srv = service.Service("foo", "hello-world")
            self.assertIsNotNone(self.interface.run_container_in_background(srv, logger, None))
        except DockerException:
            self.fail()

    def test_run_container_in_background_none_service(self):
        try:
            logger = remote_logger.RemoteLogger(None, None, None, None)
            self.interface.create_network("bar")
            time.sleep(1)
            self.interface.run_container_in_background(None, logger, "bar")
            self.fail()
        except DockerException:
            pass

    def test_run_container_in_background_empty_service_params(self):
        try:
            logger = remote_logger.RemoteLogger(None, None, None, None)
            srv = service.Service(None, None)
            self.interface.create_network("bar")
            time.sleep(1)
            self.interface.run_container_in_background(srv, logger, "bar")
            self.fail()
        except DockerException:
            pass


class TestDockerInterfaceInitSwarm(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_init_docker_swarm(self):
        try:
            self.interface.init_docker_swarm("lo")
            self.interface._docker_env.swarm.leave(force=True)
        except DockerException:
            self.fail()

    def test_init_docker_swarm_non_existent_interface(self):
        try:
            self.interface.init_docker_swarm("non_existent")
            self.fail()
        except DockerException:
            pass

    def test_init_docker_swarm_none_interface(self):
        try:
            self.interface.init_docker_swarm(None)
            self.fail()
        except DockerException:
            pass

# join_docker_swarm is not tested here because it needs two instances of swarmrob


class TestDockerInterfaceGetJoinToken(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_get_join_token(self):
        try:
            self.interface.init_docker_swarm("lo")
            self.assertIsNotNone(self.interface.get_join_token())
            self.interface._docker_env.swarm.leave(force=True)
        except DockerException:
            self.fail()

    def test_get_join_token_no_swarm_init(self):
        try:
            try:
                self.interface._docker_env.swarm.leave(force=True)
            except docker.errors.APIError:
                pass
            self.assertIsNotNone(self.interface.get_join_token())
            self.fail()
        except DockerException:
            pass


class TestDockerInterfaceCreateNetwork(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_create_network(self):
        try:
            self.interface.init_docker_swarm("lo")
            network = self.interface.create_network("bar")
            self.assertIsNotNone(network)
            self.assertEqual('swarm', network.attrs['Scope'])
            self.assertEqual('overlay', network.attrs['Driver'])
            self.assertTrue(network.attrs['Attachable'])
        except DockerException:
            self.fail()

    def test_create_network_already_existing(self):
        try:
            self.interface.init_docker_swarm("lo")
            self.assertIsNotNone(self.interface.create_network("bar"))
            network = self.interface.create_network("bar")
            self.assertIsNotNone(network)
            self.assertEqual('swarm', network.attrs['Scope'])
            self.assertEqual('overlay', network.attrs['Driver'])
            self.assertTrue(network.attrs['Attachable'])
        except DockerException:
            self.fail()

    def test_create_network_empty_name(self):
        try:
            self.interface.create_network('')
            self.fail("A network with empty name should not be creatable")
        except DockerException:
            pass

    def test_create_network_none_name(self):
        try:
            self.interface.create_network('')
            self.fail("None should not be a creatable network")
        except DockerException:
            pass


class TestDockerInterfaceHasNetworkWithName(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_has_network_with_name(self):
        self.interface.create_network("foo")
        time.sleep(1)
        self.assertTrue(self.interface.has_network_with_name("foo"))

    def test_has_network_with_name_non_existent(self):
        self.assertFalse(self.interface.has_network_with_name("non_existent"))

    def test_has_network_with_name_none(self):
        self.assertFalse(self.interface.has_network_with_name(None))


class TestDockerInterfaceGetNetworkByName(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_get_network_by_name(self):
        try:
            self.interface.init_docker_swarm("lo")
            self.interface.create_network("foo")
            time.sleep(1)
            self.assertIsNotNone(self.interface.get_network_by_name("foo"))
        except DockerException:
            self.fail(msg="Unable to get network")

    def test_get_network_by_name_non_existent(self):
        try:
            self.interface.get_network_by_name("non_existent")
            self.fail(msg="Requesting a not existing network should throw a DockerException")
        except DockerException:
            pass

    def test_get_network_by_name_none(self):
        try:
            self.interface.get_network_by_name(None)
            self.fail(msg="Requesting a not existing network should throw a DockerException")
        except DockerException:
            pass


class TestDockerInterfaceIsImageAvailable(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_is_image_available(self):
        self.assertTrue(self.interface.is_image_available("hello-world"))

    def test_is_image_available_non_existent(self):
        self.assertFalse(self.interface.is_image_available("non_existent"))

    def test_is_image_available_none(self):
        self.assertFalse(self.interface.is_image_available(None))


class TestDockerInterfaceGetImageSize(TestCase):
    def setUp(self):
        self.interface = default_setup()

    def test_get_image_size(self):
        self.assertTrue(0 <= self.interface.get_image_size("hello-world"))

    def test_get_image_size_non_existent(self):
        self.assertEqual(-1, self.interface.get_image_size("non_existent"))

    def test_get_image_size_none(self):
        self.assertEqual(-1, self.interface.get_image_size(None))


def default_setup():
    interface = docker_interface.DockerInterface()
    interface._pull_image("hello-world")
    return interface
