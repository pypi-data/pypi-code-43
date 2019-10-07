from cloudshell.devices.runners.firmware_runner import FirmwareRunner

from cloudshell.firewall.fortinet.flows.load_firmware_flow import FortiNetLoadFirmwareFlow


class FortiNetFirmwareRunner(FirmwareRunner):
    @property
    def load_firmware_flow(self):
        return FortiNetLoadFirmwareFlow(self.cli_handler, self._logger)
