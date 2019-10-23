''' Test that imports work correctly

History:
09-20-2018 - 1.0.1 - Stephen Funkhouser
    Add import test for static_vars, timeit
04-06-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.1'

import unittest
import warnings

# don't use because we don't want to allow import *
# ----------------------------------------------------
# import * only allowed at module level
# from dds_pylib.pyext import *
# ----------------------------------------------------


class TestDecorators(unittest.TestCase):
    ''' test decorators importing '''

    def test_annotate(self):
        ''' test convience import path '''
        # full import path
        from dds_pylib.decorators.annotate import annotate as f
        # test convience import path
        from dds_pylib.decorators import annotate as c
        self.assertIs(f, c)

    def test_deprecated(self):
        ''' test convience import path '''
        # full import path
        from dds_pylib.decorators.deprecated import deprecated as f
        # test convience import path
        from dds_pylib.decorators import deprecated as c
        self.assertIs(f, c)

    def test_static_vars(self):
        ''' test convience import path '''
        # full import path
        from dds_pylib.decorators.static_vars import static_vars as f
        # test convience import path
        from dds_pylib.decorators import static_vars as c
        self.assertIs(f, c)

    def test_timeit(self):
        ''' test convience import path '''
        # full import path
        from dds_pylib.decorators.time_decorators import timeit as f
        # test convience import path
        from dds_pylib.decorators import timeit as c
        self.assertIs(f, c)

class TestPyext(unittest.TestCase):
    ''' test pyext importing '''

    # def assert_import(self, msg):
    # ''' assert with a custom message

    # ** Leaving here to describe why I didn't implement **

    # There's not an easy way to create an AssertionError with a custom message
    # '''
    # try:
    #     assert False, "Hello!"
    # except AssertionError as e:
    #     e.args = (msg,)
    #     raise
    # raise AssertionError('asdf')
    # try:
    #     self.assertTrue(False, "ERROR: " + msg)
    # except:
    #     # Remove traceback info as we don't need it
    #     unittest_exception = sys.exc_info()
    #     raise unittest_exception[0], unittest_exception[1], unittest_exception[2].tb_next

    def test_collection_multidim_list(self):
        '''
        test full path import of multidim_list
        '''
        # try:
        #     from dds_pylib.pyext.collection import multidim_lis
        # except ImportError:
        #     self.assert_import(msg='asdf')
        from dds_pylib.pyext.collection import multidim_list

    # don't use because we don't want to allow import *
    # def test_import_all(self):
    #     '''
    #     test that module level from pyext import * is the same as local full path import
    #     '''
    #     # import locally via full path and compare to module level import *
    #     from dds_pylib.pyext.collection import multidim_list, flatten

    #     self.assertIs(multidim_list, collection.multidim_list)
    #     self.assertIs(flatten, collection.flatten)


if __name__ == '__main__':
    unittest.main()
