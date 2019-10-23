''' Test pyext standalone sub-modules

History:
04-05-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'
import unittest

from dds_pylib.pyext import multi_getattr, nearly_equal
from dds_pylib.pyext.objects import ObjectDict


class TestMultiGetAttr(unittest.TestCase):
    ''' test methods for flatten '''

    def setUp(self):
        ''' initialize instance '''
        sub2 = ObjectDict({
            'sub2_key1': 'sub2_value1',
            'sub2_key2': 'sub2_value2'
        })
        sub1 = ObjectDict({
            'sub1_key': 'sub1_value',
            'sub2_key2': sub2,
        })
        self.ma = ObjectDict({'key': sub1})

    def test_name(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            multi_getattr(multi_getattr, '__name__'), 'multi_getattr'
        )

    def test_objdict_sub1(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            multi_getattr(self.ma, 'key.sub1_key'), 'sub1_value'
        )

    def test_objdict_sub2(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            multi_getattr(self.ma, 'key.sub2_key2.sub2_key2'), 'sub2_value2'
        )


class TestNearlyEqual(unittest.TestCase):
    ''' test methods for flatten '''

    def test_equal(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertTrue(nearly_equal(a=10, b=10))

    def test_equal_sig_4(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertTrue(nearly_equal(a=10, b=10.00001, sig_fig=4))

    def test_equal_sig_4_false(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertFalse(nearly_equal(a=10, b=10.0001, sig_fig=4))


if __name__ == '__main__':
    unittest.main()
