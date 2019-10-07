from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor


class BaseCommandAction(object):

    def __init__(self, cli_service, logger, command_modes):
        """Enable Disable Snmp actions

        :param cloudshell.cli.cli_service.CliService cli_service: enable mode cli service
        :param logging.Logger logger:
        :param dict command_modes: dict with cls: instance of the CommandModes
        """

        self._cli_service = cli_service
        self._logger = logger
        self.command_modes = command_modes

    def execute_command(self, command_template, **kwargs):
        return CommandTemplateExecutor(
            self._cli_service,
            command_template,
        ).execute_command(**kwargs)

    def enter_command_mode(self, command_mode):
        if isinstance(command_mode, type):  # if it's a class not instance
            command_mode = self.command_modes[command_mode]

        return self._cli_service.enter_mode(command_mode)
