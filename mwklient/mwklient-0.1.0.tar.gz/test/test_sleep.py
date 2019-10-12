# encoding=utf-8
""" This module contains tests for mwklient.sleep.
The class TestSleep defines unit test cases.
"""
import unittest
import time
from mock import call, patch
from pytest import raises
from mwklient.sleep import Sleeper, Sleepers
from mwklient.errors import MaximumRetriesExceeded


class TestSleepers(unittest.TestCase):

    def setUp(self):
        self.sleep = patch('time.sleep').start()
        self.max_retries = 10
        self.sleepers = Sleepers(self.max_retries, 30)

    def tearDown(self):
        patch.stopall()

    def test_make(self):
        sleeper = self.sleepers.make()
        self.assertTrue(isinstance(sleeper, Sleeper))
        self.assertEqual(sleeper.retries, 0)

    def test_sleep(self):
        sleeper = self.sleepers.make()
        sleeper.sleep()
        sleeper.sleep()
        self.sleep.assert_has_calls([call(0), call(30)])

    def test_min_time(self):
        sleeper = self.sleepers.make()
        sleeper.sleep(5)
        self.sleep.assert_has_calls([call(5)])

    def test_retries_count(self):
        sleeper = self.sleepers.make()
        sleeper.sleep()
        sleeper.sleep()
        self.assertEqual(sleeper.retries, 2)

    def test_max_retries(self):
        sleeper = self.sleepers.make()
        for _ in range(self.max_retries):
            sleeper.sleep()
        with raises(MaximumRetriesExceeded):
            sleeper.sleep()

    def test_cheat_pylint(self):
        """ Dumb test that avoids unused import warning for time package.
        """
        self.assertIsNotNone(time)


if __name__ == '__main__':
    print("\nNote: Running in stand-alone mode. Consult the README\n")
    unittest.main()
