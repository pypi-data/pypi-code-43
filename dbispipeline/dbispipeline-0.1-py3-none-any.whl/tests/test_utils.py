# noqa: D100
import os
import unittest

from dbispipeline import store, utils


class TestUtils(unittest.TestCase):
    """Tests the utils of the dbispipeline."""

    def test_prefix_path(self):
        """Tests the prefix path function."""
        store['path_prefix'] = None
        default_prefix = '/a'
        path = '/test/test.txt'

        self.assertEqual(
            utils.prefix_path(path, default_prefix),
            os.path.join(default_prefix, path))

        with self.assertRaises(ValueError):
            utils.prefix_path(path)

        store['path_prefix'] = '/b'
        self.assertEqual(
            utils.prefix_path(path, default_prefix), os.path.join('/b', path))
