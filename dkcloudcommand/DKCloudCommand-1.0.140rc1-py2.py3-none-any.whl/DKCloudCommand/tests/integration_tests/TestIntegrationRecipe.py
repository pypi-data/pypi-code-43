import shutil
import datetime
import os
import re
import tempfile
import time
import unittest

from click.testing import CliRunner

from DKCommon.DKJSONUtils import format_file

from DKCloudCommand.tests.integration_tests.BaseTestCloud import (
    BaseTestCloud,
    EMAIL,
    EMAIL_SUFFIX,
)
from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKKitchenDisk import DKKitchenDisk
from DKCloudCommand.modules.DKPathHelper import DKPathHelper


class TestIntegrationRecipe(BaseTestCloud):

    def test_recipe_list(self):
        tv1 = 's3-small-recipe'
        tv2 = 'simple'
        tv3 = 'parallel-recipe-test'
        kitchen_name = 'CLI-Top'
        runner = CliRunner()
        result = runner.invoke(dk, ['recipe-list', '--kitchen', kitchen_name])
        rv = result.output
        self.assertTrue(tv1 in rv)
        self.assertTrue(tv2 in rv)
        self.assertTrue(tv3 in rv)

        temp_dir, kitchen_dir = self._make_kitchen_dir(kitchen_name, change_dir=True)
        result = runner.invoke(dk, ['recipe-list'])
        rv = result.output
        self.assertTrue(tv1 in rv)
        self.assertTrue(tv2 in rv)
        self.assertTrue(tv3 in rv)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_recipe_get(self):
        tv = 'simple'
        kn = 'CLI-Top'

        temp_dir, kitchen_dir = self._make_kitchen_dir(kn, change_dir=True)

        runner = CliRunner()
        result = runner.invoke(dk, ['recipe-get', tv])
        rv = result.output
        self.assertTrue(tv in rv)
        self.assertTrue(os.path.exists(tv))
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_recipe_get_status(self):
        tv = 'simple'
        kn = 'CLI-Top'
        runner = CliRunner()

        # Get something to compare against.
        temp_dir, kitchen_dir = self._make_kitchen_dir(kn, change_dir=True)
        runner.invoke(dk, ['recipe-get', tv])

        new_path = os.path.join(kitchen_dir, tv)
        os.chdir(new_path)
        result = runner.invoke(dk, ['recipe-status'])
        self.assertEqual(result.exit_code, 0)
        self.assertFalse('error' in result.output)

        match = re.search(r"([0-9]*) files are unchanged", result.output)
        self.assertTrue(int(match.group(1)) >= 15)
        self.assertTrue('files are unchanged' in result.output)

        os.chdir(os.path.split(new_path)[0])
        result = runner.invoke(dk, ['recipe-status'])
        self.assertTrue('error' in result.output.lower())
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_update_all_files(self):
        # setup
        parent_kitchen = 'CLI-Top'
        test_kitchen = 'CLI-test_update_file'
        test_kitchen = self._add_my_guid(test_kitchen)
        recipe_name = 'simple'
        recipe_file_key = recipe_name
        file_name = 'description.json'
        message = 'test update CLI-test_update_file'
        update_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        runner = CliRunner()  # for the CLI level
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)

        DKKitchenDisk.write_kitchen(parent_kitchen, temp_dir)
        parent_kitchen_dir = os.path.join(temp_dir, parent_kitchen)
        os.chdir(parent_kitchen_dir)
        original_file = self._get_recipe_file_contents(
            runner, parent_kitchen, recipe_name, recipe_file_key, file_name
        )
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        DKKitchenDisk.write_kitchen(test_kitchen, temp_dir)
        test_kitchen_dir = os.path.join(temp_dir, test_kitchen)
        os.chdir(test_kitchen_dir)
        new_kitchen_file = self._get_recipe_file_contents(
            runner, test_kitchen, recipe_name, recipe_file_key, file_name, temp_dir
        )
        self.assertEqual(original_file, new_kitchen_file)
        new_kitchen_file_dict = self._get_the_dict(new_kitchen_file)
        new_kitchen_file_abspath = os.path.join(
            test_kitchen_dir, os.path.join(recipe_file_key, file_name)
        )
        new_kitchen_file_dict[test_kitchen] = update_str
        new_kitchen_file2 = self._get_the_json_str(new_kitchen_file_dict)
        with open(new_kitchen_file_abspath, 'w') as rfile:
            rfile.seek(0)
            rfile.truncate()
            rfile.write(new_kitchen_file2)
        # test
        orig_dir = os.getcwd()
        working_dir = os.path.join(test_kitchen_dir, recipe_name)
        os.chdir(working_dir)
        result = runner.invoke(dk, ['recipe-update', '--message', message])
        os.chdir(orig_dir)
        self.assertTrue('ERROR' not in result.output)
        new_kitchen_file3 = self._get_recipe_file_contents(
            runner, test_kitchen, recipe_name, recipe_file_key, file_name
        )
        new_kitchen_file2_formatted = format_file(new_kitchen_file2)
        self.assertEqual(new_kitchen_file2_formatted, new_kitchen_file3)

        # cleanup
        runner.invoke(dk, ['kitchen-delete', '--kitchen', test_kitchen, '--yes'])
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_update_file(self):
        # setup
        parent_kitchen = 'CLI-Top'
        test_kitchen = 'CLI-test_update_file'
        test_kitchen = self._add_my_guid(test_kitchen)
        recipe_name = 'simple'
        recipe_file_key = recipe_name
        file_name = 'description.json'
        message = 'test update CLI-test_update_file'
        api_file_key = file_name
        update_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        runner = CliRunner()  # for the CLI level
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)

        DKKitchenDisk.write_kitchen(parent_kitchen, temp_dir)
        parent_kitchen_dir = os.path.join(temp_dir, parent_kitchen)
        os.chdir(parent_kitchen_dir)
        original_file = self._get_recipe_file_contents(
            runner, parent_kitchen, recipe_name, recipe_file_key, file_name
        )
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        DKKitchenDisk.write_kitchen(test_kitchen, temp_dir)
        test_kitchen_dir = os.path.join(temp_dir, test_kitchen)
        os.chdir(test_kitchen_dir)
        new_kitchen_file = self._get_recipe_file_contents(
            runner, test_kitchen, recipe_name, recipe_file_key, file_name, temp_dir
        )
        self.assertEqual(original_file, new_kitchen_file)
        new_kitchen_file_dict = self._get_the_dict(new_kitchen_file)
        new_kitchen_file_abspath = os.path.join(
            test_kitchen_dir, os.path.join(recipe_file_key, file_name)
        )
        new_kitchen_file_dict[test_kitchen] = update_str
        new_kitchen_file2 = self._get_the_json_str(new_kitchen_file_dict)
        with open(new_kitchen_file_abspath, 'w') as rfile:
            rfile.seek(0)
            rfile.truncate()
            rfile.write(new_kitchen_file2)
        # test
        orig_dir = os.getcwd()
        working_dir = os.path.join(test_kitchen_dir, recipe_name)
        os.chdir(working_dir)
        result = runner.invoke(
            dk, ['file-update', '--recipe', recipe_name, '--message', message, api_file_key]
        )
        os.chdir(orig_dir)
        self.assertTrue('ERROR' not in result.output)
        new_kitchen_file3 = self._get_recipe_file_contents(
            runner, test_kitchen, recipe_name, recipe_file_key, file_name
        )
        new_kitchen_file2_formatted = format_file(new_kitchen_file2)
        self.assertEqual(new_kitchen_file2_formatted, new_kitchen_file3)

        # cleanup
        runner.invoke(dk, ['kitchen-delete', '--kitchen', test_kitchen, '--yes'])
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_create_file(self):
        parent_kitchen = 'CLI-Top'
        test_kitchen = 'test_create_file-Runner'
        test_kitchen = self._add_my_guid(test_kitchen)
        recipe_name = 'simple'
        file_name = 'added.sql'
        filedir = 'resources'
        recipe_file_key = os.path.join(recipe_name, filedir)
        api_file_key = os.path.join(filedir, file_name)
        file_contents = '--\n-- sql for you\n--\n\nselect 1024\n\n'
        message = 'test update test_create_file-API'
        runner = CliRunner()

        # create test kitchen
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # make and cd to kitchen dir and get the recipe to disk
        temp_dir = tempfile.mkdtemp(
            prefix='unit-test_create_file', dir=BaseTestCloud._TEMPFILE_LOCATION
        )

        DKKitchenDisk.write_kitchen(test_kitchen, temp_dir)
        kd = os.path.join(temp_dir, test_kitchen)
        orig_dir = os.getcwd()
        os.chdir(kd)
        self._get_recipe(runner, recipe_name)

        # create new file on disk
        try:
            os.chdir(recipe_name)
            f = open(api_file_key, 'w')
            f.write(file_contents)
            f.close()
        except ValueError as e:
            print('could not write file %s.' % e)
            self.assertTrue(False)

        # add file from disk THE TEST
        result = runner.invoke(
            dk, [
                'file-update', '--kitchen', test_kitchen, '--recipe', recipe_name, '--message',
                message, api_file_key
            ]
        )
        self.assertTrue('ERROR' not in result.output.lower())

        # make sure file is in kitchen (get file)
        file_contents2 = self._get_recipe_file_contents(
            runner, test_kitchen, recipe_name, recipe_file_key, file_name
        )
        self.assertEqual(file_contents, file_contents2, 'Create check')

        # Now a negative file-update case
        graph_file = 'graph.json'
        graph_file_path = os.path.join(kd, recipe_name, graph_file)
        file_contents = DKFileHelper.read_file(graph_file_path)
        new_file_contents = file_contents.replace('node1', 'node7')
        DKFileHelper.write_file(graph_file_path, new_file_contents)

        result = runner.invoke(
            dk, [
                'file-update', '--kitchen', test_kitchen, '--recipe', recipe_name, '--message',
                message, graph_file
            ]
        )
        self.assertTrue('node7 does not exist in recipe' in result.output.lower())
        self.assertTrue('unable to update recipe' in result.output.lower())

        # cleanup
        os.chdir(orig_dir)
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_create_recipe(self):
        parent_kitchen = 'CLI-Top'
        test_kitchen = 'cli_test_create_recipe'
        test_kitchen = self._add_my_guid(test_kitchen)
        recipe_name = 'unit-test-my-recipe'
        runner = CliRunner()

        # create test kitchen
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # make and cd to kitchen dir and get the recipe to disk
        temp_dir = tempfile.mkdtemp(prefix=test_kitchen, dir=BaseTestCloud._TEMPFILE_LOCATION)

        # get the new kitchen
        orig_dir = os.getcwd()
        os.chdir(temp_dir)
        result = runner.invoke(dk, ['kitchen-get', test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # recipe_create
        time.sleep(30)
        result = runner.invoke(
            dk, ['recipe-create', '--kitchen', test_kitchen, '--template', 'qs1', recipe_name]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('created recipe %s' % recipe_name in result.output.lower())

        # recipe_get
        kitchen_dir = os.path.join(temp_dir, test_kitchen)
        os.chdir(kitchen_dir)
        result = runner.invoke(dk, ['recipe-get', recipe_name])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(
            "Getting the latest version of Recipe '%s' in Kitchen '%s'" %
            (recipe_name, test_kitchen) in result.output
        )
        self.assertTrue(
            DKPathHelper.normalize('%s/resources' % recipe_name, DKPathHelper.WIN) in result.output
        )

        # show variations
        recipe_dir = os.path.join(kitchen_dir, recipe_name)
        os.chdir(recipe_dir)

        result = runner.invoke(dk, ['recipe-variation-list'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Variations:' in result.output)
        self.assertTrue('variation1' in result.output)

        # Add email
        file_name = 'variables.json'
        file_path = os.path.join(recipe_dir, file_name)
        contents = DKFileHelper.read_file(file_path)
        DKFileHelper.write_file(file_path, contents.replace('[YOUR EMAIL HERE]', EMAIL))
        contents = DKFileHelper.read_file(file_path)
        self.assertTrue(EMAIL in contents)
        self.assertTrue('[YOUR EMAIL HERE]' not in contents)

        # recipe status
        result = runner.invoke(dk, ['recipe-status'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('1 files are modified on local:' in result.output)
        self.assertTrue('variables.json' in result.output)

        # recipe validate
        result = runner.invoke(dk, ['recipe-validate', '--variation', 'variation1'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Validating recipe with local changes applied' in result.output)
        self.assertTrue('No recipe issues identified.' in result.output)

        # file-update
        message = 'cli ut file update'
        result = runner.invoke(dk, ['file-update', '--message', message, file_name])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Updating File(s)' in result.output)
        self.assertTrue('update_file for variables.json' in result.output)
        self.assertTrue('succeeded' in result.output)

        # recipe status
        result = runner.invoke(dk, ['recipe-status'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('1 files are modified on local:' not in result.output)
        self.assertTrue('variables.json' not in result.output)

        # file compile
        result = runner.invoke(dk, ['file-compile', '-v', 'variation1', '-f', 'description.json'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('succeeded' in result.output)
        self.assertTrue(EMAIL in result.output)
        self.assertTrue('[YOUR EMAIL HERE]' not in result.output)

        # config list
        result = runner.invoke(dk, ["config-list"])
        self.assertEqual(0, result.exit_code, result.output)
        found_port = False
        found_ip = False
        splitted_output = result.output.split('\n')
        index = 0
        while index < len(splitted_output):
            if not found_port:
                text = 'Cloud Port:'
                start_index_port = splitted_output[index].find(text)
                if start_index_port != -1:
                    start_index_port += len(text)
                    port = splitted_output[index][start_index_port:].strip('/n').strip()
                    found_port = True
            if not found_ip:
                text = 'Cloud IP:'
                start_index_ip = splitted_output[index].find(text)
                if start_index_ip != -1:
                    start_index_ip += len(text)
                    ip = splitted_output[index][start_index_ip:].strip('/n').strip()
                    found_ip = True
            index += 1

        self.assertTrue(found_port)
        self.assertTrue(found_ip)

        # file history
        result = runner.invoke(dk, ['file-history', '-cc', '5', 'variables.json'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('succeeded' in result.output)
        self.assertTrue('Message:\t%s' % message in result.output)
        self.assertTrue('Message:\tNew recipe %s' % recipe_name in result.output)
        self.assertTrue('Author:' in result.output)
        self.assertTrue('Date:' in result.output)
        self.assertTrue('Url:' in result.output)
        self.assertTrue('%s:%s/dk/index.html#/history/dk/%s/' % (ip, port, test_kitchen))
        self.assertEqual(2, result.output.count('Message:'))

        # modify the file once again
        contents = DKFileHelper.read_file(file_path)
        DKFileHelper.write_file(file_path, contents.replace(EMAIL, 'blah%s' % EMAIL_SUFFIX))
        contents = DKFileHelper.read_file(file_path)
        self.assertTrue('blah%s' % EMAIL_SUFFIX in contents)
        self.assertTrue('[YOUR EMAIL HERE]' not in contents)
        self.assertTrue(EMAIL not in contents)

        # file get
        result = runner.invoke(dk, ['file-get', 'variables.json'])
        print(result.output)
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Getting File (variables.json)' in result.output)
        self.assertTrue('success' in result.output)
        contents = DKFileHelper.read_file(file_path)
        self.assertTrue('blah%s' % EMAIL_SUFFIX not in contents)
        self.assertTrue('[YOUR EMAIL HERE]' not in contents)
        self.assertTrue(EMAIL in contents)

        # recipe list
        result = runner.invoke(dk, ['recipe-list'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(recipe_name in result.output)

        # recipe delete
        recipe_sha_dir = os.path.join(kitchen_dir, '.dk', 'recipes', recipe_name)
        self.assertTrue(os.path.exists(recipe_dir))
        self.assertTrue(os.path.exists(recipe_sha_dir))

        os.chdir(kitchen_dir)
        result = runner.invoke(dk, ['recipe-delete', '--yes', recipe_name])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(
            'This command will delete the local and remote copy of recipe' in result.output
        )
        self.assertTrue('deleted recipe %s' % recipe_name in result.output)

        self.assertFalse(os.path.exists(recipe_dir))
        self.assertFalse(os.path.exists(recipe_sha_dir))

        result = runner.invoke(dk, ['recipe-list'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(recipe_name not in result.output)

        # cleanup
        os.chdir(orig_dir)
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_file_top(self):
        # setup
        temp_dir = None
        parent_kitchen = 'CLI-Top'
        test_kitchen = 'CLI-test_delete_file_top'
        test_kitchen = self._add_my_guid(test_kitchen)
        recipe_name = 'simple'
        recipe_file_key = recipe_name
        file_name = 'description.json'
        message = ' test Delete CLI-test_delete_file_top'
        runner = CliRunner()
        cwd = os.getcwd()
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        try:
            temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        except Exception as e:
            self.assertTrue(False, 'Problem creating temp folder %s' % e)
        os.chdir(temp_dir)
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        DKKitchenDisk.write_kitchen(test_kitchen, temp_dir)
        kitchen_dir = os.path.join(temp_dir, test_kitchen)
        os.chdir(kitchen_dir)
        result = runner.invoke(
            dk, ['file-delete', '--recipe', recipe_name, '--message', message, file_name]
        )
        self.assertTrue('ERROR' not in result.output)
        self.assertTrue(
            self._get_recipe_file_contents(
                runner, test_kitchen, recipe_name, recipe_file_key, file_name, temp_dir
            ) is None, "Found the file"
        )
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        os.chdir(cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_file_deeper(self):
        # setup
        temp_dir = None
        parent_kitchen = 'CLI-Top'
        test_kitchen = 'CLI-test_delete_file_deeper'
        test_kitchen = self._add_my_guid(test_kitchen)
        recipe_name = 'simple'
        recipe_file_key = 'resources/very_cool.sql'
        file_name = 'very_cool.sql'
        message = ' test Delete CLI-test_delete_file_deeper'
        runner = CliRunner()
        cwd = os.getcwd()
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        try:
            temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        except Exception as e:
            self.assertTrue(False, 'Problem creating temp folder %s' % e)
        os.chdir(temp_dir)
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        DKKitchenDisk.write_kitchen(test_kitchen, temp_dir)
        kitchen_dir = os.path.join(temp_dir, test_kitchen)
        os.chdir(kitchen_dir)

        result = runner.invoke(
            dk, ['file-delete', '--recipe', recipe_name, '--message', message, recipe_file_key]
        )
        self.assertTrue('ERROR' not in result.output)
        self.assertTrue(
            self._get_recipe_file_contents(
                runner, test_kitchen, recipe_name, os.path.join(recipe_name, recipe_file_key),
                file_name, temp_dir
            ) is None
        )
        runner.invoke(dk, ['kitchen-delete', '--kitchen', test_kitchen, '--yes'])
        os.chdir(cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_delete_file_deeper_multi(self):
        # setup
        temp_dir = None
        parent_kitchen = 'CLI-Top'
        test_kitchen = 'CLI-test_delete_file_deeper_multi'
        test_kitchen = self._add_my_guid(test_kitchen)
        recipe_name = 'simple'
        recipe_file_key = 'resources/very_cool.sql'
        file_name = 'very_cool.sql'
        file2 = 'description.json'
        message = ' test Delete CLI-test_delete_file_deeper_multi'
        runner = CliRunner()
        cwd = os.getcwd()
        runner.invoke(dk, ['kitchen-delete', test_kitchen, '--yes'])
        try:
            temp_dir = tempfile.mkdtemp(prefix='unit-tests', dir=BaseTestCloud._TEMPFILE_LOCATION)
        except Exception as e:
            self.assertTrue(False, 'Problem creating temp folder %s' % e)
        os.chdir(temp_dir)
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, test_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        DKKitchenDisk.write_kitchen(test_kitchen, temp_dir)
        kitchen_dir = os.path.join(temp_dir, test_kitchen)
        os.chdir(kitchen_dir)

        result = runner.invoke(
            dk,
            ['file-delete', '--recipe', recipe_name, '--message', message, recipe_file_key, file2]
        )
        self.assertTrue('ERROR' not in result.output)
        self.assertTrue(
            self._get_recipe_file_contents(
                runner, test_kitchen, recipe_name, os.path.join(recipe_name, recipe_file_key),
                file_name, temp_dir
            ) is None
        )
        runner.invoke(dk, ['kitchen-delete', '--kitchen', test_kitchen, '--yes'])
        os.chdir(cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_compiled_order_run_from_recipe(self):
        # setup
        parent_kitchen = 'master'
        new_kitchen = 'test_get_compiled_order_run_from_recipe-API'
        new_kitchen = self._add_my_guid(new_kitchen)
        recipe_name = 'parallel-recipe-test'
        variation_name = 'variation-test'
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        # test
        result = runner.invoke(
            dk, [
                'recipe-compile', '--kitchen', new_kitchen, '--recipe', recipe_name, '--variation',
                variation_name
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(
            "succeeded, compiled recipe stored in folder 'compiled-recipe'" in result.output
        )

        # cleanup
        result = runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])
        self.assertEqual(0, result.exit_code, result.output)

    # ------------------------------- Helper Methods ----------------------------------------------
    def _get_recipe(self, runner, recipe):
        result = runner.invoke(dk, ['recipe-get', recipe])
        rv = result.output
        self.assertTrue(recipe in rv)
        return True

    def _get_recipe_file_contents(
            self, runner, kitchen, recipe_name, recipe_file_key, file_name, temp_dir=None
    ):
        delete_temp_dir = False
        if temp_dir is None:
            td = tempfile.mkdtemp(prefix='unit-tests-grfc', dir=BaseTestCloud._TEMPFILE_LOCATION)
            delete_temp_dir = True
            DKKitchenDisk.write_kitchen(kitchen, td)
            kitchen_directory = os.path.join(td, kitchen)
        else:
            td = temp_dir
            kitchen_directory = os.getcwd()
        cwd = os.getcwd()
        os.chdir(kitchen_directory)
        result = runner.invoke(dk, ['recipe-get', recipe_name])
        os.chdir(cwd)
        rv = result.output
        self.assertTrue(recipe_name in rv)
        abspath = os.path.join(td, os.path.join(kitchen, recipe_file_key, file_name))
        if os.path.isfile(abspath):
            with open(abspath, 'r') as rfile:
                rfile.seek(0)
                the_file = rfile.read()
            rc = the_file
        else:
            rc = None
        if delete_temp_dir is True:
            shutil.rmtree(td, ignore_errors=True)
        return rc


if __name__ == '__main__':
    unittest.main()
