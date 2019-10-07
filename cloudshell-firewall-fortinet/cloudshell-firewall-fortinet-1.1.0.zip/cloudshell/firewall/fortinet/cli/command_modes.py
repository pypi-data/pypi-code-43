from cloudshell.cli.command_mode import CommandMode


BEGIN_OF_LINE = r'(\n|\r|^)'
END_OF_LINE = r'\s*$'


class FortiNetCommandMode(CommandMode):
    PROMPT = ''
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'end'  # exit and save

    def __init__(self):
        super(FortiNetCommandMode, self).__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
        )


class EditSomeIndexCommandMode(FortiNetCommandMode):
    ENTER_COMMAND = 'edit {}'
    ENTER_INTERMEDIATE_COMMAND = None
    PROMPT = r'{}.+? \({}\) #{}'
    INTERMEDIATE_PROMPT = None

    def __init__(self, id_):
        super(EditSomeIndexCommandMode, self).__init__()
        self._enter_command = self.ENTER_INTERMEDIATE_COMMAND
        self._prompt = self.PROMPT.format(BEGIN_OF_LINE, id_, END_OF_LINE)

        enter_command = self.ENTER_COMMAND.format(id_)
        self._enter_action_map = {
            self.INTERMEDIATE_PROMPT:
                lambda session, logger: session.send_line(enter_command, logger),
        }


class EnableCommandMode(FortiNetCommandMode):
    NOT_A_CONF_MODE = r'((?!\(.*?\)).)+?'  # without (some text)
    PROMPT = r'{}{}\s#{}'.format(BEGIN_OF_LINE, NOT_A_CONF_MODE, END_OF_LINE)
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''


class ConfigConsoleCommandMode(FortiNetCommandMode):
    PROMPT = r'{}.+? \(console\) #{}'.format(BEGIN_OF_LINE, END_OF_LINE)
    ENTER_COMMAND = 'config system console'


class ConfigSnmpSysInfoCommandMode(FortiNetCommandMode):
    PROMPT = r'{}.+? \(sysinfo\) #{}'.format(BEGIN_OF_LINE, END_OF_LINE)
    ENTER_COMMAND = 'config system snmp sysinfo'


class ConfigSnmpV2CommandMode(FortiNetCommandMode):
    PROMPT = r'{}.+? \(community\) #{}'.format(BEGIN_OF_LINE, END_OF_LINE)
    ENTER_COMMAND = 'config system snmp community'


class EditCommunityCommandMode(EditSomeIndexCommandMode):
    ENTER_INTERMEDIATE_COMMAND = ConfigSnmpV2CommandMode.ENTER_COMMAND
    INTERMEDIATE_PROMPT = ConfigSnmpV2CommandMode.PROMPT


class EditSnmpHostsCommandCommandMode(EditSomeIndexCommandMode):
    ENTER_INTERMEDIATE_COMMAND = 'config hosts'
    INTERMEDIATE_PROMPT = r'{}.+? \(hosts\) #{}'.format(BEGIN_OF_LINE, END_OF_LINE)


class ConfigSnmpV3CommandMode(FortiNetCommandMode):
    PROMPT = r'{}.+? \(user\) #{}'.format(BEGIN_OF_LINE, END_OF_LINE)
    ENTER_COMMAND = 'config system snmp user'


class EditSnmpUserCommandMode(EditSomeIndexCommandMode):
    ENTER_INTERMEDIATE_COMMAND = ConfigSnmpV3CommandMode.ENTER_COMMAND
    INTERMEDIATE_PROMPT = ConfigSnmpV3CommandMode.PROMPT


CommandMode.RELATIONS_DICT = {
    EnableCommandMode: {
        ConfigConsoleCommandMode: {},
        ConfigSnmpSysInfoCommandMode: {},
        ConfigSnmpV2CommandMode: {},
        ConfigSnmpV3CommandMode: {},
    }
}
