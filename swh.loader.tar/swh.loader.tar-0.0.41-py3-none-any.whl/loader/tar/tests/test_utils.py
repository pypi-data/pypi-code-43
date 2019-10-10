# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import random
import unittest

from swh.loader.tar import utils


class UtilsLib(unittest.TestCase):

    def assert_ok(self, actual_data, expected_data):
        """Check that actual_data and expected_data matched.

        Actual data is a random block of data.  We want to check its
        contents match exactly but not the order within.

        """
        out = []
        random.shuffle(expected_data)
        for d in actual_data:
            self.assertIn(d, expected_data)
            out.append(d)
        self.assertEqual(len(out), len(expected_data))

    def test_random_block(self):
        _input = list(range(0, 9))
        # given
        actual_data = utils.random_blocks(_input, 2)
        self.assert_ok(actual_data, expected_data=_input)

    def test_random_block2(self):
        _input = list(range(9, 0, -1))
        # given
        actual_data = utils.random_blocks(_input, 4)
        self.assert_ok(actual_data, expected_data=_input)

    def test_random_block_with_fillvalue(self):
        _input = [(i, i+1) for i in range(0, 9)]
        actual_data = utils.random_blocks(_input, 2)
        self.assert_ok(actual_data, expected_data=_input)
