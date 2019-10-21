import ast
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


class TestKitchens(DKCommonUnitTestSettings):
    # ----------------------- setup and teardown --------------------------------------------------
    def setUp(self):
        self.temp_dir = None
        if DKPathHelper.is_windows_os():
            TestKitchens._TEMP_FILE_LOCATION = 'c:\\temp'
        else:
            TestKitchens._TEMP_FILE_LOCATION = '/var/tmp'

    def tearDown(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ----------------------- tests ---------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_kitchen_config(self, backend, dkcloudapi_login):
        # Config
        kitchen = 'my-kitchen'

        mock_response_kitchen_config_new = {
            u'status': u'success',
            u'_hid': u'5a2c5f30-0f5e-11e9-9555-0242ac110002',
            u'kitchen-staff': [u'staff1', u'staff2'],
            u'recipeoverrides': {
                u'samples_s3_config': {
                    u's3-secret-key': u'vault://s3_schema/s3-secret-key',
                    u's3-access-key': u'vault://s3_schema/s3-access-key',
                    u'bucket': u'data-kitchen-io',
                    u'rolekey': u'myrole'
                },
                u'pass_the_resume_recipe': u'true',
                u'mssqlhostname': u'myhost',
                u'mssqlport': u'1433',
                u'alex_override2': u'value2',
                u'alex_override': u'value1',
                u'mssqlusername': u'unittester',
                u'email_errors': u'emai@datakitchen.com',
                u'alex_override4': u'value 4',
                u'alex_override3': u'value3',
                u'email_alerts': u'email@datakitchen.com',
                u'redshiftschema': u'alex_schema',
                u'alex_override5': u'value 5',
                u'mssqlpassword': u'#{vault://mssql/password}'
            },
            u'parent-kitchen': u'master',
            u'recipes': [u'my-recipe1', u'my-recipe2'],
            u'description': u'testing_kitchen',
            u'_name': u'DKKitchen',
            u'mesos-constraint': False,
            u'restrict-recipes': False,
            u'wizard-status': {},
            u'mesos-group': None,
            u'name': u'testing_kitchen'
        }

        mock_response_kitchen_config_old = {
            u'status': u'success',
            u'_hid': u'5a2c5f30-0f5e-11e9-9555-0242ac110002',
            u'kitchen-staff': [u'staff1', u'staff2'],
            u'recipeoverrides': [{
                u'category': u'test context',
                u'variable': u'mssqlhostname',
                u'value': u'myhost'
            }, {
                u'category': u'test context',
                u'variable': u'pass_the_resume_recipe',
                u'value': u'true'
            }],
            u'parent-kitchen': u'master',
            u'recipes': [u'my-recipe1', u'my-recipe2'],
            u'description': u'testing_kitchen',
            u'_name': u'DKKitchen',
            u'mesos-constraint': False,
            u'restrict-recipes': False,
            u'wizard-status': {},
            u'mesos-group': None,
            u'name': u'testing_kitchen'
        }

        # Test New syntax - get
        with patch.object(requests, 'get', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_kitchen_config_new)):
            runner = CliRunner()
            result = runner.invoke(
                dk, ["kitchen-config", "--kitchen", kitchen, "-g", "test_override"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('none' in result.output)

        # Test New syntax - get
        with patch.object(requests, 'get', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_kitchen_config_new)):
            runner = CliRunner()
            result = runner.invoke(
                dk, ["kitchen-config", "--kitchen", kitchen, "-g", "mssqlhostname"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('myhost' in result.output)

        # Test New syntax - get
        with patch.object(requests, 'get', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_kitchen_config_new)):
            runner = CliRunner()
            result = runner.invoke(
                dk, ["kitchen-config", "--kitchen", kitchen, "-g", "samples_s3_config"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        expected = {
            u's3-secret-key': u'vault://s3_schema/s3-secret-key',
            u's3-access-key': u'vault://s3_schema/s3-access-key',
            u'bucket': u'data-kitchen-io',
            u'rolekey': u'myrole'
        }
        self.assertDictEqual(ast.literal_eval(result.output.split('\n')[1]), expected)

        # Test New syntax - list all
        with patch.object(requests, 'get', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_kitchen_config_new)):
            runner = CliRunner()
            result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "-la"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue("mssqlhostname                  myhost" in result.output)
        self.assertTrue("mssqlport                      1433" in result.output)
        self.assertTrue("alex_override                  value1" in result.output)
        self.assertTrue("email_errors                   emai@datakitchen.com" in result.output)
        self.assertTrue("redshiftschema                 alex_schema" in result.output)
        self.assertTrue("alex_override4                 value 4" in result.output)
        self.assertTrue("pass_the_resume_recipe         true" in result.output)
        self.assertTrue("alex_override3                 value3" in result.output)
        self.assertTrue("alex_override2                 value2" in result.output)
        self.assertTrue("mssqlusername                  unittester" in result.output)
        self.assertTrue("alex_override5                 value 5" in result.output)
        self.assertTrue("email_alerts                   email@datakitchen.com" in result.output)
        self.assertTrue("mssqlpassword                  #{vault://mssql/password}" in result.output)

        observed_samples_s3_config_dict = None
        expected_samples_s3_config_dict = {
            u's3-secret-key': u'vault://s3_schema/s3-secret-key',
            u's3-access-key': u'vault://s3_schema/s3-access-key',
            u'bucket': u'data-kitchen-io',
            u'rolekey': u'myrole'
        }
        for line in result.output.split('\n'):
            if line.lstrip().startswith('samples_s3_config'):
                samples_s3_config_string = line.split('samples_s3_config')[1].lstrip()
                observed_samples_s3_config_dict = ast.literal_eval(samples_s3_config_string)
                self.assertDictEqual(
                    observed_samples_s3_config_dict, expected_samples_s3_config_dict
                )
                break
        error_msg = "samples_s3_config not present in result output"
        self.assertIsNotNone(observed_samples_s3_config_dict, msg=error_msg)

        # Test Old syntax - get
        with patch.object(requests, 'get', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_kitchen_config_old)):
            runner = CliRunner()
            result = runner.invoke(
                dk, ["kitchen-config", "--kitchen", kitchen, "-g", "mssqlhostname"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('myhost' in result.output)

        # Test Old syntax - list all
        with patch.object(requests, 'get', return_value=MockBackendResponse(
                status_code=200, response_dict=mock_response_kitchen_config_old)):
            runner = CliRunner()
            result = runner.invoke(dk, ["kitchen-config", "--kitchen", kitchen, "-la"])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue('mssqlhostname                  myhost' in result.output)
        self.assertTrue('pass_the_resume_recipe         true' in result.output)
