"""
    Test Tag entries
"""
import unittest
from libs.models.tag import Tag


class TestTagType(unittest.TestCase):
    """ Test all combinations for tag.type
        Tag type has to be 'mpls' or 'vlan'"""

    def setUp(self):
        """ SetUp procedure """
        self.tag = Tag()

    def test_incorrect_type_empty(self):
        """ Test empty type """
        with self.assertRaises(ValueError):
            self.tag.type = ""

    def test_incorrect_type_none(self):
        """ Test None type"""
        with self.assertRaises(ValueError):
            self.tag.type = None

    def test_incorrect_type_other(self):
        """ Test VLAN code instead of name """
        with self.assertRaises(ValueError):
            self.tag.type = '8021q'

    def test_correct_type_vlan(self):
        """ Test with capital letters"""
        self.tag.type = 'VLAN'

    def test_read_correct_type_vlan(self):
        """ Test to see if capital VLAN was lowered to vlan """
        self.test_correct_type_vlan()
        self.assertEqual(self.tag.type, 'vlan')

    def test_correct_type_mpls(self):
        """ Test Mpls type with capital M """
        self.tag.type = 'Mpls'

    def test_read_correct_type_mpls(self):
        """ Test to see if Mpls turned into mpls """
        self.test_correct_type_mpls()
        self.assertEqual(self.tag.type, 'mpls')


class TestTagValueVlan(unittest.TestCase):
    """ Test all combinations for tag.value
        VLAN IDs must be integer and be -1 or between 1 and 4095"""

    def setUp(self):
        """ SetUp procedure """
        self.tag = Tag()
        self.tag.type = 'vlan'

    def test_incorrect_type_vlan_value_empty(self):
        """ Test empty VLAN value """
        with self.assertRaises(ValueError):
            self.tag.value = ""

    def test_incorrect_type_vlan_value_none(self):
        """ Test None VLAN value """
        with self.assertRaises(ValueError):
            self.tag.value = None

    def test_incorrect_type_vlan_value_wrong_string(self):
        """ Test VLAN value with a string """
        with self.assertRaises(ValueError):
            self.tag.value = 'a'

    def test_incorrect_type_vlan_value_negative(self):
        """ Test VLAN value with negative value """
        with self.assertRaises(ValueError):
            self.tag.value = -2

    def test_incorrect_type_vlan_value_zero(self):
        """ Test VLAN value with 0 """
        with self.assertRaises(ValueError):
            self.tag.value = 0

    def test_incorrect_type_vlan_greater_than_4095(self):
        """ Test VLAN value outside of the scope """
        with self.assertRaises(ValueError):
            self.tag.value = 4096

    def test_correct_type_vlan_value(self):
        """ Test correct VLAN value """
        self.tag.value = 2

    def test_read_correct_type_vlan(self):
        """ Test correct VLAN value """
        self.test_correct_type_vlan_value()
        self.assertEqual(self.tag.value, 2)


class TestTagValueMPLS(unittest.TestCase):
    """ Test all combinations for tag.value
        MPLS labels must be integer and between 1-1048576 """

    def setUp(self):
        """ SetUp procedure """
        self.tag = Tag()
        self.tag.type = 'mpls'

    def test_incorrect_type_mpls_value_empty(self):
        """ Test empty MPLS value """
        with self.assertRaises(ValueError):
            self.tag.value = ""

    def test_incorrect_type_mpls_value_none(self):
        """ Test None MPLS value """
        with self.assertRaises(ValueError):
            self.tag.value = None

    def test_incorrect_type_mpls_value_wrong_string(self):
        """ Test MPLS value with a string """
        with self.assertRaises(ValueError):
            self.tag.value = 'a'

    def test_incorrect_type_mpls_value_negative(self):
        """ Test MPLS value with negative value """
        with self.assertRaises(ValueError):
            self.tag.value = -1

    def test_incorrect_type_mpls_value_zero(self):
        """ Test MPLS value with 0 """
        with self.assertRaises(ValueError):
            self.tag.value = 0

    def test_incorrect_type_mpls_greater_than_1048576(self):
        """ Test MPLS value outside of the scope """
        with self.assertRaises(ValueError):
            self.tag.value = 1048577

    def test_correct_type_mpls_value_two(self):
        """ Test correct MPLS value """
        self.tag.value = 2

    def test_read_correct_type_mpls(self):
        """ Test correct MPLS value """
        self.test_correct_type_mpls_value_two()
        self.assertEqual(self.tag.value, 2)


if __name__ == '__main__':
    unittest.main()
