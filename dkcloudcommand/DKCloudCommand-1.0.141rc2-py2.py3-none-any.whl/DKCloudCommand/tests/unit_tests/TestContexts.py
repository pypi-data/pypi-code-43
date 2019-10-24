import shutil

from mock import patch
from click.testing import CliRunner

from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.cli.__main__ import Backend
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCloudCommand.modules.DKPathHelper import DKPathHelper
from DKCloudCommand.tests.DKCommonUnitTestSettings import DKCommonUnitTestSettings


class TestContexts(DKCommonUnitTestSettings):

    # ----------------------- setup and teardown -----------------------------------------------------------------------
    def setUp(self):
        self.temp_dir = None
        if DKPathHelper.is_windows_os():
            TestContexts._TEMP_FILE_LOCATION = 'c:\\temp'
        else:
            TestContexts._TEMP_FILE_LOCATION = '/var/tmp'

    def tearDown(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ----------------------- tests -----------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def test_context_switch_with_wrong_case(self, backend, dkcloudapi_login):
        # Test
        runner = CliRunner()
        result = runner.invoke(dk, ["context-switch", "deFault"])

        # Assertions
        self.assertEqual(1, result.exit_code, result.output)
        assertions = list()
        assertions.append('Error: You probably meant context: default')
        self.assert_response(assertions, result.output)
