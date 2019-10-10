import os
import unittest

from dq.config import Config


class TestConfig(unittest.TestCase):

    def test_get(self):
        assert Config.get('author.email') == 'unittest@danqing.io'
        assert not Config.get('author.phone')
        assert os.getenv('NUMBER1') == 'cornell'

    def test_get_local2(self):
        os.environ['DQENV'] = 'local2'
        os.environ['NUMBER1'] = ''
        Config._instance = None
        assert Config.get('author.email') == 'unittest2@danqing.io'
        assert not os.getenv('NUMBER1')
        os.environ['DQENV'] = ''
        Config._instance = None
