import logging as log
from datetime import datetime
import os.path as op
from bx.parse import Command


class MRDatesCommand(Command):
    nargs = 1

    def __init__(self, *args, **kwargs):
        super(MRDatesCommand, self).__init__(*args, **kwargs)

    def parse(self, test=False):
        id = self.args[0] #should be a project or an experiment_id
        from bx import parse
        t = parse.check_xnat_item(id, self.xnat)

        if t == 0:
            log.debug('Project detected: %s'%id)

            from bx.dicom import collect_mrdates
            df = collect_mrdates(self.xnat, id=id, test=test)
            if self.destdir == None:
                self.destdir = tempfile.gettempdir()
            self.to_excel(id, df)

        elif t == 1:
            log.debug('Experiment detected: %s'%id)
            from bx.dicom import collect_mrdates
            sd = collect_mrdates(self.xnat, id=id)
            print(sd)
            log.info('Scan date: %s'%sd)

        else:
            log.error('No project/experiment found: %s'%id)
