''' Test decorators module

History:
04-05-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

import unittest
import warnings
from dds_pylib.decorators import annotate, deprecated


class TestDeprecated(unittest.TestCase):
    ''' test methods for deprecated '''

    @deprecated
    def square(self, a):
        return a ^ 2

    def setUp(self):
        '''
        initialize instance of ObjectDict
        '''

        self.warn = None
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            self.square(2)
            warnings.simplefilter('default')
            # -1 is the last element in the list
            self.warn = w[-1]

    def test_subclass(self):
        '''
        test that deprecated is working as expected
        '''
        self.assertTrue(issubclass(self.warn.category, DeprecationWarning))

    def test_deprecated_func(self):
        '''
        test that deprecated is working as expected
        '''
        self.assertTrue("deprecated function {fn}".format(
            fn=self.square.__name__) in str(self.warn.message))

    # unsure of how to test static_vars at the moment
    # def test_static_vars(self):
    #     '''
    #     test that deprecated is working as expected
    #     '''
    #     self.assertTrue("deprecated function {fn}".format(
    #         fn=self.square.__name__) in str(self.warn.message))


if __name__ == '__main__':
    unittest.main()
