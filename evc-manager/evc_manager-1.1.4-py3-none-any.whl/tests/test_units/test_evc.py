"""
    Test tracing.trace_entries
"""
import copy
import unittest
from libs.models.evc import EthernetVirtualCircuit
from libs.models.mac_address import MacAddress
from libs.models.uni import UNI
from tests.test_integration.content_files.oess_outputs import OESS_REPLY
from tests.test_integration.content_files.oess_outputs import OESS_REPL2


class TestName(unittest.TestCase):
    """ Test all combinations for evc.name """

    def setUp(self):
        self.evc = EthernetVirtualCircuit()

    def test_incorrect_name_empty(self):
        """ Name cannot be empty"""
        with self.assertRaises(ValueError):
            self.evc.name = ""

    def test_incorrect_name_none(self):
        """ Name cannot be empty"""
        with self.assertRaises(ValueError):
            self.evc.name = None

    def test_correct_name(self):
        """ Correct name"""
        self.evc.name = 1


class TestProvisioningTime(unittest.TestCase):
    """ Test all combinations for evc.provisioning_time """

    def setUp(self):
        self.evc = EthernetVirtualCircuit()

    def test_incorrect_provisioning_time_negative(self):
        """ provisioning_time cannot be negative """
        with self.assertRaises(ValueError):
            self.evc.provisioning_time = -1

    def test_incorrect_provisioning_time_none(self):
        """ provisioning_time cannot be None """
        with self.assertRaises(ValueError):
            self.evc.provisioning_time = None

    def test_incorrect_provisioning_time_empty(self):
        """ provisioning_time cannot be empty """
        with self.assertRaises(ValueError):
            self.evc.provisioning_time = ""

    def test_incorrect_provisioning_time_string(self):
        """ provisioning_time cannot be None """
        with self.assertRaises(ValueError):
            self.evc.provisioning_time = 'a'

    def test_correct_provisioning_time_int(self):
        """ provisioning_time is integer """
        self.evc.provisioning_time = 221211133

    def test_correct_provisioning_time_string(self):
        """ provisioning_time is integer-compatible """
        self.evc.provisioning_time = '221211133'


class TestDecommissioningTime(unittest.TestCase):
    """ Test all combinations for evc.decommissioning_time """

    def setUp(self):
        self.evc = EthernetVirtualCircuit()

    def test_incorrect_decommissioning_time_negative(self):
        """ decommissioning_time cannot be negative """
        with self.assertRaises(ValueError):
            self.evc.decommissioning_time = -1

    def test_incorrect_decommissioning_time_none(self):
        """ decommissioning_time cannot be None """
        with self.assertRaises(ValueError):
            self.evc.decommissioning_time = None

    def test_incorrect_decommissioning_time_empty(self):
        """ decommissioning_time cannot be empty """
        with self.assertRaises(ValueError):
            self.evc.decommissioning_time = ""

    def test_incorrect_decommissioning_time_string(self):
        """ decommissioning_time cannot be None """
        with self.assertRaises(ValueError):
            self.evc.decommissioning_time = 'a'

    def test_correct_decommissioning_time_int(self):
        """ decommissioning_time is integer """
        self.evc.decommissioning_time = 221211133

    def test_correct_decommissioning_time_string(self):
        """ decommissioning_time is integer-compatible """
        self.evc.decommissioning_time = '221211133'


class TestTenant(unittest.TestCase):
    """ Test all combinations for evc.tenant. Tenant is a string """

    def setUp(self):
        self.evc = EthernetVirtualCircuit()

    def test_incorrect_tenant_empty(self):
        """ tenant cannot be empty"""
        with self.assertRaises(ValueError):
            self.evc.tenant = ""

    def test_incorrect_tenant_none(self):
        """ tenant cannot be empty"""
        with self.assertRaises(ValueError):
            self.evc.tenant = None

    def test_correct_tenant(self):
        """ Correct tenant"""
        self.evc.tenant = 1


