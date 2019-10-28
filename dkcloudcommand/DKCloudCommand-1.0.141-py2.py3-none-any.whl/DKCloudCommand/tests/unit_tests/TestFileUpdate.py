from mock import patch
from click.testing import CliRunner

from DKCloudCommand.cli.__main__ import dk
from DKCloudCommand.cli.__main__ import Backend
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCloudCommand.tests.DKCommonUnitTestSettings import DKCommonUnitTestSettings


class TestFileUpdate(DKCommonUnitTestSettings):

    # ----------------------- tests ------------------------------------------------------------------------------
    @patch.object(DKCloudAPI, 'login', return_value='FAKE_TOKEN')
    @patch.object(Backend, 'check_version', return_value=True)
    def testfile_update_error(self, backend, dkcloudapi_login):
        runner = CliRunner()
        commands = list()
        commands.append(["file-update", "-m", "my changes", "file2.txt,", "file1.txt"])
        commands.append(["file-update", "-m", "my changes", "'file2.txt',", "file1.txt"])
        commands.append(["file-update", "-m", "my changes", "file2.txt;", "file1.txt"])
        commands.append(["file-update", "-m", "my changes", "'file2.txt';", "file1.txt"])
        commands.append(["file-update", "-m", "my changes", "file2.txt,file1.txt"])
        commands.append(["file-update", "-m", "my changes", "file2.txt;file1.txt"])
        commands.append(["file-update", "-m", "my changes", "file2.txt:file1.txt"])
        for command in commands:
            result = runner.invoke(dk, command)
            self.assertEqual(1, result.exit_code, result.output)
            self.assertTrue(
                'Error: Files to be updated must be delimited by whitespace ' in result.output
            )
