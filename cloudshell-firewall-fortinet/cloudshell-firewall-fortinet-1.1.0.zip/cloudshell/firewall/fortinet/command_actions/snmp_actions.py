import itertools
import re

from cloudshell.firewall.fortinet.cli.command_modes import EditCommunityCommandMode, \
    EditSnmpHostsCommandCommandMode, ConfigSnmpV2CommandMode, ConfigSnmpSysInfoCommandMode, \
    EditSnmpUserCommandMode, ConfigSnmpV3CommandMode
from cloudshell.firewall.fortinet.command_actions.base import BaseCommandAction
from cloudshell.firewall.fortinet.command_templates import snmp_templates


class SnmpActions(BaseCommandAction):
    def enable_server(self):
        with self.enter_command_mode(ConfigSnmpSysInfoCommandMode):
            self.execute_command(snmp_templates.SET_STATUS_ENABLE)


class SnmpV2Actions(SnmpActions):
    def __init__(self, cli_service, logger, command_modes, community):
        super(SnmpV2Actions, self).__init__(cli_service, logger, command_modes)
        self.__config = None
        self.community = community

    def get_config(self, force=False):
        if force or self.__config is None:
            self.__config = self.execute_command(snmp_templates.SHOW_V2_CONF)
        return self.__config

    def is_enabled(self):
        conf = self.get_config(force=True)
        return re.search(r'set name "{}"'.format(self.community), conf) is not None

    def get_free_id(self, start_id=100):
        conf = self.get_config()
        used_ids = map(int, re.findall(r'edit (\d+)', conf))

        for id_ in itertools.count(start_id):
            if id_ not in used_ids:
                return id_

    def enable_snmp(self):
        """Setup community"""

        community_id = self.get_free_id()
        edit_community_mode = EditCommunityCommandMode(community_id)
        edit_snmp_hosts_mode = EditSnmpHostsCommandCommandMode(1)

        with self.enter_command_mode(edit_community_mode):
            self.execute_command(snmp_templates.SET_COMMUNITY_NAME, community=self.community)
            self.execute_command(snmp_templates.SET_STATUS_ENABLE)
            self.execute_command(snmp_templates.SET_V2C_STATUS_ENABLE)

            with self.enter_command_mode(edit_snmp_hosts_mode):
                pass  # just creating new index

    def get_community_id(self):
        config = self.get_config()
        match = re.search(r'edit (\d+)\n\s+set name "{}"'.format(self.community), config)

        if match:
            return int(match.group(1))

    def disable_snmp(self):
        community_id = self.get_community_id()

        with self.enter_command_mode(ConfigSnmpV2CommandMode):
            self.execute_command(snmp_templates.DELETE_SNMP_COMMUNITY, community_id=community_id)


class SnmpV3Actions(SnmpActions):
    def __init__(self, cli_service, logger, command_modes, user, auth_type, priv_type, password,
                 priv_key):

        super(SnmpV3Actions, self).__init__(cli_service, logger, command_modes)

        self.user = user
        self.auth_type = self.get_auth_type(auth_type)
        self.priv_type = self.get_priv_type(priv_type)
        self.password = password
        self.priv_key = priv_key

    @staticmethod
    def get_auth_type(auth_type):
        return {
            'MD5': 'md5',
            'SHA': 'sha',
        }.get(auth_type, False)

    @staticmethod
    def get_priv_type(priv_type):
        return {
            'No Privacy Protocol': False,
            'DES': 'des',
            'AES-128': 'aes',
            'AES-256': 'aes256'
        }[priv_type]

    @property
    def security_level(self):
        return {
            (True, False): 'auth-no-priv',
            (True, True): 'auth-priv',
        }.get((bool(self.auth_type), bool(self.priv_type)), False)

    def get_config(self):
        return self.execute_command(snmp_templates.SHOW_V3_CONF)

    def is_enabled(self):
        conf = self.get_config()

        return re.search(r'edit "{}"'.format(self.user), conf) is not None

    def enable_snmp(self):
        edit_snmp_user_mode = EditSnmpUserCommandMode(self.user)

        with self.enter_command_mode(edit_snmp_user_mode):
            self.execute_command(snmp_templates.SET_STATUS_ENABLE)

            if self.security_level:
                self.execute_command(
                    snmp_templates.SET_SECURITY_LEVEL, security_level=self.security_level)
                self.execute_command(snmp_templates.SET_AUTH_PROTO, auth_type=self.auth_type)
                self.execute_command(snmp_templates.SET_AUTH_PWD, password=self.password)

                if self.security_level == 'auth-priv':
                    self.execute_command(snmp_templates.SET_PRIV_PROTO, priv_type=self.priv_type)
                    self.execute_command(snmp_templates.SET_PRIV_PWD, priv_key=self.priv_key)

    def disable_snmp(self):
        with self.enter_command_mode(ConfigSnmpV3CommandMode):
            self.execute_command(snmp_templates.DELETE_SNMP_USER, user=self.user)
