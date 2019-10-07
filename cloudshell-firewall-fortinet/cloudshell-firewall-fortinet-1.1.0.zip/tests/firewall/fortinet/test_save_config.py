from mock import patch, MagicMock

from cloudshell.firewall.fortinet.runners.configuration_runner import FortiNetConfigurationRunner
from tests.firewall.fortinet.base_test import BaseFortiNetTestCase, CliEmulator, Command, \
    ENABLE_PROMPT


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', MagicMock(return_value=''))
class TestSaveConfig(BaseFortiNetTestCase):

    def _setUp(self, attrs=None):
        super(TestSaveConfig, self)._setUp(attrs)
        self.runner = FortiNetConfigurationRunner(
            self.logger, self.resource_config, self.api, self.cli_handler)

    def setUp(self):
        self._setUp({
            'Backup Location': '',
            'Backup Type': FortiNetConfigurationRunner.DEFAULT_FILE_SYSTEM,
        })

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_anonymous(self, send_mock, recv_mock):
        host = '192.168.122.10'
        ftp_path = 'ftp://{}'.format(host)
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                '^execute backup config ftp FortiNet-{}-\d+-\d+ {}$'.format(
                    configuration_type, host),
                'Please wait...\n'
                '\n'
                'Connect to ftp server 192.168.122.10 ...\n'
                '\n'
                'Send config file to ftp server OK.\n'
                '\n'
                '{}'.format(ENABLE_PROMPT),
                regexp=True,
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.save(ftp_path, configuration_type)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_ftp(self, send_mock, recv_mock):
        user = 'user'
        password = 'password'
        host = '192.168.122.10'
        ftp_server = 'ftp://{}:{}@{}'.format(user, password, host)
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute backup config ftp FortiNet-{}-\d+-\d+ {} {} {}'.format(
                    configuration_type, host, user, password),
                'Please wait...\n'
                '\n'
                'Connect to ftp server 192.168.122.10 ...\n'
                '\n'
                'Send config file to ftp server OK.\n'
                '\n'
                '{}'.format(ENABLE_PROMPT),
                regexp=True
            )
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.save(ftp_server, configuration_type)

        emu.check_calls()

    def test_save_startup(self):
        ftp_server = 'ftp://user:password@192.168.122.10'
        configuration_type = 'startup'

        self.assertRaisesRegexp(
            Exception,
            'The device doesn\'t support startup configuration',
            self.runner.save,
            ftp_server,
            configuration_type,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_fail_to_save(self, send_mock, recv_mock):
        host = '192.168.122.10'
        ftp_path = 'ftp://{}'.format(host)
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute backup config ftp FortiNet-{}-\d+-\d+ {}'.format(configuration_type, host),
                'Connect to ftp server 192.168.122.10 ...\n'
                'Send config file to ftp server via vdom root failed.\n'
                'Command fail. Return code 4'
                '{}'.format(ENABLE_PROMPT),
                regexp=True,
            )
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            Exception,
            'Session returned \'Fail to backup config\'',
            self.runner.save,
            ftp_path,
            configuration_type,
        )

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_to_device(self, send_mock, recv_mock):
        path = ''
        configuration_type = 'running'

        emu = CliEmulator([
            Command(
                'execute backup config flash FortiNet-{}-\d+-\d+'.format(configuration_type),
                'Please wait...\n'
                'Config backed up to flash disk done.\n'
                '\n'
                '{}'.format(ENABLE_PROMPT),
                regexp=True,
            )
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.save(path, configuration_type)

        emu.check_calls()
