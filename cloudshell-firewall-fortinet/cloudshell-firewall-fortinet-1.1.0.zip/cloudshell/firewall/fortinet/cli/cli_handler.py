from logging import Logger

from cloudshell.cli.cli_service_impl import CliServiceImpl
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.devices.cli_handler_impl import CliHandlerImpl

from cloudshell.firewall.fortinet.cli.command_modes import EnableCommandMode, \
    ConfigConsoleCommandMode


class FortiNetCliHandler(CliHandlerImpl):

    def __init__(self, cli, resource_config, logger, api):
        super(FortiNetCliHandler, self).__init__(cli, resource_config, logger, api)
        self.modes = CommandModeHelper.create_command_mode()

    @property
    def enable_mode(self):
        return self.modes[EnableCommandMode]

    default_mode = enable_mode
    config_mode = enable_mode

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs

        :param cloudshell.cli.session.expect_session.ExpectSession session:
        :param Logger logger:
        """

        cli_service = CliServiceImpl(session, self.enable_mode, logger)
        with cli_service.enter_mode(self.modes[ConfigConsoleCommandMode]) as config_session:
            config_session.send_command('set output standard')
