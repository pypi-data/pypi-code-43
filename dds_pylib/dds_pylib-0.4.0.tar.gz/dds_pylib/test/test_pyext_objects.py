''' Test pyext.objects module

History:
04-05-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'
import unittest

from dds_pylib.pyext import objects


class TestObjectDict(unittest.TestCase):
    ''' test methods for objects.ObjectDict '''

    def setUp(self):
        '''
        initialize instance of ObjectDict
        '''
        sub = objects.ObjectDict({'sub_key': 'sub_value'})
        self.objdict = objects.ObjectDict({'x': 20, 'y': sub})

    def test_access_dictionary(self):
        '''
        test that ObjectDict can be accessed as dictionary
        '''
        self.assertEqual(
            self.objdict['x'], 20
        )

    def test_access_attribute(self):
        '''
        test that ObjectDict can be accessed as a class attribute
        '''
        self.assertEqual(
            self.objdict.x, 20
        )

    def test_update_dictionary(self):
        '''
        test that ObjectDict can be update as dictionary
        '''
        # update attribute before assertion
        self.objdict['x'] = 5
        self.assertEqual(
            self.objdict.x, 5
        )

    def test_update_attribute(self):
        '''
        test that ObjectDict can be update as a class attribute
        '''
        # update attribute before assertion
        self.objdict.x = 10
        self.assertEqual(
            self.objdict.x, 10
        )

    def test_nested_attribute(self):
        '''
        test that ObjectDict can be nested without other ObjectDict instances
        '''
        self.assertEqual(
            self.objdict.y.sub_key, 'sub_value'
        )

    def test_nested_dictionary(self):
        '''
        test that ObjectDict can be nested without other ObjectDict instances
        '''
        self.assertEqual(
            self.objdict['y']['sub_key'], 'sub_value'
        )


if __name__ == '__main__':
    unittest.main()
