import datetime
import os
import tempfile
import unittest

from click.testing import CliRunner
from time import sleep

from DKCloudCommand.tests.integration_tests.BaseTestCloud import BaseTestCloud, WaitLoop
from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKPathHelper import DKPathHelper


class TestIntegrationOrders(BaseTestCloud):

    def test_create_order(self):
        kitchen = 'CLI-Top'
        recipe = 'simple'
        variation = self._get_run_variation_for_recipe(recipe)
        runner = CliRunner()

        # create test kitchen
        result = runner.invoke(
            dk, ['order-run', '--kitchen', kitchen, '--recipe', recipe, '--yes', variation]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('simple' in result.output)

    def test_create_order_params(self):
        kitchen = 'master'
        recipe = 'simple-container-recipe'
        variation = "main"
        runner = CliRunner()
        # create test kitchen
        result = runner.invoke(
            dk, [
                'order-run', '--kitchen', kitchen, '--recipe', recipe, '--yes', '--params',
                '{"testvar":"HOLA!!!!"}', variation
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('simple' in result.output)

    def test_create_order_one_node(self):
        kitchen = 'CLI-Top'
        recipe = 'simple'
        node = 'node2'
        variation = self._get_run_variation_for_recipe(recipe)
        runner = CliRunner()

        # create test kitchen
        result = runner.invoke(
            dk, [
                'order-run', '--kitchen', kitchen, '--recipe', recipe, '--node', node, '--yes',
                variation
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('simple' in result.output)

    def test_delete_all_order(self):
        # setup
        parent_kitchen = 'CLI-Top'
        new_kitchen = 'test_deleteall_orderCLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        recipe = 'simple'
        variation = 'simple-variation-now'
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])  # clean up junk
        sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        result = runner.invoke(
            dk, ['order-run', '--kitchen', new_kitchen, '--recipe', recipe, '--yes', variation]
        )
        self.assertEqual(0, result.exit_code, result.output)
        order_id_raw = result.output
        order_id = order_id_raw.split(':')[1].strip()
        self.assertIsNotNone(variation in order_id)
        # test
        result = runner.invoke(dk, ['order-delete', '--kitchen', new_kitchen, '--yes'])
        self.assertEqual(0, result.exit_code, result.output)
        # cleanup
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])

    def test_delete_one_order(self):
        # setup
        parent_kitchen = 'CLI-Top'
        new_kitchen = 'test_deleteall_orderCLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        recipe = 'simple'
        variation = 'simple-variation-now'
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])  # clean up junk
        sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        result = runner.invoke(
            dk, ['order-run', '--kitchen', new_kitchen, '--recipe', recipe, '--yes', variation]
        )
        self.assertEqual(0, result.exit_code, result.output)

        order_id_raw = result.output
        text = 'Order ID is: '
        index = order_id_raw.find(text)
        index += len(text)
        order_id = order_id_raw[index:].strip('/n').strip()
        self.assertIsNotNone(variation in order_id)
        # test
        result = runner.invoke(
            dk, ['order-delete', '--kitchen', new_kitchen, '--order_id', order_id, '--yes']
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('deleted order %s' % order_id in result.output)
        # cleanup
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])

    def test_order_stop(self):
        # setup
        parent_kitchen = 'CLI-Top-k8s'
        new_kitchen = 'stop-da-order-CLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        recipe = 'test-everything-recipe'
        variation = 'variation-morning-prod05'
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])  # clean up junk
        sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        result = runner.invoke(
            dk, ['order-run', '--kitchen', new_kitchen, '--recipe', recipe, '--yes', variation]
        )
        self.assertEqual(0, result.exit_code, result.output)
        order_id_raw = result.output
        text = 'Order ID is: '
        index = order_id_raw.find(text)
        index += len(text)
        order_id = order_id_raw[index:].strip('/n').strip()
        # test
        sleep(2)

        result_stop = runner.invoke(
            dk, ['order-stop', '--kitchen', new_kitchen, '--order_id', order_id, '--yes']
        )
        self.assertEqual(0, int(result_stop.exit_code), result_stop.output)
        self.assertTrue('stopped order %s' % order_id in result_stop.output)

        # cleanup
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])

    def test_delete_order_bad_order_id(self):
        parent_kitchen = 'CLI-Top'
        new_kitchen = 'delete_order_bad_order_id-CLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])  # clean up junk
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        order_id = 'junk'
        runner = CliRunner()
        result = runner.invoke(
            dk, ['order-delete', '--kitchen', new_kitchen, '--order_id', order_id, '--yes']
        )
        self.assertNotEqual(0, result.exit_code, result.output)
        self.assertTrue('Order id \'junk\' does not exist.' in result.output)

    def test_delete_order_bad_kitchen(self):
        kitchen = 'junk'
        runner = CliRunner()
        result = runner.invoke(dk, ['order-delete', '--kitchen', kitchen, '--yes'])
        self.assertNotEqual(0, result.exit_code, result.output)
        message = 'Kitchen %s was not found in the database or the user does not have access rights.' % kitchen  # noqa: E501
        self.assertTrue(message in result.output)

    # test illegal command line combo
    def test_orderrun_detail_bad_command(self):
        kitchen = 'ppp'
        runner = CliRunner()
        result = runner.invoke(dk, ['orderrun-info', '--kitchen', kitchen, '-o', 'o', '-r', 'r'])
        self.assertNotEqual(0, result.exit_code, result.output)
        self.assertTrue('Error' in result.output)

    def test_list_order(self):
        kitchen = 'CLI-Top'
        runner = CliRunner()
        result = runner.invoke(dk, ['order-list', '--kitchen', kitchen])
        self.assertEqual(0, result.exit_code, result.output)

    def test_list_order_filter_recipe(self):
        kitchen = 'CLI-Top'
        recipe1 = 'simple'
        recipe2 = 's3-small-recipe'
        runner = CliRunner()

        result = runner.invoke(dk, ['order-list', '--kitchen', kitchen, '--recipe', recipe1])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Get Order information for Kitchen %s' % kitchen in result.output)
        self.assertTrue(recipe2 not in result.output)

        result = runner.invoke(dk, ['order-list', '--kitchen', kitchen, '--recipe', recipe2])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Get Order information for Kitchen %s' % kitchen in result.output)
        self.assertTrue(recipe1 not in result.output)

    def test_list_order_paging(self):
        kitchen = 'CLI-Top'
        runner = CliRunner()

        result = runner.invoke(dk, ['order-list', '--kitchen', kitchen])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Get Order information for Kitchen %s' % kitchen in result.output)
        count_paging_default = result.output.count('ORDER SUMMARY')
        self.assertEqual(5, count_paging_default)

        result = runner.invoke(
            dk, [
                'order-list', '--kitchen', kitchen, '--start', 2, '--order_count', 1,
                '--order_run_count', 1
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Get Order information for Kitchen %s' % kitchen in result.output)
        count_paging = result.output.count('ORDER SUMMARY')
        self.assertEqual(1, count_paging)

    def test_orderrun_stop(self):
        parent_kitchen = 'CLI-Top'
        recipe_name = 'test-long-recipe'
        variation_name = 'variation-test'
        new_kitchen = 'test_orderrun_stop-CLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])
        sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # start order & order run
        print('Starting Create-Order in test_orderrun_stop()')
        result = runner.invoke(
            dk, [
                'order-run', '--kitchen', new_kitchen, '--recipe', recipe_name, '--yes',
                variation_name
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Order ID is:' in result.output)

        order_id_raw = result.output
        text = 'Order ID is: '
        index = order_id_raw.find(text)
        index += len(text)
        order_id = order_id_raw[index:].strip('/n').strip()

        found_active_serving = False
        w1 = WaitLoop()

        while w1:
            resp1 = runner.invoke(dk, ['orderrun-info', '-k', new_kitchen, '-o', order_id])
            if resp1.output is not None:
                if "ACTIVE_SERVING" in resp1.output or "PLANNED_SERVING" in resp1.output:
                    found_active_serving = True

                    order_run_id_raw = resp1.output
                    text = 'Order Run ID:'
                    index = order_run_id_raw.find(text)
                    index += len(text)
                    text2 = 'Status:'
                    index2 = order_run_id_raw.find(text2)
                    order_run_id = order_run_id_raw[index:index2].strip('/n').strip()
                    break

        self.assertTrue(found_active_serving)
        print('test_orderrun_stop: found_active_serving is True')

        resp3 = runner.invoke(
            dk, ['orderrun-stop', '-k', new_kitchen, '-ori', order_run_id, '--yes']
        )

        self.assertEqual(0, resp3.exit_code, resp3.output)
        self.assertTrue('stopped order run %s' % order_run_id in resp3.output)

        # check to make sure the serving is in the "STOPPED_SERVING" state
        found_stopped_state = False
        w2 = WaitLoop()
        while w2:
            resp4 = runner.invoke(
                dk, ['orderrun-info', '-k', new_kitchen, '-ori', order_run_id, '--runstatus']
            )
            if resp4.output is not None:
                self.assertFalse('Current context is:' in resp4.output)
                print('got %s' % resp4.output)
                if "STOPPED_SERVING" in resp4.output:
                    found_stopped_state = True
                    break
        self.assertTrue(found_stopped_state)
        print('test_orderrun_stop: found_stopped_state is True')

        # cleanup
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])

    def test_orderrun_resume(self):
        parent_kitchen = 'CLI-Top'
        recipe_name = 'unit-test-order-resume'
        variation_name = 'Variation1'
        new_kitchen = 'test_orderrun_resume-CLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        runner = CliRunner()

        # Delete kitchen if already existing
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])

        # Create Kitchen
        sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # Start order & order run
        print('Starting Create-Order in test_orderrun_resume()')
        result = runner.invoke(
            dk, [
                'order-run', '--kitchen', new_kitchen, '--recipe', recipe_name, '--yes',
                variation_name
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)
        order_id_raw = result.output
        text = 'Order ID is: '
        index = order_id_raw.find(text)
        index += len(text)
        order_id = order_id_raw[index:].strip('/n').strip()

        # Wait for state "SERVING_ERROR"
        desired_state = 'SERVING_ERROR'
        found_desired_serving_state = False
        wait_loop = WaitLoop()

        while wait_loop:
            resp1 = runner.invoke(dk, ['orderrun-info', '-k', new_kitchen, '-o', order_id])
            if resp1.output is not None:
                print('got %s' % resp1.output)
                if desired_state in resp1.output:
                    found_desired_serving_state = True
                    text = 'Order Run ID:'
                    index = resp1.output.find(text)
                    index += len(text)
                    text2 = 'Status:'
                    index2 = resp1.output.find(text2)
                    orderrun_id = resp1.output[index:index2].strip('/n').strip()
                    orderrun_id_error = orderrun_id
                    break

        self.assertTrue(found_desired_serving_state)
        print('test_orderrun_resume: found error in serving')

        # Make temp location
        temp_dir = tempfile.mkdtemp(prefix=new_kitchen, dir=BaseTestCloud._TEMPFILE_LOCATION)

        orig_dir = os.getcwd()
        os.chdir(temp_dir)

        # Get the kitchen
        result = runner.invoke(dk, ['kitchen-get', new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # Get the recipe
        kitchen_dir = os.path.join(temp_dir, new_kitchen)
        os.chdir(kitchen_dir)
        result = runner.invoke(dk, ['recipe-get', recipe_name])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(
            "Getting the latest version of Recipe '%s' in Kitchen '%s'" %
            (recipe_name, new_kitchen) in result.output
        )
        self.assertTrue(
            DKPathHelper.normalize('%s/resources' % recipe_name, DKPathHelper.WIN) in result.output
        )

        # Fix the recipe error
        recipe_dir = os.path.join(kitchen_dir, recipe_name)
        file_name = DKPathHelper.normalize('resources/s3-to-redshift.sql', DKPathHelper.WIN)
        file_path = os.path.join(recipe_dir, file_name)
        contents = DKFileHelper.read_file(file_path)
        DKFileHelper.write_file(
            file_path, contents.replace('make this sql fail', '-- fix this sql')
        )
        contents = DKFileHelper.read_file(file_path)
        self.assertTrue('-- fix this sql' in contents)

        # file-update
        os.chdir(recipe_dir)
        message = 'cli ut file update'
        result = runner.invoke(dk, ['file-update', '--message', message, file_name])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Updating File(s)' in result.output)
        self.assertTrue('update_file for %s' % file_name in result.output)
        self.assertTrue('succeeded' in result.output)

        # recipe status
        result = runner.invoke(dk, ['recipe-status'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('files are modified on local:' not in result.output)
        self.assertTrue('13 files are unchanged' in result.output)

        # Resume the recipe
        result = runner.invoke(
            dk, ['orderrun-resume', '--kitchen', new_kitchen, orderrun_id, '--yes']
        )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('Resuming Order-Run %s' % orderrun_id in result.output)
        self.assertTrue('succeeded' in result.output)

        # Check now is successful, wait for state "COMPLETED_SERVING"
        desired_state = 'COMPLETED_SERVING'
        found_desired_serving_state = False
        wait_loop = WaitLoop()

        while wait_loop:
            resp1 = runner.invoke(dk, ['orderrun-info', '-k', new_kitchen])
            if resp1.output is not None:
                print('got %s' % resp1.output)
                if desired_state in resp1.output:
                    text = 'Order Run ID:'
                    index = resp1.output.find(text)
                    index += len(text)
                    text2 = 'Status:'
                    index2 = resp1.output.find(text2)
                    orderrun_id_success = resp1.output[index:index2].strip('/n').strip()
                    found_desired_serving_state = True
                    break

        self.assertTrue(found_desired_serving_state)
        print('test_orderrun_resume: found completed serving in serving')

        # Check order runs by order run id
        self._check_order_run_info_by_ori(new_kitchen, orderrun_id_error, 'SERVING_RERAN')
        self._check_order_run_info_by_ori(new_kitchen, orderrun_id_success, 'COMPLETED_SERVING')

        # cleanup
        os.chdir(orig_dir)
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])

    def test_wait_for_serving_states(self):
        # setup
        parent_kitchen = 'CLI-Top'
        recipe_name = 'parallel-recipe-test'
        variation_name = self._get_run_variation_for_recipe(recipe_name)
        new_kitchen = 'test_scenario_orderrun_stop-CLI'
        new_kitchen = self._add_my_guid(new_kitchen)
        runner = CliRunner()
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])
        sleep(BaseTestCloud.SLEEP_TIME)
        result = runner.invoke(dk, ['kitchen-create', '--parent', parent_kitchen, new_kitchen])
        self.assertEqual(0, result.exit_code, result.output)

        # start order & order run
        print('Starting Create-Order in test_wait_for_serving_states()')
        result = runner.invoke(
            dk, [
                'order-run', '--kitchen', new_kitchen, '--recipe', recipe_name, '--yes',
                variation_name
            ]
        )
        self.assertEqual(0, result.exit_code, result.output)

        # wait for state "ACTIVE_SERVING"
        # not going to try for "PLANNED_SERVING" because that may go by too fast
        found_active_serving = False
        wait_loop = WaitLoop()

        while wait_loop:
            resp1 = runner.invoke(dk, ['orderrun-info', '-k', new_kitchen, '--runstatus'])
            if resp1.output is not None:
                self.assertFalse('Current context is:' in resp1.output)
                print('got %s' % resp1.output)
                if "ACTIVE_SERVING" in resp1.output or "COMPLETED_SERVING" in resp1.output:
                    found_active_serving = True
                    break

        self.assertTrue(found_active_serving)
        print('test_wait_for_serving_states: found_active_serving is True')

        # wait for state "COMPLETED_SERVING"
        found_completed_serving = False
        wait_loop = WaitLoop()

        while wait_loop:
            resp2 = runner.invoke(dk, ['orderrun-info', '-k', new_kitchen, '--runstatus'])
            if resp2.output is not None:
                self.assertFalse('Current context is:' in resp2.output)
                print('got %s' % resp2.output)
                if "COMPLETED_SERVING" in resp2.output:
                    found_completed_serving = True
                    break
        self.assertTrue(found_completed_serving)
        print('test_wait_for_serving_states: found_completed_serving is True')

        # Get order id
        resp3 = runner.invoke(dk, ['orderrun-info', '-k', new_kitchen])
        text = 'Order Run ID:'
        index = resp3.output.find(text)
        index += len(text)
        text2 = 'Status:'
        index2 = resp3.output.find(text2)
        orderrun_id = resp3.output[index:index2].strip('/n').strip()

        # Full dk ori -at command check
        self._check_order_run_info_all_things(
            new_kitchen, recipe=recipe_name, variation=variation_name, status='COMPLETED_SERVING'
        )

        # Check full logs
        self._check_order_run_info_by_ori_full_logs(
            new_kitchen,
            orderrun_id,
            recipe=recipe_name,
            variation=variation_name,
            status='COMPLETED_SERVING'
        )

        # cleanup
        runner.invoke(dk, ['kitchen-delete', new_kitchen, '--yes'])

    # ---------------------------------------------- helper nethods -------------------------------
    def _check_order_run_info_by_ori(self, kitchen, orderrun_id, expected_status):
        runner = CliRunner()
        result = runner.invoke(dk, ['orderrun-info', '-k', kitchen, '-ori', orderrun_id])
        self.assertEqual(0, result.exit_code, result.output)

        splitted_output = result.output.split('\n')
        index = 0
        stage = 1
        while index < len(splitted_output):
            if stage == 1:
                if 'ORDER RUN SUMMARY' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 2:
                if 'Order ID:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 3:
                if 'Order Run ID:' in splitted_output[index
                                                      ] and orderrun_id in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            if stage == 4:
                if 'Status:' in splitted_output[index] and expected_status in splitted_output[
                        index]:  # noqa: E501
                    stage += 1
                index += 1
                continue
            if stage == 5:
                if 'Run duration:' in splitted_output[index]:
                    stage += 1
                index += 1
                continue
            index += 1
        self.assertEqual(6, stage)

    def _check_order_run_info_by_ori_full_logs(
            self, kitchen, order_run_id, recipe=None, variation=None, status=None, order_id=None
    ):
        runner = CliRunner()
        result = runner.invoke(dk, ['orderrun-info', '-k', kitchen, '-ori', order_run_id, '-fl'])
        self.assertEqual(0, result.exit_code, result.output)

        current_year = datetime.datetime.now().year

        conditions = [
            'ORDER RUN SUMMARY',
            'Order ID:\t%s' % (order_id if order_id is not None else ''),
            'Order Run ID:\t%s' % (order_run_id if order_run_id is not None else ''),
            'Status:\t\t%s' % (status if status is not None else ''),
            'Kitchen:\t%s' % kitchen,
            'Recipe:\t\t%s' % (recipe if recipe is not None else ''),
            'Variation:\t%s' % (variation if variation is not None else ''),
            'Start time:\t%s-' % current_year, 'Run duration:\t0:', 'FULL LOG',
            'DKCommandServer: starting',
            'DKCommandServer in kitchen: %s' % kitchen, 'Set node',
            'Set Serving(%s) Status (%s)' % (order_run_id, status), 'Ending variation make thread'
        ]

        for condition in conditions:
            msg = "Missing condition in order run summary: {}".format(condition)
            self.assertTrue(condition in result.output, msg)

    def _check_order_run_info_all_things(
            self, kitchen, recipe=None, variation=None, status=None, order_id=None,
            order_run_id=None
    ):
        runner = CliRunner()
        # After the order run is marked as finished, there may be still sending some last pending
        # logs, so wait a bit to ensure it completely finishes
        sleep(5)
        result = runner.invoke(dk, ['orderrun-info', '-k', kitchen, '-at'])
        self.assertEqual(0, result.exit_code, result.output)

        current_year = datetime.datetime.now().year

        conditions = [
            'ORDER RUN SUMMARY',
            'Order ID:\t%s' % (order_id if order_id is not None else ''),
            'Order Run ID:\t%s' % (order_run_id if order_run_id is not None else ''),
            'Status:\t\t%s' % (status if status is not None else ''),
            'Kitchen:\t%s' % kitchen,
            'Recipe:\t\t%s' % (recipe if recipe is not None else ''),
            'Variation:\t%s' % (variation if variation is not None else ''),
            'Start time:\t%s-' % current_year, 'Run duration:\t0:', 'TEST RESULTS', 'Tests: Failed',
            'Tests: Warning', 'Tests: Log', 'Tests: Passed', 'TIMING RESULTS',
            'DKRecipe timing (parallel-recipe-test), status = DKNodeStatus_completed_production',
            'total recipe execution time|0:',
            'Node (node9), status = DKNodeStatus_completed_production, timing is||0:0',
            '(node9) Notebook elapsed time is|0:0', 'STEP STATUS',
            'node1\tDKNodeStatus_completed_production', 'node2\tDKNodeStatus_completed_production',
            'node3\tDKNodeStatus_completed_production', 'node4\tDKNodeStatus_completed_production',
            'node5\tDKNodeStatus_completed_production', 'node6\tDKNodeStatus_completed_production',
            'node7\tDKNodeStatus_completed_production', 'node8\tDKNodeStatus_completed_production',
            'node9\tDKNodeStatus_completed_production', 'LOG',
            'Log Format:\t\tdatetime | record_type | thread_name | message',
            ' | INFO | MainThread | DKCommandServer: starting',
            ' | INFO | MainThread | DKCommandServer in kitchen: %s' % kitchen,
            ' | INFO | NodeThread:node1 | Set node',
            ' | INFO | VariationThread | Ending variation make thread'
        ]

        for condition in conditions:
            msg = "Missing condition in order run summary: {}".format(condition)
            self.assertTrue(condition in result.output, msg)


if __name__ == '__main__':
    unittest.main()
