import unittest
from .test_platform import TestPlatform
from .test_repository import TestRepository
from .test_branch import TestBranch
from .test_node import TestNode

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPlatform)
    suite.addTest(TestRepository)
    suite.addTest(TestBranch)
    suite.addTest(TestNode)

    return suite

if __name__ == "__main__":
    suite = create_suite()
    runner = unittest.TextTestRunner()

    runner.run(suite)