from p4_ctl.commands import Command


class LoadConfigCommand(Command):

    def __init__(self, load_config):
        Command.__init__(self)
        self.load_config = load_config

    def execute(self):
        self.load_config.load_config()