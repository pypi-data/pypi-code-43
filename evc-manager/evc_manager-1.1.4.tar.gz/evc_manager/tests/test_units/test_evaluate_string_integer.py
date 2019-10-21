"""
    Test tracing.trace_entries
"""
import unittest
from libs.core.fix_variables import evaluate_str
from libs.core.fix_variables import evaluate_integer


class TestStr(unittest.TestCase):
    """ Test all combinations for evaluate_str """

    def setUp(self):
        """ setUp """
        self.str_empty = ""
        self.str_none = None
        self.str_dict = dict()
        self.str_list = list()

    def test_incorrect_evaluate_str_empty(self):
        """ String cannot be empty"""
        with self.assertRaises(ValueError):
            evaluate_str(self.str_empty, 'string')

    def test_incorrect_evaluate_str_none(self):
        """ String cannot be empty"""
        with self.assertRaises(ValueError):
            evaluate_str(self.str_none, 'string')

    def test_incorrect_evaluate_str_dict(self):
        """ String cannot be a dictionary"""
        with self.assertRaises(ValueError):
            evaluate_str(self.str_dict, 'string')

    def test_incorrect_evaluate_str_list(self):
        """ String cannot be a list"""
        with self.assertRaises(ValueError):
            evaluate_str(self.str_list, 'string')

    @staticmethod
    def test_correct_name_integer():
        """ Correct String"""
        evaluate_str(1, 'string')

    @staticmethod
    def test_correct_name_capital_str():
        """ Correct String"""
        evaluate_str('String', 'string')

    @staticmethod
    def test_correct_name_lower_str():
        """ Correct String"""
        evaluate_str('string', 'string')


class TestInt(unittest.TestCase):
    """ Test all combinations for evaluate_int """

    def setUp(self):
        """ setUp """
        self.int_empty = ""
        self.int_none = None
        self.int_dict = dict()
        self.int_list = list()

    def test_incorrect_evaluate_integer_empty(self):
        """ integer cannot be empty"""
        with self.assertRaises(ValueError):
            evaluate_integer(self.int_empty, 'integer')

    def test_incorrect_evaluate_integer_none(self):
        """ integer cannot be empty"""
        with self.assertRaises(ValueError):
            evaluate_integer(self.int_none, 'integer')

    def test_incorrect_evaluate_integer_dict(self):
        """ integer cannot be a dictionary"""
        with self.assertRaises(ValueError):
            evaluate_integer(self.int_dict, 'integer')

    def test_incorrect_evaluate_integer_list(self):
        """ integer cannot be a list"""
        with self.assertRaises(ValueError):
            evaluate_integer(self.int_list, 'integer')

    def test_incorrect_evaluate_integer_negative(self):
        """ integer cannot be a negative"""
        with self.assertRaises(ValueError):
            evaluate_integer(-1, 'integer')

    def test_incorrect_evaluate_string_integer_negative(self):
        """ integer cannot be a negative"""
        with self.assertRaises(ValueError):
            evaluate_integer('-1', 'integer')

    @staticmethod
    def test_correct_name_integer():
        """ Correct integer"""
        evaluate_integer('1', 'integer')

    @staticmethod
    def test_correct_name_capital_int():
        """ Correct integer"""
        evaluate_integer(1, 'integer')

    @staticmethod
    def test_correct_name_lower_int():
        """ Correct integer"""
        evaluate_integer(100000, 'integer')


if __name__ == '__main__':
    unittest.main()
