"""
    Test UNI entries
"""
import unittest
from libs.models.uni import UNI


class TestUniWithMacAddress(unittest.TestCase):
    """ Test UNI class. Variables are already tested by evaluate_str
     and evaluate_integer functions and testers. Testing with Mac_address
     because it is an inheritance """

    def setUp(self):
        """ set up procedure """
        self.uni = UNI()

    def test_correct_empty_mac_address_list(self):
        """ Test empty return """
        self.assertEqual(self.uni.mac_addresses, [])

    def test_incorrect_multiple_mac_addresses(self):
        """ Test with multiple mac addresses """
        mac_list = ["00:g1:01:20:bc:55"]
        with self.assertRaises(ValueError):
            self.uni.mac_addresses = mac_list

    def test_correct_multiple_mac_addresses(self):
        """ Test with multiple mac addresses """
        mac_list = ["00:01:01:20:bc:55", "00-01-01-20-bc-55"]
        self.uni.mac_addresses = mac_list

    def test_correct_addition_of_mac_addresses(self):
        """ Test with multiple mac addresses """
        mac_list = ["00:01:01:20:bc:55", "00-01-01-20-bc-55"]
        self.uni.mac_addresses = mac_list
        self.uni.add_mac_address("ff:ff:ff:ff:ff:ff")
        self.assertEqual(self.uni.mac_addresses[2].mac_address, "ff:ff:ff:ff:ff:ff")


if __name__ == '__main__':
    unittest.main()
