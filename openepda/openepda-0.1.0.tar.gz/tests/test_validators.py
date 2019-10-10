import doctest
import unittest
import os

from openepda import validators


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(validators))
    return tests


module_fpath = os.path.abspath(os.path.join(__file__, '..'))


if __name__ == '__main__':
    os.chdir(module_fpath + '/..')
    # print(module_fpath)
    unittest.main()
