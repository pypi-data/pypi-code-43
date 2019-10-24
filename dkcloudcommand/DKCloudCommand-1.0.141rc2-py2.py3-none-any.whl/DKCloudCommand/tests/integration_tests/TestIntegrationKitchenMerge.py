import os
import shutil
import time
import unittest

from click.testing import CliRunner

from DKCloudCommand.tests.integration_tests.BaseTestCloud import BaseTestCloud
from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.modules.DKFileHelper import DKFileHelper


class TestIntegrationKitchenMerge(BaseTestCloud):

    def test_merge_kitchens_no_changes(self):
        clean_up = True

        existing_kitchen_name = 'master'
        base_test_kitchen_name = 'base-test-kitchen'
        base_test_kitchen_name = self._add_my_guid(base_test_kitchen_name)
        branched_test_kitchen_name = 'branched-from-base-test-kitchen'
        branched_test_kitchen_name = self._add_my_guid(branched_test_kitchen_name)

        # setup
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', branched_test_kitchen_name, '--yes'])
        runner.invoke(dk, ['kitchen-delete', base_test_kitchen_name, '--yes'])
        # test
        # create base kitchen
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(
            dk, ['kitchen-create', '-p', existing_kitchen_name, base_test_kitchen_name]
        )
        self.assertEqual(0, result.exit_code, result.output)
        # create branch kitchen from base kitchen
        time.sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(
            dk, ['kitchen-create', '-p', base_test_kitchen_name, branched_test_kitchen_name]
        )
        self.assertEqual(0, result.exit_code, result.output)

        # do merge preview
        result = runner.invoke(
            dk, [
                'kitchen-merge-preview', '--source_kitchen', branched_test_kitchen_name,
                '--target_kitchen', base_test_kitchen_name, '-cpr'
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Previewing merge Kitchen' in result.output)
        self.assertTrue('Merge Preview Results' in result.output)
        self.assertTrue('Nothing to merge.' in result.output)
        self.assertTrue('Kitchen merge preview done.' in result.output)

        git_url = os.environ.get("GITHUB_URL", 'https://ghe.datakitchen.io')
        url_string = 'Url: \t%s/api/v3/DataKitchen/DKCustomers/compare/%s...%s' % \
                     (git_url, base_test_kitchen_name, branched_test_kitchen_name)
        self.assertTrue(url_string in result.output)
        self.assertTrue('Url:' in result.output)

        # do merge
        result = runner.invoke(
            dk, [
                'kitchen-merge', '--source_kitchen', branched_test_kitchen_name, '--target_kitchen',
                base_test_kitchen_name, '--yes'
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self._check_no_merge_conflicts(result.output)

        # cleanup
        if clean_up:
            runner.invoke(dk, ['kitchen-delete', branched_test_kitchen_name, '--yes'])
            runner.invoke(dk, ['kitchen-delete', base_test_kitchen_name, '--yes'])

    def test_merge_kitchens_changes(self):
        self.assertTrue(True)
        base_kitchen = 'CLI-Top'
        parent_kitchen = self._add_my_guid('merge_changes_parent')
        child_kitchen = self._add_my_guid('merge_changes_child')
        recipe = 'simple'
        new_file = 'new-file.txt'
        new_file2 = 'new-file2.txt'
        new_dir = 'new-dir'

        temp_dir_child, kitchen_dir_child, recipe_dir_child = self._make_recipe_dir(
            recipe, child_kitchen
        )
        temp_dir_parent, kitchen_dir_parent, recipe_dir_parent = self._make_recipe_dir(
            recipe, parent_kitchen
        )

        runner = CliRunner()

        setup = True
        cleanup = True
        if setup:
            runner.invoke(dk, ['kitchen-delete', child_kitchen, '--yes'])
            runner.invoke(dk, ['kitchen-delete', parent_kitchen, '--yes'])

            time.sleep(BaseTestCloud.SLEEP_TIME)
            result = runner.invoke(dk, ['kitchen-create', '--parent', base_kitchen, parent_kitchen])
            self.assertTrue(0 == result.exit_code)

            time.sleep(BaseTestCloud.SLEEP_TIME)
            result = runner.invoke(
                dk, ['kitchen-create', '--parent', parent_kitchen, child_kitchen]
            )
            self.assertTrue(0 == result.exit_code)

            # get parent recipe
            os.chdir(kitchen_dir_child)
            result = runner.invoke(dk, ['recipe-get', recipe])
            rv = result.output
            self.assertTrue(recipe in rv)
            self.assertTrue(os.path.exists(recipe))

            # change the file and add to child kitchen
            os.chdir(recipe_dir_child)
            with open(new_file, 'w') as f:
                f.write('line1\nchild\nline2\n')
            message = 'adding %s to %s' % (new_file, child_kitchen)
            result = runner.invoke(
                dk, [
                    'file-update', '--kitchen', child_kitchen, '--recipe', recipe, '--message',
                    message, new_file
                ]
            )
            self.assertEqual(0, result.exit_code, result.output)

            os.mkdir(new_dir)
            new_file2_path = os.path.join(new_dir, new_file2)
            with open(new_file2_path, 'w') as f:
                f.write('my new file 2\n')

            message = 'adding %s to %s' % (new_file2, child_kitchen)
            result = runner.invoke(
                dk, [
                    'file-update', '--kitchen', child_kitchen, '--recipe', recipe, '--message',
                    message, new_file2_path
                ]
            )
            self.assertEqual(0, result.exit_code, result.output)

        # do merge preview
        os.chdir(temp_dir_child)
        result = runner.invoke(
            dk, [
                'kitchen-merge-preview', '--source_kitchen', child_kitchen, '--target_kitchen',
                parent_kitchen
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)

        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'Previewing merge Kitchen' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Merge Preview Results' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'ok' in splitted_output[index] and os.path.normpath('simple/new-file.txt'
                                                                       ) in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Kitchen merge preview done.' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            index += 1

        self.assertEqual(5, stage)

        # do merge
        result = runner.invoke(
            dk, [
                'kitchen-merge', '--source_kitchen', child_kitchen, '--target_kitchen',
                parent_kitchen, '--yes'
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)

        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'looking for manually merged files' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Calling Merge ...' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if os.path.normpath('simple/new-dir/new-file2.txt') in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                url = '/dk/index.html#/history/dk/'
                if 'Url:' in splitted_output[index] and url in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            index += 1

        self.assertEqual(5, stage)

        if cleanup:
            runner.invoke(dk, ['kitchen-delete', child_kitchen, '--yes'])
            runner.invoke(dk, ['kitchen-delete', parent_kitchen, '--yes'])
            shutil.rmtree(temp_dir_child, ignore_errors=True)
            shutil.rmtree(temp_dir_parent, ignore_errors=True)

    def test_merge_kitchens_changes_manual(self):
        self.assertTrue(True)
        base_kitchen = 'CLI-Top'
        parent_kitchen = 'merge_resolve_parent'
        parent_kitchen = self._add_my_guid(parent_kitchen)
        child_kitchen = 'merge_resolve_child'
        child_kitchen = self._add_my_guid(child_kitchen)
        recipe = 'simple'
        conflicted_file = 'conflicted-file.txt'

        self.assertTrue(True)

        temp_dir_child, kitchen_dir_child, recipe_dir_child = self._make_recipe_dir(
            recipe, child_kitchen
        )
        temp_dir_parent, kitchen_dir_parent, recipe_dir_parent = self._make_recipe_dir(
            recipe, parent_kitchen
        )

        runner = CliRunner()

        setup = True
        cleanup = True
        if setup:
            runner.invoke(dk, ['kitchen-delete', child_kitchen, '--yes'])
            runner.invoke(dk, ['kitchen-delete', parent_kitchen, '--yes'])

            time.sleep(BaseTestCloud.SLEEP_TIME)
            result = runner.invoke(dk, ['kitchen-create', '--parent', base_kitchen, parent_kitchen])
            self.assertEqual(0, result.exit_code, result.output)

            time.sleep(BaseTestCloud.SLEEP_TIME)
            result = runner.invoke(
                dk, ['kitchen-create', '--parent', parent_kitchen, child_kitchen]
            )
            self.assertEqual(0, result.exit_code, result.output)

            # get parent recipe
            os.chdir(kitchen_dir_parent)
            result = runner.invoke(dk, ['recipe-get', recipe])
            rv = result.output
            self.assertTrue(recipe in rv)
            self.assertTrue(os.path.exists(recipe))

            # change the conflicted file and add to parent kitchen
            os.chdir(recipe_dir_parent)
            with open(conflicted_file, 'w') as f:
                f.write('line1\nparent\nline2\n')
            message = 'adding %s to %s' % (conflicted_file, parent_kitchen)
            result = runner.invoke(
                dk, [
                    'file-update', '--kitchen', parent_kitchen, '--recipe', recipe, '--message',
                    message, conflicted_file
                ]
            )
            self.assertEqual(0, result.exit_code, result.output)

            # change the conflicted file and add to child kitchen
            os.chdir(recipe_dir_child)
            with open(conflicted_file, 'w') as f:
                f.write('line1\nchild\nline2\n')
            message = 'adding %s to %s' % (conflicted_file, child_kitchen)
            result = runner.invoke(
                dk, [
                    'file-update', '--kitchen', child_kitchen, '--recipe', recipe, '--message',
                    message, conflicted_file
                ]
            )
            self.assertEqual(0, result.exit_code, result.output)

        # do merge preview
        os.chdir(temp_dir_parent)
        result = runner.invoke(
            dk, [
                'kitchen-merge-preview', '--source_kitchen', child_kitchen, '--target_kitchen',
                parent_kitchen, '-cpr'
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)

        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'Previewing merge Kitchen' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Merge Preview Results' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'conflict' in splitted_output[index] and os.path.normpath(
                        'simple/conflicted-file.txt') in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Kitchen merge preview done.' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            index += 1

        self.assertEqual(5, stage)

        # do merge without resolving conflicts
        result = runner.invoke(
            dk, [
                'kitchen-merge', '--source_kitchen', child_kitchen, '--target_kitchen',
                parent_kitchen, '--yes'
            ]
        )
        self.assertNotEqual(0, result.exit_code, result.output)

        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'Merging Kitchen' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'looking for manually merged files in temporary directory' in splitted_output[
                        index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'There are unresolved conflicts, please resolve through the following sequence of commands' in splitted_output[  # noqa: E501
                        index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Offending file encountered is: conflicted-file.txt.base' in splitted_output[
                        index]:
                    stage += 1
                index += 1
                continue
            index += 1

        self.assertEqual(5, stage)

        # Resolve the conflict
        base_working_dir = self._api.get_merge_dir()
        path1 = '%s' % base_working_dir
        path2 = '%s_to_%s' % (child_kitchen, parent_kitchen)
        working_dir = os.path.join(path1, path2)
        file_name = 'conflicted-file.txt'
        full_path = os.path.join(working_dir, recipe, file_name)

        with open('%s.base' % full_path, 'w') as f:
            f.write('line1\nmerged\nline2\n')

        result = runner.invoke(
            dk, [
                'file-resolve', '--source_kitchen', child_kitchen, '--target_kitchen',
                parent_kitchen,
                os.path.normpath('simple/%s' % file_name)
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(
            'File resolve for file %s' %
            os.path.normpath('simple/conflicted-file.txt') in result.output
        )
        self.assertTrue('File resolve done.' in result.output)

        resolved_contents = DKFileHelper.read_file('%s.resolved' % full_path)
        self.assertTrue('line1' in resolved_contents)
        self.assertTrue('merged' in resolved_contents)
        self.assertTrue('line2' in resolved_contents)

        # do merge preview after resolving conflicts
        result = runner.invoke(
            dk, [
                'kitchen-merge-preview', '--source_kitchen', child_kitchen, '--target_kitchen',
                parent_kitchen
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)

        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'Previewing merge Kitchen' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Merge Preview Results' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'resolved' in splitted_output[index] and os.path.normpath(
                        'simple/conflicted-file.txt') in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Kitchen merge preview done.' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            index += 1

        self.assertEqual(5, stage)

        # do merge
        result = runner.invoke(
            dk, [
                'kitchen-merge', '--source_kitchen', child_kitchen, '--target_kitchen',
                parent_kitchen, '--yes'
            ]
        )
        self.assertEqual(0, result.exit_code)

        splitted_output = result.output.split('\n')

        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'looking for manually merged files' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Found' in splitted_output[index] and os.path.normpath(
                        '/simple/conflicted-file.txt.resolved') in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'Calling Merge with manual resolved conflicts ...' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Merge done.' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 5:
                url = '/dk/index.html#/history/dk/'
                if 'Url:' in splitted_output[index] and url in splitted_output[index]:
                    stage += 1
                index += 1
                continue

            index += 1

        self.assertEqual(6, stage)

        if cleanup:
            runner.invoke(dk, ['kitchen-delete', child_kitchen, '--yes'])
            runner.invoke(dk, ['kitchen-delete', parent_kitchen, '--yes'])
            shutil.rmtree(temp_dir_child, ignore_errors=True)
            shutil.rmtree(temp_dir_parent, ignore_errors=True)

    # ------------------------------------- Helper Methods ----------------------------------------
    def _check_no_merge_conflicts(self, resp):
        self.assertTrue(str(resp).find('diverged') < 0)


if __name__ == '__main__':
    unittest.main()