class TestPriority(unittest.TestCase):
    """ Test all combinations for evc.priority.
    Priority must be an integer """

    def setUp(self):
        self.evc = EthernetVirtualCircuit()

    def test_incorrect_priority_negative(self):
        """ priority cannot be negative """
        with self.assertRaises(ValueError):
            self.evc.priority = -1

    def test_incorrect_priority_none(self):
        """ priority cannot be None """
        with self.assertRaises(ValueError):
            self.evc.priority = None

    def test_incorrect_priority_empty(self):
        """ priority cannot be empty """
        with self.assertRaises(ValueError):
            self.evc.priority = ""

    def test_incorrect_priority_string(self):
        """ priority cannot be None """
        with self.assertRaises(ValueError):
            self.evc.priority = 'a'

    def test_correct_priority_int(self):
        """ priority is integer """
        self.evc.priority = 221211133

    def test_correct_priority_string(self):
        """ priority is integer-compatible """
        self.evc.priority = '221211133'


class TestExternalId(unittest.TestCase):
    """ Test all combinations for evc.external_id. external_id is a string """

    def setUp(self):
        self.evc = EthernetVirtualCircuit()

    def test_incorrect_external_id_empty(self):
        """ external_id cannot be empty"""
        with self.assertRaises(ValueError):
            self.evc.external_id = ""

    def test_incorrect_external_id_none(self):
        """ external_id cannot be empty"""
        with self.assertRaises(ValueError):
            self.evc.external_id = None

    def test_correct_external_id(self):
        """ Correct external_id"""
        self.evc.external_id = 1


class TestCompareMethod(unittest.TestCase):
    """ Test if Compare method works for name and unis. The concept
    behind is: if two EVCs share the same NAME or the SAME UNIs, they
    are considered the same """

    def setUp(self):
        self.evc_a = EthernetVirtualCircuit()
        self.evc_b = EthernetVirtualCircuit()
        self.evc_a.name = 'EVC_A'
        self.evc_b.name = 'EVC_B'

    def test_equal_no_unis(self):
        """ Test if two EVCs are equal using __eq__ special method
        As UNIs are empty, they are 'equal' """
        self.assertEqual(self.evc_a, self.evc_b)

    def test_equal_with_unis(self):
        """ Test if two EVCs are equal using __eq__ special method """

        def create_uni(endpoints):
            unis = list()
            for endpoint in endpoints:
                uni = UNI()
                uni.device = endpoint['node']
                uni.interface_name = endpoint['interface']
                uni.interface_description = endpoint['interface_description']
                uni.tag.type = 'vlan'
                uni.tag.value = endpoint['tag']
                for mac_addr in endpoint['mac_addrs']:
                    uni.mac_addresses.append(MacAddress(mac_addr['mac_address']))
                unis.append(copy.deepcopy(uni))
                del uni
            return unis

        self.evc_a.unis = create_uni(OESS_REPLY['endpoints'])
        self.evc_b.unis = create_uni(OESS_REPLY['endpoints'])
        self.assertEqual(self.evc_a, self.evc_b)

    def test_error_equal_with_different_unis(self):
        """ Test if two EVCs are equal using __eq__ special method """

        def create_uni(endpoints):
            unis = list()
            for endpoint in endpoints:
                uni = UNI()
                uni.device = endpoint['node']
                uni.interface_name = endpoint['interface']
                uni.interface_description = endpoint['interface_description']
                uni.tag.type = 'vlan'
                uni.tag.value = endpoint['tag']
                for mac_addr in endpoint['mac_addrs']:
                    uni.mac_addresses.append(MacAddress(mac_addr['mac_address']))
                unis.append(copy.deepcopy(uni))
                del uni
            return unis

        self.evc_a.unis = create_uni(OESS_REPLY['endpoints'])
        self.evc_b.unis = create_uni(OESS_REPL2['endpoints'])
        self.assertNotEqual(self.evc_a, self.evc_b)


if __name__ == '__main__':
    unittest.main()
