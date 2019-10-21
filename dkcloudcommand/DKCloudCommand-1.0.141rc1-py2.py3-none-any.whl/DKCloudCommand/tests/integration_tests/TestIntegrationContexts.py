import json
import os
import shutil
import tempfile
import unittest

from os.path import expanduser

from click.testing import CliRunner
from DKCloudCommand.tests.integration_tests.BaseTestCloud import BaseTestCloud
from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.modules.DKCloudCommandConfig import DKCloudCommandConfig
from DKCloudCommand.modules.DKFileHelper import DKFileHelper


class TestIntegrationContexts(BaseTestCloud):

    def test_contexts(self):
        # Test Cleanup
        self._delete_context('test03', skip_checks=True)
        self._delete_context('test02', skip_checks=True)
        self._delete_context('test01', skip_checks=True)

        # Initial check
        expected_context_list = ['default', 'test']
        unexpected_context_list = ['test01', 'test02', 'test03']
        current_context = 'test'
        self.assertTrue(
            self._check_contexts(expected_context_list, unexpected_context_list, current_context)
        )

        # Create test contexts
        self.assertTrue(self._create_context('test01'))
        self.assertTrue(self._create_context('test02'))
        self.assertTrue(self._create_context('test03'))

        expected_context_list = ['default', 'test', 'test01', 'test02', 'test03']
        unexpected_context_list = []
        current_context = 'test'
        self.assertTrue(
            self._check_contexts(expected_context_list, unexpected_context_list, current_context)
        )

        # Context switch
        self.assertTrue(self._context_switch('test02'))

        expected_context_list = ['default', 'test', 'test01', 'test02', 'test03']
        unexpected_context_list = []
        current_context = 'test02'
        self.assertTrue(
            self._check_contexts(expected_context_list, unexpected_context_list, current_context)
        )

        # Context switch
        self.assertTrue(self._context_switch('test'))

        expected_context_list = ['default', 'test', 'test01', 'test02', 'test03']
        unexpected_context_list = []
        current_context = 'test'
        self.assertTrue(
            self._check_contexts(expected_context_list, unexpected_context_list, current_context)
        )

        # Working path check
        cfg = DKCloudCommandConfig()
        home = expanduser('~')  # does not end in a '/'
        dk_temp_folder = os.path.join(home, '.dk')
        cfg.set_dk_temp_folder(dk_temp_folder)
        general_config_file_data = DKFileHelper.read_file(cfg.get_general_config_file_location())
        general_config_dict = json.loads(general_config_file_data)
        self.assertTrue(
            general_config_dict[cfg.DK_CHECK_WORKING_PATH],
            'Configure %s as true at {HOME}/.dk/general-config.json' % cfg.DK_CHECK_WORKING_PATH
        )

        orig_dir = os.getcwd()
        temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        working_dir = os.path.join(temp_dir, 'test02', 'myfolder')
        os.makedirs(working_dir)
        os.chdir(working_dir)

        runner = CliRunner()
        result = runner.invoke(dk, ["kl"])
        rv = result.output
        os.chdir(orig_dir)
        message = 'Warning: context name "test02" shows up in your current working path,\nbut your current context is "test".'  # noqa: E501
        self.assertTrue(message in rv)

        # Delete test contexts
        self.assertTrue(self._delete_context('test03'))
        self.assertTrue(self._delete_context('test02'))
        self.assertTrue(self._delete_context('test01'))

        # Final check
        expected_context_list = ['default', 'test']
        unexpected_context_list = ['test01', 'test02', 'test03']
        current_context = 'test'
        self.assertTrue(
            self._check_contexts(expected_context_list, unexpected_context_list, current_context)
        )

        # Remove temp files
        shutil.rmtree(temp_dir, ignore_errors=True)

    # ----------------------------- Helper Methods ---------------------------------------------------------------------
    def _context_switch(self, context_name):
        runner = CliRunner()
        result = runner.invoke(dk, ["context-switch", "--yes", context_name])
        self.assertEqual(0, result.exit_code, result.output)
        delete_message = 'Switching to context %s' % context_name
        self.assertTrue(delete_message in result.output)
        self.assertTrue('Context switch done.' in result.output)

        # Check file system
        home = expanduser('~')
        context_file_path = os.path.join(home, '.dk', '.context')
        context_file_contents = DKFileHelper.read_file(context_file_path)
        self.assertEqual(context_name, context_file_contents)

        context_folder_path = os.path.join(home, '.dk', context_name)
        self.assertTrue(os.path.exists(context_folder_path))
        return True

    def _delete_context(self, context_name, skip_checks=False):
        runner = CliRunner()
        result = runner.invoke(dk, ["context-delete", "--yes", context_name])
        if not skip_checks:
            self.assertEqual(0, result.exit_code, result.output)
            delete_message = 'Deleting context %s' % context_name
            self.assertTrue(delete_message in result.output)
            self.assertTrue('Done!' in result.output)

        # Check file system
        home = expanduser('~')
        full_path = os.path.join(home, '.dk', context_name)
        if os.path.exists(full_path):
            return False

        return True

    def _create_context(self, context_name):
        home = expanduser('~')
        source = os.path.join(home, '.dk', 'test')
        target = os.path.join(home, '.dk', context_name)
        shutil.copytree(source, target)
        return True

    def _check_contexts(
            self, expected_context_list, unexpected_context_list=[], current_context='test'
    ):
        runner = CliRunner()
        result = runner.invoke(dk, ["context-list"])
        self.assertEqual(0, result.exit_code, result.output)
        splitted_output = result.output.split('\n')

        found_title = False

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'Available contexts are ...' in splitted_output[index]:
                    found_title = True
                index += 1
                continue
        if not found_title:
            return False

        current_context_legend = 'Current context is: %s' % current_context
        if current_context_legend not in result.output:
            return False

        for context in unexpected_context_list:
            if context in result.output:
                return False

        for context in expected_context_list:
            if context not in result.output:
                return False
        return True


if __name__ == '__main__':
    unittest.main()
