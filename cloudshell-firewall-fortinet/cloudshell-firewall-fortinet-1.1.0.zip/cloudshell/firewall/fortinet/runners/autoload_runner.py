from cloudshell.devices.runners.autoload_runner import AutoloadRunner

from cloudshell.firewall.fortinet.flows.autoload_flow import FortiNetSnmpAutoloadFlow


class FortiNetAutoloadRunner(AutoloadRunner):
    def __init__(self, resource_config, logger, snmp_handler):
        super(FortiNetAutoloadRunner, self).__init__(resource_config, logger)
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        return FortiNetSnmpAutoloadFlow(self.snmp_handler, self._logger)
