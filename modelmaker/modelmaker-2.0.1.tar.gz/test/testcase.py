import os,sys
import unittest
from os.path import expanduser
sys.path.append('../')

config_file = os.path.join(expanduser("~"), ".wcscfg")

class WcsTestCases(unittest.TestCase):
    
    def setUp(self):
        self.cfg = Config(config_file)
        self.cli = Client(self.cfg)
        self.bucket = 'caiyz'
 

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(WcsTestCases("test_simple_upload"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
