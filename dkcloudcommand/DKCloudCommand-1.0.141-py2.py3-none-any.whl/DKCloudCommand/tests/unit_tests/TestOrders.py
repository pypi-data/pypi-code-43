import requests
import shutil

from click.testing import CliRunner
from mock import patch

from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.cli.__main__ import Backend
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCloudCommand.modules.DKPathHelper import DKPathHelper
from DKCloudCommand.tests.DKCommonUnitTestSettings import DKCommonUnitTestSettings
from DKCloudCommand.tests.DKCommonUnitTestSettings import MockBackendResponse


class TestOrders(DKCommonUnitTestSettings):
    FULL_LOG = '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'  # noqa: E501

    # ----------------------- setup and teardown --------------------------------
    def setUp(self):
        self.temp_dir = None
        if DKPathHelper.is_windows_os():
            TestOrders._TEMP_FILE_LOCATION = 'c:\\temp'
        else:
            TestOrders._TEMP_FILE_LOCATION = '/var/tmp'

    def tearDown(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ----------------------- order run -----------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_order_run_full_log(self, backend, dkcloudapi_login):
        # Config
        kitchen = 'my-kitchen'
        order_run_id = 'my-order-run-id'
        order_id = 'my-order-id'

        mock_response_order_details = {
            'status':
                'success',
            'servings': [{
                'hid': order_run_id,
                'variation_name': 'variation-test',
                'summary': {
                    'status': 'DKNodeStatus_completed_production',
                    'end-time': 1541433704725,
                    'start-time': 1541433695489,
                    'name': 'parallel-recipe-test'
                },
                'status': 'COMPLETED_SERVING',
                'order_id': order_id
            }],
            'orders': [{
                'hid': order_id,
                'schedule': 'now',
                'recipes': ['11b1db2c-e114-11e8-a272-0800273d3b01']
            }]
        }

        mock_response_full_logs = {'status': 'success', 'log': TestOrders.FULL_LOG}

        # Test
        with patch.object(requests, 'post', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_order_details)):
            with patch.object(requests, 'get', return_value=MockBackendResponse(
                    status_code=200, response_dict=mock_response_full_logs)):
                runner = CliRunner()
                result = runner.invoke(
                    dk, ['orderrun-info', '-k', kitchen, '-ori', order_run_id, '-fl']
                )

        # Assertions
        self.assertEqual(0, result.exit_code, result.output)

        status = 'COMPLETED_SERVING'
        variation = 'variation-test'
        recipe = 'parallel-recipe-test'
        assertions = list()
        assertions.append('ORDER RUN SUMMARY',)
        assertions.append('Order Run ID:\t%s' % (order_run_id if order_run_id is not None else ''))
        assertions.append('Status:\t\t%s' % (status if status is not None else ''))
        assertions.append('Kitchen:\t%s' % kitchen)
        assertions.append('Recipe:\t\t%s' % (recipe if recipe is not None else ''))
        assertions.append('Variation:\t%s' % (variation if variation is not None else ''))
        assertions.append('Start time:\t2018-')
        assertions.append('FULL LOG')
        assertions.append('DKCommandServer: starting')
        assertions.append('DKCommandServer in kitchen: test_scenario_orderrun_stop-CLI_ut_807e6180')
        assertions.append('Set node in production')
        assertions.append('Set Serving(04eff20c-e114-11e8-a272-0800273d3b01) Status (%s)' % status)
        assertions.append('Ending variation make thread')
        self.assert_response(assertions, result.output)

    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_order_run_log_threshold(self, backend, dkcloudapi_login):
        # Config
        kitchen = 'my-kitchen'
        order_run_id = 'my-order-run-id'
        order_id = 'my-order-id'

        mock_response_order_details = {
            'status':
                'success',
            'servings': [{
                'hid': order_run_id,
                'variation_name': 'variation-test',
                'summary': {
                    'status': 'DKNodeStatus_completed_production',
                    'end-time': 1541433704725,
                    'start-time': 1541433695489,
                    'name': 'parallel-recipe-test'
                },
                'status': 'COMPLETED_SERVING',
                'order_id': order_id,
                'log': {
                    'count':
                        5,
                    'start':
                        0,
                    'lines': [{
                        'record_type': 'INFO',
                        'message': 'My INFO log',
                        'thread_name': 'MainThread',
                        'traceback': None,
                        'pid': 59,
                        'disk_total': '40284.31 MB',
                        'exc_desc': None,
                        'datetime': '2018-11-09 15:18:14.006686',
                        'exc_formatted': '',
                        'disk_free': '25299.49 MB',
                        'replace_secrets': False,
                        'mem_usage': '56.51 MB',
                        'disk_used': '13289.60 MB',
                        'exc_type': None
                    }, {
                        'record_type': 'ERROR',
                        'message': 'My ERROR log',
                        'thread_name': 'MainThread',
                        'traceback': None,
                        'pid': 59,
                        'disk_total': '40284.31 MB',
                        'exc_desc': None,
                        'datetime': '2018-11-09 15:18:14.006686',
                        'exc_formatted': '',
                        'disk_free': '25299.49 MB',
                        'replace_secrets': False,
                        'mem_usage': '56.51 MB',
                        'disk_used': '13289.60 MB',
                        'exc_type': None
                    }, {
                        'record_type': 'DEBUG',
                        'message': 'My DEBUG log',
                        'thread_name': 'MainThread',
                        'traceback': None,
                        'pid': 59,
                        'disk_total': '40284.31 MB',
                        'exc_desc': None,
                        'datetime': '2018-11-09 15:18:14.006686',
                        'exc_formatted': '',
                        'disk_free': '25299.49 MB',
                        'replace_secrets': False,
                        'mem_usage': '56.51 MB',
                        'disk_used': '13289.60 MB',
                        'exc_type': None
                    }, {
                        'record_type': 'TRACE',
                        'message': 'My TRACE log',
                        'thread_name': 'MainThread',
                        'traceback': None,
                        'pid': 59,
                        'disk_total': '40284.31 MB',
                        'exc_desc': None,
                        'datetime': '2018-11-09 15:18:14.006686',
                        'exc_formatted': '',
                        'disk_free': '25299.49 MB',
                        'replace_secrets': False,
                        'mem_usage': '56.51 MB',
                        'disk_used': '13289.60 MB',
                        'exc_type': None
                    }, {
                        'record_type': 'INFO',
                        'message': 'My second INFO log',
                        'thread_name': 'MainThread',
                        'traceback': None,
                        'pid': 59,
                        'disk_total': '40284.31 MB',
                        'exc_desc': None,
                        'datetime': '2018-11-09 15:18:14.006686',
                        'exc_formatted': '',
                        'disk_free': '25299.49 MB',
                        'replace_secrets': False,
                        'mem_usage': '56.51 MB',
                        'disk_used': '13289.60 MB',
                        'exc_type': None
                    }]
                }
            }],
            'orders': [{
                'hid': order_id,
                'schedule': 'now',
                'recipes': ['11b1db2c-e114-11e8-a272-0800273d3b01']
            }]
        }

        # Test
        with patch.object(requests, 'post', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_order_details)):
            runner = CliRunner()
            result_log_level_error = runner.invoke(
                dk, ['orderrun-info', '-k', kitchen, '-l', '-lt', 'ERROR']
            )
            result_log_level_info = runner.invoke(
                dk, ['orderrun-info', '-k', kitchen, '-l', '-lt', 'INFO']
            )
            result_log_level_debug = runner.invoke(
                dk, ['orderrun-info', '-k', kitchen, '-l', '-lt', 'DEBUG']
            )
            result_log_level_trace = runner.invoke(
                dk, ['orderrun-info', '-k', kitchen, '-l', '-lt', 'TRACE']
            )
            result_log_level_default = runner.invoke(dk, ['orderrun-info', '-k', kitchen, '-l'])

        # Assertions
        self.assertEqual(0, result_log_level_error.exit_code, result_log_level_error.output)
        self.assertEqual(0, result_log_level_info.exit_code, result_log_level_info.output)
        self.assertEqual(0, result_log_level_debug.exit_code, result_log_level_debug.output)
        self.assertEqual(0, result_log_level_trace.exit_code, result_log_level_trace.output)
        self.assertEqual(0, result_log_level_default.exit_code, result_log_level_default.output)

        # TRACE
        self.assertTrue('My ERROR log' in result_log_level_trace.output)
        self.assertTrue('My INFO log' in result_log_level_trace.output)
        self.assertTrue('My second INFO log' in result_log_level_trace.output)
        self.assertTrue('My DEBUG log' in result_log_level_trace.output)
        self.assertTrue('My TRACE log' in result_log_level_trace.output)

        # DEBUG
        self.assertTrue('My ERROR log' in result_log_level_debug.output)
        self.assertTrue('My INFO log' in result_log_level_debug.output)
        self.assertTrue('My second INFO log' in result_log_level_debug.output)
        self.assertTrue('My DEBUG log' in result_log_level_debug.output)
        self.assertTrue('My TRACE log' not in result_log_level_debug.output)

        # INFO
        self.assertTrue('My ERROR log' in result_log_level_info.output)
        self.assertTrue('My INFO log' in result_log_level_info.output)
        self.assertTrue('My second INFO log' in result_log_level_info.output)
        self.assertTrue('My DEBUG log' not in result_log_level_info.output)
        self.assertTrue('My TRACE log' not in result_log_level_info.output)

        # DEFAULT
        self.assertTrue('My ERROR log' in result_log_level_default.output)
        self.assertTrue('My INFO log' in result_log_level_default.output)
        self.assertTrue('My second INFO log' in result_log_level_default.output)
        self.assertTrue('My DEBUG log' not in result_log_level_default.output)
        self.assertTrue('My TRACE log' not in result_log_level_default.output)

        # ERROR
        self.assertTrue('My ERROR log' in result_log_level_error.output)
        self.assertTrue('My INFO log' not in result_log_level_error.output)
        self.assertTrue('My second INFO log' not in result_log_level_error.output)
        self.assertTrue('My DEBUG log' not in result_log_level_error.output)
        self.assertTrue('My TRACE log' not in result_log_level_error.output)
