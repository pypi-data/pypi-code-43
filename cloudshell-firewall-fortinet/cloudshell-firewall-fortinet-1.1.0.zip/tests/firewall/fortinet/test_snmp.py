from mock import patch, MagicMock

from cloudshell.firewall.fortinet.helpers.exceptions import FortiNetException
from cloudshell.firewall.fortinet.runners.autoload_runner import FortiNetAutoloadRunner
from cloudshell.firewall.fortinet.snmp.snmp_handler import FortiNetSnmpHandler
from tests.firewall.fortinet.base_test import BaseFortiNetTestCase, CliEmulator, Command, \
    CONFIG_SNMP_V2_PROMPT, ENABLE_PROMPT, CONFIG_SNMP_SYSINFO_PROMPT, EDIT_COMMUNITY_PROMPT, \
    CONFIG_SNMP_HOSTS_PROMPT, EDIT_SNMP_HOSTS_PROMPT, CONFIG_SNMP_V3_PROMPT, EDIT_SNMP_USER_PROMPT


@patch('cloudshell.devices.snmp_handler.QualiSnmp', MagicMock())
@patch('cloudshell.firewall.fortinet.flows.autoload_flow.SNMPAutoload', MagicMock())
@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', MagicMock(return_value=''))
class TestEnableDisableSnmp(BaseFortiNetTestCase):

    def _setUp(self, attrs=None):
        attrs = attrs or {}
        snmp_attrs = {
            'SNMP Version': 'v2c',
            'SNMP Read Community': 'public',
            'SNMP V3 User': 'quali_user',
            'SNMP V3 Password': 'password',
            'SNMP V3 Private Key': 'private_key',
            'SNMP V3 Authentication Protocol': 'No Authentication Protocol',
            'SNMP V3 Privacy Protocol': 'No Privacy Protocol',
            'Enable SNMP': 'True',
            'Disable SNMP': 'False',
        }
        snmp_attrs.update(attrs)
        super(TestEnableDisableSnmp, self)._setUp(snmp_attrs)
        self.snmp_handler = FortiNetSnmpHandler(
            self.resource_config, self.logger, self.api, self.cli_handler)
        self.runner = FortiNetAutoloadRunner(self.resource_config, self.logger, self.snmp_handler)

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v2(self, send_mock, recv_mock):
        self._setUp()

        emu = CliEmulator([
            Command(
                'show system snmp community',
                'config system snmp community\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp sysinfo', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('set status enable', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command('config system snmp community', CONFIG_SNMP_V2_PROMPT),
            Command('edit 100', EDIT_COMMUNITY_PROMPT),
            Command('set name public', EDIT_COMMUNITY_PROMPT),
            Command('set status enable', EDIT_COMMUNITY_PROMPT),
            Command('set query-v2c-status enable', EDIT_COMMUNITY_PROMPT),
            Command('config hosts', CONFIG_SNMP_HOSTS_PROMPT),
            Command('edit 1', EDIT_SNMP_HOSTS_PROMPT),
            Command('end', EDIT_COMMUNITY_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp community',
                'config system snmp community\n'
                '    edit 100\n'
                '        set name "public"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v2_already_enabled(self, send_mock, recv_mock):
        self._setUp()

        emu = CliEmulator([
            Command(
                'show system snmp community',
                'config system snmp community\n'
                '    edit 100\n'
                '        set name "public"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v2_community_index_is_used(self, send_mock, recv_mock):
        edit_community_prompt = EDIT_COMMUNITY_PROMPT.replace('100', '101')
        self._setUp()

        emu = CliEmulator([
            Command(
                'show system snmp community',
                '    edit 100\n'
                '        set name "other_community"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                'config system snmp community\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp sysinfo', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('set status enable', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command('config system snmp community', CONFIG_SNMP_V2_PROMPT),
            Command('edit 101', edit_community_prompt),
            Command('set name public', edit_community_prompt),
            Command('set status enable', edit_community_prompt),
            Command('set query-v2c-status enable', edit_community_prompt),
            Command('config hosts', CONFIG_SNMP_HOSTS_PROMPT),
            Command('edit 1', EDIT_SNMP_HOSTS_PROMPT),
            Command('end', edit_community_prompt),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp community',
                'config system snmp community\n'
                '    edit 100\n'
                '        set name "other_community"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                '    edit 101\n'
                '        set name "public"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v2_not_enabled(self, send_mock, recv_mock):
        self._setUp()

        emu = CliEmulator([
            Command(
                'show system snmp community',
                'config system snmp community\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp sysinfo', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('set status enable', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command('config system snmp community', CONFIG_SNMP_V2_PROMPT),
            Command('edit 100', EDIT_COMMUNITY_PROMPT),
            Command('set name public', EDIT_COMMUNITY_PROMPT),
            Command('set status enable', EDIT_COMMUNITY_PROMPT),
            Command('set query-v2c-status enable', EDIT_COMMUNITY_PROMPT),
            Command('config hosts', CONFIG_SNMP_HOSTS_PROMPT),
            Command('edit 1', EDIT_SNMP_HOSTS_PROMPT),
            Command('end', EDIT_COMMUNITY_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp community',
                'config system snmp community\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            FortiNetException,
            'Failed to create SNMP community "public"',
            self.runner.discover,
        )

        emu.check_calls()

    def test_enable_snmp_v2_write_community(self):
        self._setUp({'SNMP Write Community': 'private'})

        self.assertRaisesRegexp(
            FortiNetException,
            '^FortiNet devices doesn\'t support write communities$',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_disable_snmp_v2(self, send_mock, recv_mock):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command(
                'show system snmp community',
                'config system snmp community\n'
                '    edit 100\n'
                '        set name "public"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp community', CONFIG_SNMP_V2_PROMPT),
            Command('delete 100', CONFIG_SNMP_V2_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp community',
                'config system snmp community\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_disable_snmp_v2_already_disabled(self, send_mock, recv_mock):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command(
                'show system snmp community',
                'config system snmp community\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_disable_snmp_v2_is_not_disabled(self, send_mock, recv_mock):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command(
                'show system snmp community',
                'config system snmp community\n'
                '    edit 100\n'
                '        set name "public"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp community', CONFIG_SNMP_V2_PROMPT),
            Command('delete 100', CONFIG_SNMP_V2_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp community',
                'config system snmp community\n'
                '    edit 100\n'
                '        set name "public"\n'
                '        config hosts\n'
                '            edit 1\n'
                '            next\n'
                '        end\n'
                '    next\n'
                'end'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            FortiNetException,
            'Failed to remove SNMP community "public"',
            self.runner.discover,
        )

        emu.check_calls()

    def test_disable_snmp_v2_write_community(self):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
            'SNMP Write Community': 'private',
        })

        self.assertRaisesRegexp(
            FortiNetException,
            '^FortiNet devices doesn\'t support write communities$',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v3(self, send_mock, recv_mock):
        self._setUp({'SNMP Version': 'v3'})

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp sysinfo', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('set status enable', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command('config system snmp user', CONFIG_SNMP_V3_PROMPT),
            Command('edit quali_user', EDIT_SNMP_USER_PROMPT),
            Command('set status enable', EDIT_SNMP_USER_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp user',
                'config system snmp user\n'
                '    edit "quali_user"\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_snmp_v3_user_already_created(self, send_mock, recv_mock):
        self._setUp({'SNMP Version': 'v3'})

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                '    edit "quali_user"\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_snmp_v3_user_didnt_created(self, send_mock, recv_mock):
        self._setUp({'SNMP Version': 'v3'})

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp sysinfo', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('set status enable', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command('config system snmp user', CONFIG_SNMP_V3_PROMPT),
            Command('edit quali_user', EDIT_SNMP_USER_PROMPT),
            Command('set status enable', EDIT_SNMP_USER_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp user',
                'config system snmp user\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            FortiNetException,
            r'^Failed to create SNMP User "quali_user"$',
            self.runner.discover,
        )

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v3_with_auth(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'MD5',
        })

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp sysinfo', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('set status enable', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command('config system snmp user', CONFIG_SNMP_V3_PROMPT),
            Command('edit quali_user', EDIT_SNMP_USER_PROMPT),
            Command('set status enable', EDIT_SNMP_USER_PROMPT),
            Command('set security-level auth-no-priv', EDIT_SNMP_USER_PROMPT),
            Command('set auth-proto md5', EDIT_SNMP_USER_PROMPT),
            Command('set auth-pwd password', EDIT_SNMP_USER_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp user',
                'config system snmp user\n'
                '    edit "quali_user"\n'
                '        set security-level auth-no-priv\n'
                '        set auth-proto md5\n'
                '        set auth-pwd ENC 3iJai3...\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v3_with_auth_and_priv(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-128',
        })

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp sysinfo', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('set status enable', CONFIG_SNMP_SYSINFO_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command('config system snmp user', CONFIG_SNMP_V3_PROMPT),
            Command('edit quali_user', EDIT_SNMP_USER_PROMPT),
            Command('set status enable', EDIT_SNMP_USER_PROMPT),
            Command('set security-level auth-priv', EDIT_SNMP_USER_PROMPT),
            Command('set auth-proto sha', EDIT_SNMP_USER_PROMPT),
            Command('set auth-pwd password', EDIT_SNMP_USER_PROMPT),
            Command('set priv-proto aes', EDIT_SNMP_USER_PROMPT),
            Command('set priv-pwd private_key', EDIT_SNMP_USER_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp user',
                'config system snmp user\n'
                '    edit "quali_user"\n'
                '        set security-level auth-priv\n'
                '        set auth-proto sha\n'
                '        set auth-pwd ENC 142A8NXCPlqD...\n'
                '        set priv-pwd ENC KTmph2yQ...\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    def test_enable_snmp_v3_with_not_supported_priv_protocol(self):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-192',
        })

        self.assertRaisesRegexp(
            FortiNetException,
            'Doen\'t supported private key protocol AES-192',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_disable_snmp_v3(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-128',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                '    edit "quali_user"\n'
                '        set security-level auth-priv\n'
                '        set auth-proto sha\n'
                '        set auth-pwd ENC 142A8NXCPlqD...\n'
                '        set priv-pwd ENC KTmph2yQ...\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp user', CONFIG_SNMP_V3_PROMPT),
            Command('delete quali_user', CONFIG_SNMP_V3_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp user',
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    def test_disable_snmp_v3_with_not_supported_priv_protocol(self):
        self._setUp({
            'SNMP Version': 'v3',
            'SNMP V3 Authentication Protocol': 'SHA',
            'SNMP V3 Privacy Protocol': 'AES-192',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        self.assertRaisesRegexp(
            FortiNetException,
            'Doen\'t supported private key protocol AES-192',
            self.runner.discover,
        )

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_remove_snmp_v3_user_already_deleted(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_snmp_v3_user_didnt_deleted(self, send_mock, recv_mock):
        self._setUp({
            'SNMP Version': 'v3',
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            Command(
                'show system snmp user',
                'config system snmp user\n'
                '    edit "quali_user"\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
            Command('config system snmp user', CONFIG_SNMP_V3_PROMPT),
            Command('delete quali_user', CONFIG_SNMP_V3_PROMPT),
            Command('end', ENABLE_PROMPT),
            Command(
                'show system snmp user',
                'config system snmp user\n'
                '    edit "quali_user"\n'
                '    next\n'
                'end\n'
                '{}'.format(ENABLE_PROMPT)),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            FortiNetException,
            r'^Failed to disable SNMP User "quali_user"$',
            self.runner.discover,
        )

        emu.check_calls()


class TestSnmpAutoload(BaseFortiNetTestCase):
    def _setUp(self, attrs=None):
        attrs = attrs or {}
        snmp_attrs = {
            'SNMP Version': 'v2c',
            'SNMP Read Community': 'public',
            'Enable SNMP': 'False',
            'Disable SNMP': 'False',
        }
        snmp_attrs.update(attrs)
        super(TestSnmpAutoload, self)._setUp(snmp_attrs)
        self.snmp_handler = FortiNetSnmpHandler(
            self.resource_config, self.logger, self.api, self.cli_handler)
        self.runner = FortiNetAutoloadRunner(self.resource_config, self.logger, self.snmp_handler)

    def setUp(self):
        self._setUp()

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_autoload_without_ports_in_ent_table(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysObjectID', 0): 'SNMPv2-SMI::enterprises.12356.101.1.60',
            ('SNMPv2-MIB', 'sysContact', '0'): 'admin',
            ('SNMPv2-MIB', 'sysName', '0'): 'FortiGate-VM64-KVM',
            ('SNMPv2-MIB', 'sysLocation', '0'): 'somewhere',
            ('FORTINET-FORTIGATE-MIB', 'fgSysVersion', 0): 'v6.0.2,build0163,180725 (GA)',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'FORTINET-FORTIGATE-MIB::fgtVM64KVm',
            ('ENTITY-MIB', 'entPhysicalModelName', 1): 'FGT_VM64KVM',
            ('ENTITY-MIB', 'entPhysicalSerialNum', 1): 'FGVMEVBICE74EA11',
            ('ENTITY-MIB', 'entPhysicalModelName', 2): 'FGT_VM64KVM',
            ('ENTITY-MIB', 'entPhysicalSerialNum', 2): 'FGVMEVBICE74EA11',
            # missed ifName for port1, look for it in ifDesc
            ('IF-MIB', 'ifName', 2): '',
            ('IF-MIB', 'ifDesc', 2): 'port1',
            ('IF-MIB', 'ifAlias', 2): '',
            ('IF-MIB', 'ifType', 2): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 2): '52:54:00:e5:48:f5',
            ('IF-MIB', 'ifMtu', 2): '1500',
            ('IF-MIB', 'ifHighSpeed', 2): '10000',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 2): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 2): 'No Such Object currently exists at this OID',
            ('IF-MIB', 'ifName', 3): 'port2',
            ('IF-MIB', 'ifAlias', 3): '',
            ('IF-MIB', 'ifType', 3): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 3): '52:54:00:5c:65:1a',
            ('IF-MIB', 'ifMtu', 3): '1500',
            ('IF-MIB', 'ifHighSpeed', 3): '10000',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 3): "'fullDuplex'",
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 3): 'No Such Object currently exists at this OID',
            ('IF-MIB', 'ifName', 4): 'port3',
            ('IF-MIB', 'ifAlias', 4): '',
            ('IF-MIB', 'ifType', 4): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 4): '52:54:00:66:1f:8d',
            ('IF-MIB', 'ifMtu', 4): '1500',
            ('IF-MIB', 'ifHighSpeed', 4): '10000',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 4): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 4): 'No Such Object currently exists at this OID',
            ('IF-MIB', 'ifName', 6): 'aggr',
            ('IF-MIB', 'ifAlias', 6): '',
        }
        table_map = {
            ('ENTITY-MIB', 'entPhysicalClass'): {
                1: {'entPhysicalClass': "'chassis'", 'suffix': '1'},
                2: {'entPhysicalClass': "'chassis'", 'suffix': '2'},
            },
            ('IF-MIB', 'ifType'): {
                1: {'ifType': "'tunnel'", 'suffix': '1'},
                2: {'ifType': "'ethernetCsmacd'", 'suffix': '2'},
                3: {'ifType': "'ethernetCsmacd'", 'suffix': '3'},
                4: {'ifType': "'ethernetCsmacd'", 'suffix': '4'},
                6: {'ifType': "'ieee8023adLag'", 'suffix': '6'}
            },
            ('IP-MIB', 'ipAdEntIfIndex'): {
                '192.168.122.240':
                    {'ipAdEntIfIndex': '2', 'suffix': '192.168.122.240'},
                '192.168.121.239':
                    {'ipAdEntIfIndex': '6', 'suffix': '192.168.121.239'}
            },
            ('IPV6-MIB', 'ipv6AddrType'): {
                '2.2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d': {'ipv6AddrType': ''},
                '6.2001:0db8:11a3:09d7:1f34:8a2e:07a0:766d': {'ipv6AddrType': ''},
            },
            ('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'): {},
            ('LLDP-MIB', 'lldpRemSysName'): {},
            ('LLDP-MIB', 'lldpLocPortDesc'): {},
        }

        snmp_mock().get_property.side_effect = lambda *args: property_map[args]
        snmp_mock().get_table.side_effect = lambda *args: table_map[args]

        details = self.runner.discover()

        contact_name = sys_name = location = model = os_version = None
        for attr in details.attributes:
            if attr.relative_address == '':
                if attr.attribute_name == 'Contact Name':
                    contact_name = attr.attribute_value
                elif attr.attribute_name == 'System Name':
                    sys_name = attr.attribute_value
                elif attr.attribute_name == 'Location':
                    location = attr.attribute_value
                elif attr.attribute_name == 'Model':
                    model = attr.attribute_value
                elif attr.attribute_name == 'OS Version':
                    os_version = attr.attribute_value

        self.assertEqual('admin', contact_name)
        self.assertEqual('FortiGate-VM64-KVM', sys_name)
        self.assertEqual('somewhere', location)
        self.assertEqual('fgtVM64KVm', model)
        self.assertEqual('v6.0.2,build0163,180725 (GA)', os_version)

        ports = []
        power_ports = []
        port_channels = []
        chassis = []

        for resource in details.resources:
            if resource.model == 'GenericPort':
                ports.append(resource)
            elif resource.model == 'GenericChassis':
                chassis.append(resource)
            elif resource.model == 'GenericPowerPort':
                power_ports.append(resource)
            elif resource.model == 'GenericPortChannel':
                port_channels.append(resource)

        ports.sort(key=lambda p: p.name)
        power_ports.sort(key=lambda pw: pw.name)
        port_channels.sort(key=lambda pc: pc.name)

        self.assertItemsEqual(['Chassis 1', 'Chassis 2'], [ch.name for ch in chassis])
        self.assertItemsEqual(
            ['port1', 'port2', 'port3'], [port.name for port in ports]
        )
        self.assertItemsEqual([], [pw.name for pw in power_ports])
        self.assertItemsEqual(['aggr'], [pc.name for pc in port_channels])

        not_found = object
        ipv4 = ipv6 = not_found
        for attr in details.attributes:
            if attr.relative_address == 'CH1/P2':
                if attr.attribute_name == 'IPv6 Address':
                    ipv6 = attr.attribute_value
                elif attr.attribute_name == 'IPv4 Address':
                    ipv4 = attr.attribute_value
            if not_found not in (ipv4, ipv6):
                break
        else:
            self.fail("Didn't find port CH1/P2")

        self.assertEqual('192.168.122.240', ipv4)
        self.assertEqual('2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d', ipv6)

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_not_supported_os(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysObjectID', 0): 'some another value',
        }
        snmp_mock().get_property.side_effect = lambda *args: property_map[args]

        self.assertRaisesRegexp(
            FortiNetException,
            '^Unsupported device OS$',
            self.runner.discover,
        )

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_adjacent(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysObjectID', 0): 'SNMPv2-SMI::enterprises.12356.101.1.60',
            ('SNMPv2-MIB', 'sysContact', '0'): 'admin',
            ('SNMPv2-MIB', 'sysName', '0'): 'FortiGate-VM64-KVM',
            ('SNMPv2-MIB', 'sysLocation', '0'): 'somewhere',
            ('FORTINET-FORTIGATE-MIB', 'fgSysVersion', 0): 'v6.0.2,build0163,180725 (GA)',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'FORTINET-FORTIGATE-MIB::fgtVM64KVm',
            ('ENTITY-MIB', 'entPhysicalModelName', 1): 'FGT_VM64KVM',
            ('ENTITY-MIB', 'entPhysicalSerialNum', 1): 'FGVMEVBICE74EA11',
            ('IF-MIB', 'ifName', 2): 'port1',
            ('IF-MIB', 'ifAlias', 2): '',
            ('IF-MIB', 'ifType', 2): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 2): '52:54:00:e5:48:f5',
            ('IF-MIB', 'ifMtu', 2): '1500',
            ('IF-MIB', 'ifHighSpeed', 2): '10000',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 2): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 2): 'No Such Object currently exists at this OID',
            ('LLDP-MIB', 'lldpRemPortDesc', '12.50.1.12'): 'Ethernet 12',
        }
        table_map = {
            ('ENTITY-MIB', 'entPhysicalClass'): {
                1: {'entPhysicalClass': "'chassis'", 'suffix': '1'}
            },
            ('IF-MIB', 'ifType'): {
                1: {'ifType': "'tunnel'", 'suffix': '1'},
                2: {'ifType': "'ethernetCsmacd'", 'suffix': '2'},
            },
            ('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'): {},
            ('IP-MIB', 'ipAdEntIfIndex'): {},
            ('IPV6-MIB', 'ipv6AddrType'): {},
            ('LLDP-MIB', 'lldpRemSysName'): {
                '12.50.1.12': {'lldpRemSysName': 'Other_device'}},
            ('LLDP-MIB', 'lldpLocPortDesc'): {
                '50.1': {'lldpLocPortDesc': 'port1'}},
        }

        snmp_mock().get_property.side_effect = lambda *args: property_map[args]
        snmp_mock().get_table.side_effect = lambda *args: table_map[args]

        self.runner.discover()

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_autoload_with_ports_in_ent_table(self, snmp_mock):
        property_map = {
            ('SNMPv2-MIB', 'sysObjectID', 0): 'SNMPv2-SMI::enterprises.12356.101.1.60',
            ('SNMPv2-MIB', 'sysContact', '0'): 'admin',
            ('SNMPv2-MIB', 'sysName', '0'): 'FortiGate-VM64-KVM',
            ('SNMPv2-MIB', 'sysLocation', '0'): 'somewhere',
            ('FORTINET-FORTIGATE-MIB', 'fgSysVersion', 0): 'v6.0.2,build0163,180725 (GA)',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'FORTINET-FORTIGATE-MIB::fgtVM64KVm',
            ('ENTITY-MIB', 'entPhysicalModelName', 1): 'FGT_VM64KVM',
            ('ENTITY-MIB', 'entPhysicalSerialNum', 1): 'FGVMEVBICE74EA11',
            ('ENTITY-MIB', 'entPhysicalName', 2): 'modem',
            ('ENTITY-MIB', 'entPhysicalName', 3): 'port1',
            ('IF-MIB', 'ifAlias', 11): '',
            ('IF-MIB', 'ifType', 11): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 11): '00:09:0f:9a:30:97',
            ('IF-MIB', 'ifMtu', 11): '1500',
            ('IF-MIB', 'ifHighSpeed', 11): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 11): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 11):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 3): '1',
            ('ENTITY-MIB', 'entPhysicalName', 4): 'port2',
            ('IF-MIB', 'ifAlias', 14): '',
            ('IF-MIB', 'ifType', 14): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 14): '00:09:0f:9a:30:98',
            ('IF-MIB', 'ifMtu', 14): '1500',
            ('IF-MIB', 'ifHighSpeed', 14): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 14): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 14):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 4): '1',
            ('ENTITY-MIB', 'entPhysicalName', 5): 'port3',
            ('IF-MIB', 'ifAlias', 15): '',
            ('IF-MIB', 'ifType', 15): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 15): '00:09:0f:9a:30:99',
            ('IF-MIB', 'ifMtu', 15): '1500',
            ('IF-MIB', 'ifHighSpeed', 15): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 15): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 15):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 5): '1',
            ('ENTITY-MIB', 'entPhysicalName', 6): 'port4',
            ('IF-MIB', 'ifAlias', 16): '',
            ('IF-MIB', 'ifType', 16): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 16): '00:09:0f:9a:30:9a',
            ('IF-MIB', 'ifMtu', 16): '1500',
            ('IF-MIB', 'ifHighSpeed', 16): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 16): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 16):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 6): '1',
            ('ENTITY-MIB', 'entPhysicalName', 7): 'port5',
            ('IF-MIB', 'ifAlias', 17): '',
            ('IF-MIB', 'ifType', 17): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 17): '00:09:0f:9a:30:9b',
            ('IF-MIB', 'ifMtu', 17): '1500',
            ('IF-MIB', 'ifHighSpeed', 17): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 17): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 17):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 7): '1',
            ('ENTITY-MIB', 'entPhysicalName', 8): 'port6',
            ('IF-MIB', 'ifAlias', 18): '',
            ('IF-MIB', 'ifType', 18): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 18): '00:09:0f:9a:30:9c',
            ('IF-MIB', 'ifMtu', 18): '1500',
            ('IF-MIB', 'ifHighSpeed', 18): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 18): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 18):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 8): '1',
            ('ENTITY-MIB', 'entPhysicalName', 9): 'port7',
            ('IF-MIB', 'ifAlias', 19): '',
            ('IF-MIB', 'ifType', 19): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 19): '00:09:0f:9a:30:9d',
            ('IF-MIB', 'ifMtu', 19): '1500',
            ('IF-MIB', 'ifHighSpeed', 19): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 19): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 19):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 9): '1',
            ('ENTITY-MIB', 'entPhysicalName', 10): 'port8',
            ('IF-MIB', 'ifAlias', 20): '',
            ('IF-MIB', 'ifType', 20): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 20): '00:09:0f:9a:30:9e',
            ('IF-MIB', 'ifMtu', 20): '1500',
            ('IF-MIB', 'ifHighSpeed', 20): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 20): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 20):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 10): '1',
            ('ENTITY-MIB', 'entPhysicalName', 11): 'port9',
            ('IF-MIB', 'ifAlias', 12): '',
            ('IF-MIB', 'ifType', 12): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 12): '00:09:0f:9a:30:9f',
            ('IF-MIB', 'ifMtu', 12): '1500',
            ('IF-MIB', 'ifHighSpeed', 12): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 12): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 12):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 11): '1',
            ('ENTITY-MIB', 'entPhysicalName', 12): 'port10',
            ('IF-MIB', 'ifAlias', 13): '',
            ('IF-MIB', 'ifType', 13): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 13): '00:09:0f:9a:30:a0',
            ('IF-MIB', 'ifMtu', 13): '1500',
            ('IF-MIB', 'ifHighSpeed', 13): '10',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 13): '',
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 13):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 12): '1',
            ('ENTITY-MIB', 'entPhysicalName', 13): 'port11',
            ('IF-MIB', 'ifAlias', 1): 'TRUNK',
            ('IF-MIB', 'ifType', 1): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 1): '00:09:0f:9a:30:91',
            ('IF-MIB', 'ifMtu', 1): '1500',
            ('IF-MIB', 'ifHighSpeed', 1): '1000',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 1): "'fullDuplex'",
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 1):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 13): '1',
            ('ENTITY-MIB', 'entPhysicalName', 14): 'port12',
            ('IF-MIB', 'ifAlias', 2): 'TRANSITO-CLEAN',
            ('IF-MIB', 'ifType', 2): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 2): '00:09:0f:9a:30:92',
            ('IF-MIB', 'ifMtu', 2): '1500',
            ('IF-MIB', 'ifHighSpeed', 2): '1000',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 2): "'fullDuplex'",
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 2):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 14): '1',
            ('ENTITY-MIB', 'entPhysicalName', 15): 'port13',
            ('IF-MIB', 'ifAlias', 3): '',
            ('IF-MIB', 'ifType', 3): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 3): '00:09:0f:9a:30:93',
            ('IF-MIB', 'ifMtu', 3): '1500',
            ('IF-MIB', 'ifHighSpeed', 3): '0',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 3): "'halfDuplex'",
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 3):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 15): '1',
            ('ENTITY-MIB', 'entPhysicalName', 16): 'port14',
            ('IF-MIB', 'ifAlias', 4): '',
            ('IF-MIB', 'ifType', 4): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 4): '00:09:0f:9a:30:94',
            ('IF-MIB', 'ifMtu', 4): '1500',
            ('IF-MIB', 'ifHighSpeed', 4): '0',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 4): "'halfDuplex'",
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 4):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 16): '1',
            ('ENTITY-MIB', 'entPhysicalName', 17): 'port15',
            ('IF-MIB', 'ifAlias', 5): '',
            ('IF-MIB', 'ifType', 5): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 5): '00:09:0f:9a:30:95',
            ('IF-MIB', 'ifMtu', 5): '1500',
            ('IF-MIB', 'ifHighSpeed', 5): '0',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 5): "'halfDuplex'",
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 5):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 17): '1',
            ('ENTITY-MIB', 'entPhysicalName', 18): 'port16',
            ('IF-MIB', 'ifAlias', 6): '',
            ('IF-MIB', 'ifType', 6): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', 6): '00:09:0f:9a:30:96',
            ('IF-MIB', 'ifMtu', 6): '1500',
            ('IF-MIB', 'ifHighSpeed', 6): '0',
            ('EtherLike-MIB', 'dot3StatsDuplexStatus', 6): "'halfDuplex'",
            ('MAU-MIB', 'ifMauAutoNegAdminStatus', 6):
                'No Such Instance currently exists at this OID',
            ('ENTITY-MIB', 'entPhysicalContainedIn', 18): '1',
        }
        table_map = {
            ('ENTITY-MIB', 'entPhysicalClass'): {
                1: {'entPhysicalClass': "'chassis'", 'suffix': '1'},
                2: {'entPhysicalClass': "'port'", 'suffix': '2'},
                3: {'entPhysicalClass': "'port'", 'suffix': '3'},
                4: {'entPhysicalClass': "'port'", 'suffix': '4'},
                5: {'entPhysicalClass': "'port'", 'suffix': '5'},
                6: {'entPhysicalClass': "'port'", 'suffix': '6'},
                7: {'entPhysicalClass': "'port'", 'suffix': '7'},
                8: {'entPhysicalClass': "'port'", 'suffix': '8'},
                9: {'entPhysicalClass': "'port'", 'suffix': '9'},
                10: {'entPhysicalClass': "'port'", 'suffix': '10'},
                11: {'entPhysicalClass': "'port'", 'suffix': '11'},
                12: {'entPhysicalClass': "'port'", 'suffix': '12'},
                13: {'entPhysicalClass': "'port'", 'suffix': '13'},
                14: {'entPhysicalClass': "'port'", 'suffix': '14'},
                15: {'entPhysicalClass': "'port'", 'suffix': '15'},
                16: {'entPhysicalClass': "'port'", 'suffix': '16'},
                17: {'entPhysicalClass': "'port'", 'suffix': '17'},
                18: {'entPhysicalClass': "'port'", 'suffix': '18'}
            },
            ('IF-MIB', 'ifName'): {
                # port 11 missed name the name is in ifDesc
                1: {'ifName': '', 'suffix': '1'},
                2: {'ifName': 'port12', 'suffix': '2'},
                3: {'ifName': 'port13', 'suffix': '3'},
                4: {'ifName': 'port14', 'suffix': '4'},
                5: {'ifName': 'port15', 'suffix': '5'},
                6: {'ifName': 'port16', 'suffix': '6'},
                7: {'ifName': 'modem', 'suffix': '7'},
                8: {'ifName': 'CR_DC_DIRTY', 'suffix': '8'},
                9: {'ifName': 'CR_DIRTY_MGT', 'suffix': '9'},
                10: {'ifName': 'ssl.root', 'suffix': '10'},
                11: {'ifName': 'port1', 'suffix': '11'},
                12: {'ifName': 'port9', 'suffix': '12'},
                13: {'ifName': 'port10', 'suffix': '13'},
                14: {'ifName': 'port2', 'suffix': '14'},
                15: {'ifName': 'port3', 'suffix': '15'},
                16: {'ifName': 'port4', 'suffix': '16'},
                17: {'ifName': 'port5', 'suffix': '17'},
                18: {'ifName': 'port6', 'suffix': '18'},
                19: {'ifName': 'port7', 'suffix': '19'},
                20: {'ifName': 'port8', 'suffix': '20'},
                21: {'ifName': 'CR_CSHELL_DIRTY', 'suffix': '21'},
                22: {'ifName': 'CR_HITL', 'suffix': '22'},
                23: {'ifName': 'ssl.CSHELL_DIRT', 'suffix': '23'}
            },
            ('IF-MIB', 'ifDesc'): {1: {'ifDesc': 'port11', 'suffix': '1'}},
            ('IP-MIB', 'ipAdEntIfIndex'): {
                '192.168.2.1': {'ipAdEntIfIndex': '2', 'suffix': '192.168.2.1'},
                '192.168.2.2': {'ipAdEntIfIndex': '21', 'suffix': '192.168.2.2'},
                '192.168.2.3': {'ipAdEntIfIndex': '22', 'suffix': '192.168.2.3'},
                '192.168.2.4': {'ipAdEntIfIndex': '8', 'suffix': '192.168.2.4'},
                '192.168.2.5': {'ipAdEntIfIndex': '9', 'suffix': '192.168.2.5'}},
            ('IPV6-MIB', 'ipv6AddrType'): {
                '2.2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d': {'ipv6AddrType': ''},
                '6.2001:0db8:11a3:09d7:1f34:8a2e:07a0:766d': {'ipv6AddrType': ''},
            },
            ('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'): {},
            ('LLDP-MIB', 'lldpRemSysName'): {},
            ('LLDP-MIB', 'lldpLocPortDesc'): {},
            ('IF-MIB', 'ifType'): {},
        }

        snmp_mock().get_property.side_effect = lambda *args: property_map[args]
        snmp_mock().get_table.side_effect = lambda *args: table_map[args]

        details = self.runner.discover()

        contact_name = sys_name = location = model = os_version = None
        for attr in details.attributes:
            if attr.relative_address == '':
                if attr.attribute_name == 'Contact Name':
                    contact_name = attr.attribute_value
                elif attr.attribute_name == 'System Name':
                    sys_name = attr.attribute_value
                elif attr.attribute_name == 'Location':
                    location = attr.attribute_value
                elif attr.attribute_name == 'Model':
                    model = attr.attribute_value
                elif attr.attribute_name == 'OS Version':
                    os_version = attr.attribute_value

        self.assertEqual('admin', contact_name)
        self.assertEqual('FortiGate-VM64-KVM', sys_name)
        self.assertEqual('somewhere', location)
        self.assertEqual('fgtVM64KVm', model)
        self.assertEqual('v6.0.2,build0163,180725 (GA)', os_version)

        ports = []
        power_ports = []
        port_channels = []
        chassis = None

        for resource in details.resources:
            if resource.model == 'GenericPort':
                ports.append(resource)
            elif resource.model == 'GenericChassis':
                chassis = resource
            elif resource.model == 'GenericPowerPort':
                power_ports.append(resource)
            elif resource.model == 'GenericPortChannel':
                port_channels.append(resource)

        ports.sort(key=lambda p: p.name)
        power_ports.sort(key=lambda pw: pw.name)
        port_channels.sort(key=lambda pc: pc.name)

        self.assertEqual('Chassis 1', chassis.name)

        self.assertItemsEqual(
            map('port{}'.format, range(1, 17)),
            [port.name for port in ports]
        )
        self.assertItemsEqual(
            [], [pw.name for pw in power_ports]
        )
        self.assertItemsEqual(
            [], [pc.name for pc in port_channels]
        )

        not_found = object
        ipv4 = ipv6 = not_found
        for attr in details.attributes:
            if attr.relative_address == 'CH1/P14':
                if attr.attribute_name == 'IPv6 Address':
                    ipv6 = attr.attribute_value
                elif attr.attribute_name == 'IPv4 Address':
                    ipv4 = attr.attribute_value
            if not_found not in (ipv4, ipv6):
                break
        else:
            self.fail("Didn't find port CH1/P2")

        self.assertEqual('192.168.2.1', ipv4)
        self.assertEqual('2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d', ipv6)
