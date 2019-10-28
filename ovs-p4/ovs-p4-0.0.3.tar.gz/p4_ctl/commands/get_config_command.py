from p4_ctl.commands import Command


class GetConfigCommand(Command):

    def __init__(self, get_config):
        Command.__init__(self)
        self.get_config = get_config

    def execute(self):
        self.get_config.get_config()