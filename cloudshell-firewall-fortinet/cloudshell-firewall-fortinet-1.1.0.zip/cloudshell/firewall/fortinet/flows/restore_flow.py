from cloudshell.devices.flows.action_flows import RestoreConfigurationFlow

from cloudshell.firewall.fortinet.command_actions.system_actions import SystemActions
from cloudshell.firewall.fortinet.helpers.exceptions import FortiNetException


class FortiNetRestoreFlow(RestoreConfigurationFlow):

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name):
        """ Execute flow which restore selected file to the provided destination

        :param str path: the path to the configuration file, including the configuration file name
        :param str restore_method: the restore method to use when restoring the configuration file,
            append and override
        :param str configuration_type: the configuration type to restore, startup or running
        :param str vrf_management_name: Virtual Routing and Forwarding Name
        """

        if 'startup' in configuration_type:
            raise FortiNetException('The device doesn\'t support startup configuration')
        if restore_method == 'append':
            raise FortiNetException('The device doesn\'t support append restore method')

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            system_action = SystemActions(cli_service, self._logger, self._cli_handler.modes)
            system_action.restore_config(path)
