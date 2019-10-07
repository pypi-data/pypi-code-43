from mock import patch, MagicMock

from cloudshell.firewall.fortinet.runners.firmware_runner import FortiNetFirmwareRunner
from tests.firewall.fortinet.base_test import BaseFortiNetTestCase, CliEmulator, Command, \
    ENABLE_PROMPT


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', MagicMock(return_value=''))
class TestLoadFirmware(BaseFortiNetTestCase):

    def _setUp(self, attrs=None):
        super(TestLoadFirmware, self)._setUp(attrs)
        self.runner = FortiNetFirmwareRunner(self.logger, self.cli_handler)

    def setUp(self):
        self._setUp()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_load_firmware_ftp(self, send_mock, recv_mock):
        host = '192.168.122.10'
        file_name = 'firmware'
        file_path = 'ftp://{}/{}'.format(host, file_name)

        emu = CliEmulator([
            Command(
                'execute restore image ftp {} {}'.format(file_name, host),
                'This operation will replace the current firmware version!\n'
                'Do you want to continue? (y/n)'
            ),
            Command(
                'y',
                'Start updating firmware\n'
                '{}'.format(ENABLE_PROMPT),
            )
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.load_firmware(file_path)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_load_firmware_file_system(self, send_mock, recv_mock):
        revision_id = '2'
        file_path = 'flash://{}'.format(revision_id)

        emu = CliEmulator([
            Command(
                'execute restore image flash {}'.format(revision_id),
                'This operation will replace the current firmware version!\n'
                'Do you want to continue? (y/n)'
            ),
            Command(
                'y',
                'Start updating firmware\n'
                '{}'.format(ENABLE_PROMPT),
            )
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.load_firmware(file_path)

        emu.check_calls()
