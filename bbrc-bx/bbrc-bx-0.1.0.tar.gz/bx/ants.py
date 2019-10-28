from bx.parse import Command

class ANTSCommand(Command):
    nargs = 2

    def __init__(self, *args, **kwargs):
        super(ANTSCommand, self).__init__(*args, **kwargs)

    def parse(self, test=False):
        
        subcommand = self.args[0]
        id = self.args[1] #should be a project or an experiment_id

        report_only = subcommand == 'report'
        resource_name = 'ANTS'
        validation_report = 'ANTSValidator'
        if report_only:
            resource_name = None

        from bx import download
        download.download_experiments(self.xnat, id, resource_name,
            validation_report, self.dest_dir, self.overwrite,
            test=test)
