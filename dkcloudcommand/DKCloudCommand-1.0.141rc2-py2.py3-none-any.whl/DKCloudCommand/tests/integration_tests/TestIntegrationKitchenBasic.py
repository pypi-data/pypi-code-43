import os
import shutil
import tempfile
import time
import unittest

from click.testing import CliRunner
from shutil import copy

from DKCloudCommand.tests.integration_tests.BaseTestCloud import BaseTestCloud
from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKKitchenDisk import DKKitchenDisk
from DKCloudCommand.modules.DKPathHelper import DKPathHelper


class TestIntegrationKitchenBasic(BaseTestCloud):

    def test_kitchen_config(self):
        parent = 'CLI-Top'
        kitchen = 'temp-kitchen-config'
        kitchen = self._add_my_guid(kitchen)
        runner = CliRunner()

        # delete previous runs
        result = runner.invoke(dk, ['kitchen-delete', kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)

        # create kitchen
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent, kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        result2 = runner.invoke(dk, ['kitchen-list'])
        self.assertEqual(0, result2.exit_code, result.output)
        rv = result2.output
        self.assertTrue(kitchen in rv)  # kitchen should be in the list

        # kitchen config list all
        result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "--listall"])
        self.assertEqual(0, result.exit_code, result.output)

        # kitchen config add a new value
        result = runner.invoke(
            dk, ["kitchen-config", "--kitchen", kitchen, "-a", "test_override", "test_value"]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue("test_override added with value 'test_value'" in result.output)

        # kitchen config list all, check new value is there
        result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "--listall"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('test_override            test_value' in result.output)

        # kitchen config get new value
        result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "-g", "test_override"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue("test_value" in result.output)

        # kitchen config remove new value
        result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "-u", "test_override"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue("test_override unset" in result.output)

        # kitchen config list all, check new value is not there any more
        result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "--listall"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertFalse('test_override            test_value' in result.output)

        # kitchen config get new value, but should not be there any more
        result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "-g", "test_override"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertFalse("test_value" in result.output)
        self.assertTrue("none" in result.output)

        # delete kitchen once we are done
        result = runner.invoke(dk, ['kitchen-delete', kitchen, '--yes'])
        self.assertEqual(0, result.exit_code, result.output)

    def test_a_kitchen_list(self):
        tv1 = 'CLI-Top'
        tv2 = 'kitchens-plus'
        tv3 = 'master'
        runner = CliRunner()
        result = runner.invoke(dk, ['kitchen-list'])
        rv = result.output
        self.assertTrue(tv1 in rv)
        self.assertTrue(tv2 in rv)
        self.assertTrue(tv3 in rv)

    def test_kitchen_which(self):

        kn = 'bobo'
        temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        os.chdir(temp_dir)
        DKKitchenDisk.write_kitchen(kn, temp_dir)
        os.chdir(os.path.join(temp_dir, kn))

        runner = CliRunner()
        result = runner.invoke(dk, ['kitchen-which'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertIn('bobo', result.output)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_kitchen_get(self):
        tk = 'CLI-Top'
        recipe1 = 'simple'
        recipe2 = 'parallel-recipe-test'
        runner = CliRunner()

        temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        os.chdir(temp_dir)
        result = runner.invoke(dk, ['kitchen-get', tk, '--recipe', recipe1, '--recipe', recipe2])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertEqual(os.path.isdir(os.path.join(temp_dir, tk, recipe1)), True)
        self.assertTrue(
            DKPathHelper.normalize('simple/node2/data_sinks', DKPathHelper.WIN) in result.output
        )
        self.assertTrue(
            DKPathHelper.normalize('parallel-recipe-test/node1/data_sources', DKPathHelper.WIN) in
            result.output
        )
        shutil.rmtree(temp_dir, ignore_errors=True)

        temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        os.chdir(temp_dir)
        result = runner.invoke(dk, ['kitchen-get', tk])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertEqual(os.path.isdir(os.path.join(temp_dir, tk, '.dk')), True)
        self.assertEqual(os.path.isfile(os.path.join(temp_dir, tk, '.dk', 'KITCHEN_META')), True)
        shutil.rmtree(temp_dir, ignore_errors=True)

        temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        os.chdir(temp_dir)
        result = runner.invoke(dk, ['kitchen-get', tk, '--recipe', recipe1])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertEqual(os.path.isdir(os.path.join(temp_dir, tk, recipe1)), True)
        self.assertTrue(
            DKPathHelper.normalize('simple/node2/data_sinks', DKPathHelper.WIN) in result.output
        )
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_kitchen_create(self):
        parent = 'CLI-Top'
        kitchen = 'temp-create-kitchen-CL'
        kitchen = self._add_my_guid(kitchen)
        runner = CliRunner()

        result = runner.invoke(dk, ['kitchen-delete', kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent, kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        result2 = runner.invoke(dk, ['kitchen-list'])
        self.assertEqual(0, result2.exit_code, result.output)
        rv = result2.output
        self.assertTrue(kitchen in rv)  # kitchen should be in the list

        result = runner.invoke(dk, ['kitchen-delete', kitchen, '--yes'])
        self.assertEqual(0, result.exit_code, result.output)

    def test_kitchen_delete(self):
        parent = 'CLI-Top'
        kitchen = 'temp-delete-kitchen-CL'
        kitchen = self._add_my_guid(kitchen)
        runner = CliRunner()

        runner.invoke(dk, ['kitchen-delete', kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent, kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        result = runner.invoke(dk, ['kitchen-delete', kitchen, '--yes'])
        self.assertEqual(0, result.exit_code, result.output)
        result2 = runner.invoke(dk, ['kitchen-list'])
        self.assertEqual(0, result2.exit_code, result2.output)
        self.assertTrue(kitchen not in result2.output)  # kitchen should not be in the list

    def test_kitchen_settings(self):
        # setup
        orig_dir = os.getcwd()
        test_kitchen = "master"
        temp_dir = tempfile.mkdtemp(prefix=test_kitchen, dir=BaseTestCloud._TEMPFILE_LOCATION)
        os.chdir(temp_dir)
        runner = CliRunner()

        # kitchen-settings-get
        result = runner.invoke(dk, ['kitchen-settings-get'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('succeeded' in result.output)
        self.assertTrue(
            'Find the kitchen-settings.json file in the current directory' in result.output
        )

        file_name = 'kitchen-settings.json'
        file_path = os.path.join(temp_dir, file_name)
        contents = DKFileHelper.read_file(file_path)
        self.assertTrue('kitchenwizard' in contents)
        self.assertTrue('agile-tools' in contents)

        # backup the original file
        backup_file_name = 'kitchen-settings.json.bkp'
        backup_file_path = os.path.join(temp_dir, backup_file_name)
        copy(file_path, backup_file_path)

        # edit the file
        my_settings = "{\"kitchenwizard\" : {\"wizards\": [], \"variablesets\": []}, \"agile-tools\": null}"
        DKFileHelper.write_file(file_path, my_settings)
        contents = DKFileHelper.read_file(file_path)
        self.assertTrue('variablesets' in contents)

        # kitchen-settings-update
        result = runner.invoke(dk, ['kitchen-settings-update', file_path])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Updating the settings' in result.output)
        self.assertTrue('succeeded' in result.output)

        # restore the file
        copy(backup_file_path, file_path)

        # kitchen-settings-update
        result = runner.invoke(dk, ['kitchen-settings-update', file_path])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Updating the settings' in result.output)
        self.assertTrue('succeeded' in result.output)

        # cleanup
        os.chdir(orig_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
