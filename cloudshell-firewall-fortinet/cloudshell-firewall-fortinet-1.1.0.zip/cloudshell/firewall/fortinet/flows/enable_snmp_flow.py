from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters,\
    SNMPV2ReadParameters

from cloudshell.firewall.fortinet.command_actions.snmp_actions import SnmpV2Actions, SnmpV3Actions
from cloudshell.firewall.fortinet.helpers.exceptions import FortiNetException


class FortiNetEnableSnmpFlow(EnableSnmpFlow):

    def execute_flow(self, snmp_param):
        if isinstance(snmp_param, SNMPV3Parameters):
            flow = EnableSnmpV3
        else:
            flow = EnableSnmpV2

        flow(self._cli_handler, self._logger, snmp_param).execute()


class EnableSnmpV2(object):

    def __init__(self, cli_handler, logger, snmp_param):
        """Enable SNMP v2

        :param cloudshell.firewall.fortinet.cli.cli_handler.FortiNetCliHandler cli_handler:
        :param logging.Logger logger:
        :param SNMPV2WriteParameters|SNMPV2ReadParameters snmp_param:
        """

        self._cli = cli_handler
        self._logger = logger
        self.snmp_param = snmp_param

    def execute(self):
        if isinstance(self.snmp_param, SNMPV2WriteParameters):
            raise FortiNetException('FortiNet devices doesn\'t support write communities')

        community = self.snmp_param.snmp_community
        self._logger.info('Start creating SNMP community {}'.format(community))

        with self._cli.get_cli_service(self._cli.enable_mode) as cli_service:
            snmp_actions = SnmpV2Actions(cli_service, self._logger, self._cli.modes, community)

            if snmp_actions.is_enabled():
                self._logger.debug('SNMP Community "{}" already configured'.format(community))
                return

            snmp_actions.enable_server()
            snmp_actions.enable_snmp()

            if not snmp_actions.is_enabled():
                msg = 'Failed to create SNMP community "{}"'.format(community)
                self._logger.info(msg)
                raise FortiNetException(msg)

        self._logger.info('SNMP community {} created'.format(community))


class EnableSnmpV3(object):
    SNMP_AUTH_MAP = {v: k for k, v in SNMPV3Parameters.AUTH_PROTOCOL_MAP.items()}
    SNMP_PRIV_MAP = {v: k for k, v in SNMPV3Parameters.PRIV_PROTOCOL_MAP.items()}
    EXCLUDED_PRIV_TYPES = {'AES-192', '3DES-EDE'}

    def __init__(self, cli_handler, logger, snmp_param):
        """Enable SNMP v3

        :param cloudshell.firewall.fortinet.cli.cli_handler.FortiNetCliHandler cli_handler:
        :param logging.Logger logger:
        :param SNMPV3Parameters snmp_param:
        """

        self._cli = cli_handler
        self._logger = logger
        self.snmp_param = snmp_param

    def execute(self):
        auth_type = self.SNMP_AUTH_MAP[self.snmp_param.auth_protocol]
        priv_type = self.SNMP_PRIV_MAP[self.snmp_param.private_key_protocol]
        user = self.snmp_param.snmp_user

        self._logger.info('Start creating SNMP User "{}"'.format(user))

        if priv_type in self.EXCLUDED_PRIV_TYPES:
            raise FortiNetException('Doen\'t supported private key protocol {}'.format(priv_type))

        with self._cli.get_cli_service(self._cli.enable_mode) as cli_service:
            snmp_actions = SnmpV3Actions(
                cli_service,
                self._logger,
                self._cli.modes,
                user,
                auth_type,
                priv_type,
                self.snmp_param.snmp_password,
                self.snmp_param.snmp_private_key,
            )

            if snmp_actions.is_enabled():
                self._logger.debug('SNMP User "{}" already configured'.format(user))
                return

            snmp_actions.enable_server()
            snmp_actions.enable_snmp()

            if not snmp_actions.is_enabled():
                msg = 'Failed to create SNMP User "{}"'.format(user)
                self._logger.info(msg)
                raise FortiNetException(msg)

        self._logger.info('SNMP User {} created'.format(user))
