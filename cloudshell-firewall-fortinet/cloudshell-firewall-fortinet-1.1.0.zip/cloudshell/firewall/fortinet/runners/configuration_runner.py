from cloudshell.devices.runners.configuration_runner import ConfigurationRunner

from cloudshell.firewall.fortinet.flows.restore_flow import FortiNetRestoreFlow
from cloudshell.firewall.fortinet.flows.save_flow import FortiNetSaveFlow


class FortiNetConfigurationRunner(ConfigurationRunner):

    @property
    def restore_flow(self):
        return FortiNetRestoreFlow(self.cli_handler, self._logger)

    @property
    def save_flow(self):
        return FortiNetSaveFlow(self.cli_handler, self._logger)

    @property
    def file_system(self):
        return 'flash'
