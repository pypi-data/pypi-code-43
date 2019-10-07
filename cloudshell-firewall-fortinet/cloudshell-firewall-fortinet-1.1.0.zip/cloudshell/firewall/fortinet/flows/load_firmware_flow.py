from cloudshell.devices.flows.action_flows import LoadFirmwareFlow

from cloudshell.firewall.fortinet.command_actions.system_actions import SystemActions


class FortiNetLoadFirmwareFlow(LoadFirmwareFlow):

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param str path: The path to the firmware file, including the firmware file name
        :param str vrf: Virtual Routing and Forwarding Name
        :param int timeout:
        """

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as config_session:
            system_action = SystemActions(config_session, self._logger, self._cli_handler.modes)
            system_action.load_firmware(path)
