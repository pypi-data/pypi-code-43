import os
import pkg_resources
import unittest

from bandit.core import config
from bandit.core import constants
from bandit.core import manager
from bandit.core import extension_loader


class AwsChecksTestCase(unittest.TestCase):

    def setUp(self):
        # create entry point for bandit-aws plugin
        distribution = pkg_resources.Distribution(__file__)
        entry_point = pkg_resources.EntryPoint.parse(
            'hardcoded_aws_key = bandit_aws.aws_checks:hardcoded_aws_key',
            dist=distribution,
        )
        distribution._ep_map = {
            'bandit.plugins': {
                'hardcoded_aws_key': entry_point,
            }
        }
        pkg_resources.working_set.add(distribution)

        # reload the bandit plugins
        extension_loader.MANAGER.load_plugins('bandit.plugins')

        # create a bandit instance
        bandit_config = config.BanditConfig()
        self.b_mgr = manager.BanditManager(bandit_config, 'file')

    def run_example(self, example_script, ignore_nosec=False):
        # copied from bandit test_functional.py

        path = os.path.join(os.getcwd(), 'examples', example_script)
        self.b_mgr.ignore_nosec = ignore_nosec
        self.b_mgr.discover_files([path], True)
        self.b_mgr.run_tests()

    def check_example(self, example_script, expect, ignore_nosec=False):
        # copied from bandit test_functional.py

        # reset scores for subsequent calls to check_example
        self.b_mgr.scores = []
        self.run_example(example_script, ignore_nosec=ignore_nosec)

        result = {
            'SEVERITY': {'UNDEFINED': 0, 'LOW': 0, 'MEDIUM': 0, 'HIGH': 0},
            'CONFIDENCE': {'UNDEFINED': 0, 'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
        }

        for issue in self.b_mgr.results:
            if issue.test_id.startswith("C"):  # ensure it's one of our checks
                result["SEVERITY"][issue.severity] += 1
                result["CONFIDENCE"][issue.confidence] += 1

        self.assertDictEqual(expect, result)

    def test_aws_key(self):
        '''Test the `aws_key` example.'''
        expect = {
            'SEVERITY': {'UNDEFINED': 0, 'LOW': 1, 'MEDIUM': 1, 'HIGH': 0},
            'CONFIDENCE': {'UNDEFINED': 0, 'LOW': 0, 'MEDIUM': 2, 'HIGH': 0}
        }
        self.check_example('aws_key.py', expect)
