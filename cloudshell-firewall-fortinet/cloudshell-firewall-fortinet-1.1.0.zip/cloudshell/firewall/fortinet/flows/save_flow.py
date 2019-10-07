from cloudshell.devices.flows.action_flows import SaveConfigurationFlow

from cloudshell.firewall.fortinet.command_actions.system_actions import SystemActions
from cloudshell.firewall.fortinet.helpers.exceptions import FortiNetException


class FortiNetSaveFlow(SaveConfigurationFlow):

    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param str folder_path: destination path where file will be saved
        :param str configuration_type: source file, which will be saved running or startup
        :param str vrf_management_name: Virtual Routing and Forwarding Name
        """

        if 'startup' in configuration_type:
            raise FortiNetException('The device doesn\'t support startup configuration')

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            system_action = SystemActions(cli_service, self._logger, self._cli_handler.modes)
            system_action.backup_config(folder_path)
