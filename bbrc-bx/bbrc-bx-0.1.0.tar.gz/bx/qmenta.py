from bx.parse import Command


class QMENTACommand(Command):
    nargs = 2

    def __init__(self, *args, **kwargs):
        super(QMENTACommand, self).__init__(*args, **kwargs)

    def parse(self, test=False):
        args = self.args
        command = self.command
        subcommand = args[0]
        id = args[1]

        if subcommand == 'files':

            resource_name = 'QMENTA_RESULTS'
            validation_report = 'QMENTA'

            from bx import parse
            parse.download_experiments(self.xnat, id, resource_name,
                validation_report, self.destdir, self.overwrite,
                test=test)
