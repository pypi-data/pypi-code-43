import logging as log
from datetime import datetime
import os.path as op
from bx.parse import Command

class NiftiCommand(Command):
    nargs = 1

    def __init__(self, *args, **kwargs):
        super(NiftiCommand, self).__init__(*args, **kwargs)
        s = input('Enter Sequence Name (i.e. Series Description):')
        self.sequence_name = s

    def parse(self, test=False):
        id = self.args[0]
        self.run_id(id, download_sequence, test=test,
            sequence_name=self.sequence_name, destdir=self.destdir)



def download_sequence(x, experiments, sequence_name, destdir):

    import os, shutil
    from glob import glob
    import tempfile
    from tqdm import tqdm
    columns = ['label', 'subject_label']

    for e in tqdm(experiments):
        log.debug('Experiment %s:'%e['ID'])


        scans = x.select.experiment(e['ID']).scans()
        seq_scans = [s for s in scans if not s.label().startswith('0-') and\
            sequence_name == s.attrs.get('type')]
        log.debug('Found following scans: %s'%seq_scans)

        for s in seq_scans:
            r = s.resource('NIFTI')
            if not r.exists():
                log.error('%s has no NIFTI'%e)
                continue
            wd = tempfile.mkdtemp()

            r.get(dest_dir=wd, extract=True)
            fp = glob(op.join(wd, 'NIFTI', '*.nii.gz'))
            if len(fp) != 1:
                log.error('Multiple files found in archive. Skipping %s (%s) folder: %s'\
                    %(e['ID'], s.label(), op.join(wd, 'NIFTI')))
                continue
            fp = fp[0]
            fn = '%s_%s_%s_%s.nii.gz'%(e['subject_label'], e['label'], s.label(), e['ID'])
            log.debug('Saving %s...'%fn)
            shutil.move(fp, op.join(destdir, fn))
            shutil.rmtree(wd)
