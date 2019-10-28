from p4_ctl.commands import Command


class TableUpdateCommand(Command):

    def __init__(self, table_update):
        Command.__init__(self)
        self.table_update = table_update

    def execute(self):
        self.table_update.table_update()