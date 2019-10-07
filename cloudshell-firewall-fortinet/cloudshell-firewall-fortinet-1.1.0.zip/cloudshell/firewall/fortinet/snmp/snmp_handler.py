from cloudshell.devices.snmp_handler import SnmpHandler

from cloudshell.firewall.fortinet.flows.disable_snmp_flow import FortiNetDisableSnmpFlow
from cloudshell.firewall.fortinet.flows.enable_snmp_flow import FortiNetEnableSnmpFlow


class FortiNetSnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        super(FortiNetSnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        return FortiNetEnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return FortiNetDisableSnmpFlow(self.cli_handler, self._logger)
