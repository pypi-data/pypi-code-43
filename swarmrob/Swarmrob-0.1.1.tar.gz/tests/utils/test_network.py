from unittest import TestCase
from swarmrob.utils import network
from swarmrob.utils import errors


class TestNetworkInfo(TestCase):
    def test_default_network_info(self):
        try:
            network.NetworkInfo()
        except errors.NetworkException:
            self.fail(msg="Unable to create default network info object")

    def test_local_network_info(self):
        try:
            network_info = network.NetworkInfo("lo")
            self.assertEqual(network_info.interface, "lo")
            self.assertEqual(network_info.ip_address, "127.0.0.1")
        except errors.NetworkException:
            self.fail(msg="Unable to create localhost network info object")

    def test_none(self):
        try:
            network_info = network.NetworkInfo(None)
            default_interface = network.get_default_interface()
            self.assertEqual(network_info.interface, default_interface)
            self.assertEqual(network_info.ip_address, network.get_ip_of_interface(default_interface))
        except errors.NetworkException:
            self.fail(msg="Unable to create default network info object")


class TestCheckNetworkBandwidth(TestCase):
    def test_none(self):
        try:
            network.check_network_bandwidth_of_repository(None)
            self.fail(msg="None has to throw a NetworkException")
        except errors.NetworkException:
            pass

    def test_non_existing_repository(self):
        try:
            network.check_network_bandwidth_of_repository("non_existing_repository")
            self.fail(msg="non_existing_repository has to throw a NetworkException")
        except errors.NetworkException:
            pass

    def test_existing_repository(self):
        try:
            results = network.check_network_bandwidth_of_repository("foo")
            self.assertIsNotNone(results)
        except errors.NetworkException:
            self.fail(msg="Unable to connect to an existing repository. Please check if the repository can be reached")


class TestGetIpOfInterface(TestCase):
    def test_non_existing_network(self):
        try:
            network.get_ip_of_interface("non_existing_network")
            self.fail(msg="get_ip_of_interface has to throw a NetworkException if the given network does not exist")
        except errors.NetworkException:
            pass

    def test_local_network(self):
        try:
            ip = network.get_ip_of_interface("lo")
            self.assertEqual(ip, "127.0.0.1", msg="lo network does not have the ip address 127.0.0.1")
        except errors.NetworkException:
            self.fail(msg="lo network does not exist")

    def test_docker_network(self):
        try:
            ip = network.get_ip_of_interface("docker0")
            self.assertIsNotNone(ip, msg="docker0 network has no ip address")
        except errors.NetworkException:
            self.fail(msg="docker0 network does not exist. Make sure docker is installed")

    def test_none(self):
        try:
            network.get_ip_of_interface(None)
            self.fail(msg="None has to throw a NetworkException")
        except errors.NetworkException:
            pass


class TestGetInterfaceList(TestCase):
    def test_get_interface_list(self):
        interface_list = network.get_interface_list()
        self.assertIsNotNone(interface_list)
        self.assertNotEqual(len(interface_list), 0)
        self.assertTrue("lo" in interface_list)


class TestGetDefaultInterface(TestCase):
    def test_get_default_interface(self):
        try:
            default = network.get_default_interface()
            self.assertIsNotNone(default)
            self.assertEqual(type(default), str)
        except errors.NetworkException:
            self.fail(msg="No default interface with an ip exists")


class TestGetInterfaceOfIp(TestCase):
    def test_success(self):
        try:
            interface = network.get_interface_of_ip("127.0.0.1")
            self.assertIsNotNone(interface)
            self.assertEqual(interface, "lo")
        except errors.NetworkException:
            self.fail(msg="No interface with ip address 127.0.0.1")

    def test_unknown_ip_address(self):
        try:
            network.get_interface_of_ip("8.8.8.8")
            self.fail("The ip address 8.8.8.8 should not have an interface assigned to it")
        except errors.NetworkException:
            pass

    def test_malformed_ip_address(self):
        try:
            network.get_interface_of_ip("THIS_IS_NOT_AN_IP_ADDRESS")
            self.fail("The ip address THIS_IS_NOT_AN_IP_ADDRESS should not have an interface assigned to it")
        except errors.NetworkException:
            pass

    def test_none_ip_address(self):
        try:
            network.get_interface_of_ip(None)
            self.fail("The ip address None should not have an interface assigned to it")
        except errors.NetworkException:
            pass
