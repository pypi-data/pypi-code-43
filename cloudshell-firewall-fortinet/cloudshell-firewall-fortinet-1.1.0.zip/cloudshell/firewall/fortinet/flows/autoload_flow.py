from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow

from cloudshell.firewall.fortinet.autoload.snmp_autoload import SNMPAutoload


class FortiNetSnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snmp_service:
            snmp_autoload = SNMPAutoload(
                snmp_service, shell_name, shell_type, resource_name, self._logger)
            return snmp_autoload.discover(supported_os)
