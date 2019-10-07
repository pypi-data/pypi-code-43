from mock import patch, MagicMock

from cloudshell.firewall.fortinet.helpers.exceptions import FortiNetException
from cloudshell.firewall.fortinet.runners.configuration_runner import FortiNetConfigurationRunner
from tests.firewall.fortinet.base_test import BaseFortiNetTestCase, CliEmulator, Command, \
    ENABLE_PROMPT


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', MagicMock(return_value=''))
class TestRestoreConfig(BaseFortiNetTestCase):

    def _setUp(self, attrs=None):
        super(TestRestoreConfig, self)._setUp(attrs)
        self.runner = FortiNetConfigurationRunner(
            self.logger, self.resource_config, self.api, self.cli_handler)

    def setUp(self):
        self._setUp({
            'Backup Location': 'Test-running-081018-215424',
            'Backup Type': FortiNetConfigurationRunner.DEFAULT_FILE_SYSTEM,
        })

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_restore_anonymous(self, send_mock, recv_mock):
        host = '192.168.122.10'
        file_name = 'Test-running-100418-163658'
        remote_path = 'ftp://{}/{}'.format(host, file_name)
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute restore config ftp {} {}'.format(file_name, host),
                'This operation will overwrite the current setting and could possibly '
                'reboot the system!\n'
                'Do you want to continue? (y/n)'
            ),
            Command(
                'y',
                '\n'
                'Please wait...\n'
                'Connect to ftp server 192.168.42.102 ...\n'
                'Get config file from ftp server OK.\n'
                'File check OK.\n'
                '{}'.format(ENABLE_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.restore(remote_path, configuration_type)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_restore_ftp(self, send_mock, recv_mock):
        host = '192.168.122.10'
        file_name = 'Test-running-100418-163658'
        user = 'user'
        password = 'password'
        remote_path = 'ftp://{}:{}@{}/{}'.format(user, password, host, file_name)
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute restore config ftp {} {} {} {}'.format(file_name, host, user, password),
                'This operation will overwrite the current setting and could possibly '
                'reboot the system!\n'
                'Do you want to continue? (y/n)'
            ),
            Command(
                'y',
                '\n'
                'Please wait...\n'
                'Connect to ftp server 192.168.42.102 ...\n'
                'Get config file from ftp server OK.\n'
                'File check OK.\n'
                '{}'.format(ENABLE_PROMPT),
            )
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.restore(remote_path, configuration_type)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_fail_to_restore(self, send_mock, recv_mock):
        host = '192.168.122.10'
        file_name = 'Test-running-100418-163658'
        remote_path = 'ftp://{}/{}'.format(host, file_name)
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute restore config ftp {} {}'.format(file_name, host),
                'This operation will overwrite the current setting and could possibly '
                'reboot the system!\n'
                'Do you want to continue? (y/n)'
            ),
            Command(
                'y',
                '\n'
                'Please wait...\n'
                'Connect to ftp server 192.168.122.240 ...\n'
                'Can not get config file from ftp server via vdom root. Err code: 5.\n'
                'Command fail. Return code -28\n'
                '\n'
                '{}'.format(ENABLE_PROMPT),
            )
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            Exception,
            'Session returned \'Fail to restore config\'',
            self.runner.restore,
            remote_path,
            configuration_type,
        )

        emu.check_calls()

    def test_append_method(self):
        remote_path = 'ftp://user:password@192.168.122.10/Test-running-100418-163658'
        configuration_type = 'running'
        restore_method = 'append'

        self.assertRaisesRegexp(
            FortiNetException,
            'The device doesn\'t support append restore method',
            self.runner.restore,
            remote_path,
            configuration_type,
            restore_method,
        )

    def test_restore_startup(self):
        remote_path = 'ftp://user:password@192.168.122.10/Test-startup-100418-163658'
        configuration_type = 'startup'

        self.assertRaisesRegexp(
            FortiNetException,
            'The device doesn\'t support startup configuration',
            self.runner.restore,
            remote_path,
            configuration_type,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_restore_from_device(self, send_mock, recv_mock):
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute revision list config',
                'Last Firmware Version: V0.0.0-build000-REL0\n'
                'ID TIME                   ADMIN                	FIRMWARE VERSION     	COMMENT\n'
                ' 4 2018-10-08 11:54:28    admin                	V6.0.0-build163-REL0 	Test-running-081018-215424\n'
                ' 6 2018-10-08 12:33:47    admin                	V6.0.0-build163-REL0 	Test-running-081018-223342\n'
                '{}'.format(ENABLE_PROMPT),
            ),
            Command(
                'execute restore config flash 4',
                'This operation will overwrite the current setting and could possibly '
                'reboot the system!\n'
                'Do you want to continue? (y/n)'
            ),
            Command(
                'y',
                '\n'
                'Please wait...\n'
                'Get config from local disk OK.\n'
                'File check OK.\n'
                '{}'.format(ENABLE_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.restore('', configuration_type)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_restore_from_device_not_exists_config(self, send_mock, recv_mock):
        path = 'flash://Test-running-081018-215425'
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute revision list config',
                'Last Firmware Version: V0.0.0-build000-REL0\n'
                'ID TIME                   ADMIN                	FIRMWARE VERSION     	COMMENT\n'
                ' 4 2018-10-08 11:54:28    admin                	V6.0.0-build163-REL0 	Test-running-081018-215424\n'
                ' 6 2018-10-08 12:33:47    admin                	V6.0.0-build163-REL0 	Test-running-081018-223342\n'
                '{}'.format(ENABLE_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            FortiNetException,
            'Cannot find config file ".*?" on the device',
            self.runner.restore,
            path,
            configuration_type,
        )

        emu.check_calls()
