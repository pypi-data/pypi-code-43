import unittest

from DKCloudCommand.modules.DKIgnore import DKIgnore


class TestDKIgnore(unittest.TestCase):

    def test_ignore(self):
        ignore = DKIgnore(None)

        test = 'not_ignore'
        self.assertFalse(ignore.ignore(test))

        test = '.DS_Store'
        self.assertTrue(ignore.ignore(test))

        test = 'base/path/directory/.DS_Store'
        self.assertTrue(ignore.ignore(test))

    def test_ignore_with_path(self):
        dummy_path = 'dummy/path/'
        ignore = DKIgnore(dummy_path)

        test = 'not_ignore'
        self.assertFalse(ignore.ignore(test))

        test = '.DS_Store'
        self.assertTrue(ignore.ignore(test))

        test = 'base/path/directory/.DS_Store'
        self.assertTrue(ignore.ignore(test))
