from p4_ctl.commands import Command


class TableDumpCommand(Command):

    def __init__(self, table_dump):
        Command.__init__(self)
        self.table_dump = table_dump

    def execute(self):
        self.table_dump.table_dump()