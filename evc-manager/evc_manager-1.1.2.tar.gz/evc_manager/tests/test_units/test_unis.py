"""
    Test UNIs entries
"""


import copy
import unittest
from libs.models.unis import UNIS
from libs.models.uni import UNI


def create_uni(num_endpoints):
    """ Creates a list of UNIs"""
    unis = list()
    i = 1
    while i < num_endpoints + 1:
        uni = UNI()
        uni.device = 'a_%s' % i
        uni.interface_name = 'a_int_%s' % i
        uni.tag.type = 'vlan'
        uni.tag.value = i
        unis.append(copy.deepcopy(uni))
        del uni
        i += 1
    return unis


class TestUnis(unittest.TestCase):
    """ Test UNIs class. """

    def setUp(self):
        """ set up procedure """
        self.unis = UNIS()

    def test_incorrect_unis_none(self):
        """ test inputs UNIs not being a list """
        list_unis = None
        with self.assertRaises(ValueError):
            self.unis.unis = list_unis

    def test_incorrect_unis_dict(self):
        """ test inputs UNIs not being a list """
        list_unis = dict()
        with self.assertRaises(ValueError):
            self.unis.unis = list_unis

    def test_incorrect_unis_empty_list(self):
        """ test inputs UNIs not being a list """
        list_unis = list()
        with self.assertRaises(ValueError):
            self.unis.unis = list_unis

    def test_correct_unis(self):
        """ test inputs UNIs not being a list """
        list_unis = create_uni(num_endpoints=3)
        self.unis.unis = list_unis


if __name__ == '__main__':
    unittest.main()
