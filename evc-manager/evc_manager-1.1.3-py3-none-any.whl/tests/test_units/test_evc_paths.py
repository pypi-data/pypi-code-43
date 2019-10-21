"""
    Test Requested_path
"""


import unittest
from libs.models.nni import NNI
from libs.models.evc_paths import EvcPath
from tests.test_integration.content_files.oess_outputs import OESS_REPL2


class TestRequestedPath(unittest.TestCase):
    """ Test all combinations for tag.type
        Tag type has to be 'mpls' or 'vlan'"""

    def setUp(self):
        """ SetUp procedure """
        self.requested_path = EvcPath()
        self.list_nnis = list()
        self.non_nnis = list()
        self.non_nnis.append(OESS_REPL2['links'])
        self.non_nnis.append(OESS_REPL2['backup_links'])

        my_list = list()
        for links in ['links', 'backup_links']:
            for span in OESS_REPL2[links]:
                link = NNI()
                link.device_a = span['node_a']
                link.interface_a = span['interface_a']
                link.device_z = span['node_z']
                link.interface_z = span['interface_z']
                link.name = span['name']
                my_list.append(link)
                del link
            self.list_nnis.append(my_list[:])
            my_list.clear()

    def test_InsertWrongPathsNonList(self):
        """ Insert None """
        with self.assertRaises(ValueError):
            self.requested_path.paths = None

    def test_InsertWrongPathsZero(self):
        """ Insert int(0) """
        with self.assertRaises(ValueError):
            self.requested_path.paths = 0

    def test_InsertWrongPathsString(self):
        """ Insert String """
        with self.assertRaises(ValueError):
            self.requested_path.paths = 'a'

    def test_InsertWrongPathsEmptyList(self):
        """ Insert Empty List """
        with self.assertRaises(ValueError):
            self.requested_path.paths = []

    def test_InsertWrongPathsEmptyListofListsNonEmpty(self):
        """ Insert Empty List """
        with self.assertRaises(ValueError):
            self.requested_path.paths = [['a', 'c'], ['b', 'd']]

    def test_InsertWrongPathsEmptyListofListsWithDicts(self):
        """ Insert Empty List """
        with self.assertRaises((ValueError, KeyError, TypeError)):
            self.requested_path.paths = [[{}, {}], [{}, {}]]

    def test_InsertCorrectPathsAtInstantiation(self):
        """ Insert Correct path already in NNI format"""
        requested_path = EvcPath(self.non_nnis)
        self.assertIsInstance(requested_path.paths, list)

    def test_InsertCorrectPathsLists(self):
        """ Insert Correct path already in NNI format"""
        self.requested_path.paths = self.non_nnis
        self.assertIsInstance(self.requested_path.paths, list)

    def test_InsertCorrectPathsNNIs(self):
        """ Insert Correct path already in NNI format"""
        self.requested_path.paths = self.list_nnis
        self.assertIsInstance(self.requested_path.paths, list)

    def test_IterateThroughItemsLists(self):
        """ Iterate through items with source being a list of lists"""
        self.requested_path.paths = self.non_nnis
        for paths in iter(self.requested_path):
            for path in paths:
                self.assertIsInstance(path, NNI)

    def test_IterateThroughItemsNNIs(self):
        """ Iterate through items with source being a list of NNIs"""
        self.requested_path.paths = self.list_nnis
        for paths in iter(self.requested_path):
            for path in paths:
                self.assertIsInstance(path, NNI)

    def test_InsertCorrectEmptyPath(self):
        """ Insert Empty List """
        self.requested_path.paths = [[]]


if __name__ == '__main__':
    unittest.main()
