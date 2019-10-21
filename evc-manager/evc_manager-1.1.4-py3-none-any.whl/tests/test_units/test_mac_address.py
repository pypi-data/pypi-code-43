"""
    Test Mac_address entries
"""
import unittest
from libs.models.mac_address import MacAddress


class TestMacAddress(unittest.TestCase):
    """ Test MacAddress class """

    def setUp(self):
        """ set up procedure """
        self.mac = MacAddress()

    def test_incorrect_macs_01(self):
        """ Test multiple combination of incorrect
        mac addresses. No : or - """
        mac_addr = "0015F2204D6B"
        with self.assertRaises(ValueError):
            self.mac.mac_address = mac_addr

    def test_incorrect_macs_02(self):
        """ Test multiple combination of incorrect
        mac addresses. Letter over F and : """
        mac_addr = "00:13:AA:00:tr:01"
        with self.assertRaises(ValueError):
            self.mac.mac_address = mac_addr

    def test_incorrect_macs_03(self):
        """ Test multiple combination of incorrect
        mac addresses. Letter over F and - """
        mac_addr = "00-01-01-20-t5-55"
        with self.assertRaises(ValueError):
            self.mac.mac_address = mac_addr

    def test_incorrect_macs_04(self):
        """ Test multiple combination of incorrect
        mac addresses. Incorrect formation """
        mac_addr = "00-01-01-20abc-55"
        with self.assertRaises(ValueError):
            self.mac.mac_address = mac_addr

    def test_correct_macs(self):
        """ Test multiple combination of incorrect
        mac addresses """
        mac_list = ["00:01:01:20:bc:55",
                    "00-01-01-20-bc-55"]
        for mac in mac_list:
            self.mac.mac_address = mac


class TestMacAddressWithValue(unittest.TestCase):
    """ Test MacAddress class """

    def test_incorrect_macs(self):
        """ Test multiple combination of incorrect
        mac addresses. Incorrect formation """
        mac_addr = "00-01-01-20abc-55"
        with self.assertRaises(ValueError):
            self.mac = MacAddress(mac_addr)  # pylint: disable=W0201

    def test_correct_macs(self):
        """ Test multiple combination of incorrect
        mac addresses """
        macList = ["00:01:01:20:bc:55",
                   "00-01-01-20-bc-55"]
        for mac in macList:
            self.mac = MacAddress(mac)  # pylint: disable=W0201


if __name__ == '__main__':
    unittest.main()
