""" Test module for CurrentConfig Class """

import unittest
from .libs.models.current_config import  CurrentConfig


class TestCurrentConfigIsActive(unittest.TestCase):
    """ Test all combinations for is_active """

    def setUp(self):
        self.curr_config = CurrentConfig()

    def test_incorrect_is_active_empty(self):
        """ is_active cannot be empty """
        with self.assertRaises(ValueError):
            self.curr_config.is_active = ""

    def test_incorrect_is_active_none(self):
        """ is_active cannot be None """
        with self.assertRaises(ValueError):
            self.curr_config.is_active = None

    def test_incorrect_is_active_one(self):
        """ is_active cannot be integer """
        with self.assertRaises(ValueError):
            self.curr_config.is_active = 1

    def test_correct_is_active_true(self):
        """ Correct is_active"""
        self.curr_config.is_active = True

    def test_correct_is_active_false(self):
        """ Correct is_active"""
        self.curr_config.is_active = False

    def test_correct_is_active_active(self):
        """ Correct is_active"""
        self.curr_config.is_active = 'ACTIVE'
        self.assertTrue(self.curr_config.is_active)

    def test_correct_is_active_deactive(self):
        """ Correct is_active"""
        self.curr_config.is_active = 'DEACTIVED'
        self.assertFalse(self.curr_config.is_active)


class TestCurrentConfigIsOptimized(unittest.TestCase):
    """ Test all combinations for is_optimized """

    def setUp(self):
        self.curr_config = CurrentConfig()

    def test_incorrect_is_optimized_empty(self):
        """ is_optimized cannot be empty """
        with self.assertRaises(ValueError):
            self.curr_config.is_optimized = ""

    def test_incorrect_is_optimized_none(self):
        """ is_optimized cannot be None """
        with self.assertRaises(ValueError):
            self.curr_config.is_optimized = None

    def test_incorrect_is_optimized_one(self):
        """ is_optimized cannot be integer """
        with self.assertRaises(ValueError):
            self.curr_config.is_optimized = 1

    def test_incorrect_is_optimized_string(self):
        """ is_optimized cannot be string """
        with self.assertRaises(ValueError):
            self.curr_config.is_optimized = 'yes'

    def test_correct_is_optimized_true(self):
        """ Correct is_optimized """
        self.curr_config.is_optimized = True

    def test_correct_is_optimized_false(self):
        """ Correct is_optimized """
        self.curr_config.is_optimized = False


class TestCurrentConfigIsExpired(unittest.TestCase):
    """ Test all combinations for is_expired """

    def setUp(self):
        self.curr_config = CurrentConfig()

    def test_incorrect_is_expired_empty(self):
        """ is_expired cannot be empty """
        with self.assertRaises(ValueError):
            self.curr_config.is_expired = ""

    def test_incorrect_is_expired_none(self):
        """ is_expired cannot be None """
        with self.assertRaises(ValueError):
            self.curr_config.is_expired = None

    def test_incorrect_is_expired_one(self):
        """ is_expired cannot be integer """
        with self.assertRaises(ValueError):
            self.curr_config.is_expired = 1

    def test_incorrect_is_expired_string(self):
        """ is_expired cannot be a string """
        with self.assertRaises(ValueError):
            self.curr_config.is_expired = 'yes'

    def test_correct_is_expired_true(self):
        """ Correct is_expired """
        self.curr_config.is_expired = True

    def test_correct_is_expired_false(self):
        """ Correct is_expired """
        self.curr_config.is_expired = False


class TestCurrentConfigIsUp(unittest.TestCase):
    """ Test all combinations for is_up """

    def setUp(self):
        self.curr_config = CurrentConfig()

    def test_incorrect_is_up_empty(self):
        """ is_up cannot be empty """
        with self.assertRaises(ValueError):
            self.curr_config.is_up = ""

    def test_incorrect_is_up_none(self):
        """ is_up cannot be None """
        with self.assertRaises(ValueError):
            self.curr_config.is_up = None

    def test_incorrect_is_up_one(self):
        """ is_up cannot be integer """
        with self.assertRaises(ValueError):
            self.curr_config.is_up = 1

    def test_incorrect_is_up_string(self):
        """ is_up cannot be a string """
        with self.assertRaises(ValueError):
            self.curr_config.is_up = 'yes'

    def test_correct_is_up_true(self):
        """ Correct is_up """
        self.curr_config.is_up = True

    def test_correct_is_up_false(self):
        """ Correct is_up """
        self.curr_config.is_up = False


class TestCurrentConfigIsBackup(unittest.TestCase):
    """ Test all combinations for is_backup """

    def setUp(self):
        self.curr_config = CurrentConfig()

    def test_incorrect_is_backup_empty(self):
        """ is_backup cannot be empty """
        with self.assertRaises(ValueError):
            self.curr_config.is_backup = ""

    def test_incorrect_is_backup_none(self):
        """ is_backup cannot be None """
        with self.assertRaises(ValueError):
            self.curr_config.is_backup = None

    def test_incorrect_is_backup_one(self):
        """ is_backup cannot be integer """
        with self.assertRaises(ValueError):
            self.curr_config.is_backup = 1

    def test_incorrect_is_backup_string(self):
        """ is_backup cannot be a string """
        with self.assertRaises(ValueError):
            self.curr_config.is_backup = 'yes'

    def test_correct_is_backup_true(self):
        """ Correct is_backup """
        self.curr_config.is_backup = True

    def test_correct_is_backup_false(self):
        """ Correct is_backup """
        self.curr_config.is_backup = False


if __name__ == '__main__':
    unittest.main()
