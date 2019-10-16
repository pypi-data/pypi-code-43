import shutil

from click.testing import CliRunner
from mock import patch

from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCloudCommand.modules.DKCloudCommandConfig import DKCloudCommandConfig
from DKCloudCommand.modules.DKPathHelper import DKPathHelper
from DKCloudCommand.tests.DKCommonUnitTestSettings import DKCommonUnitTestSettings


class TestVersionCheck(DKCommonUnitTestSettings):

    # ----------------------- setup and teardown -----------------------------------------------------------------------
    def setUp(self):
        self.temp_dir = None
        if DKPathHelper.is_windows_os():
            TestVersionCheck._TEMP_FILE_LOCATION = 'c:\\temp'
        else:
            TestVersionCheck._TEMP_FILE_LOCATION = '/var/tmp'

    def tearDown(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ------------------------------------ tests -----------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    def test_version_check_ask_to_upgrade(self, dkcloudapi_login):
        # Config
        mock_version = u'200.500.97'

        # Test
        runner = CliRunner()
        with patch.object(DKCloudCommandConfig, 'get_latest_version_from_pip', return_value=mock_version), \
             patch.object(DKCloudCommandConfig, 'is_skip_version_check_present', return_value=False):
            result = runner.invoke(dk, ["xl"])

        # Assertions
        self.assertEqual(1, result.exit_code, result.output)
        assertions = list()
        assertions.append('Warning !!!')
        assertions.append(
            ' Your command line is out of date, new version %s is available. Please update' %
            mock_version
        )
        assertions.append(' Type "pip install DKCloudCommand --upgrade" to upgrade')
        self.assert_response(assertions, result.output)
