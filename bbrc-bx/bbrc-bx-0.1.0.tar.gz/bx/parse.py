import pandas as pd
import json
import os.path as op
import os
import tempfile
import argparse
import pkgutil
import inspect
from datetime import datetime
from tqdm import tqdm

from .validation import validation_scores
from .download import *
from .dicom import *


def __get_modules__(m):
    modules = []
    prefix = m.__name__ + '.'
    log.info('prefix : %s'%prefix)
    for importer, modname, ispkg in pkgutil.iter_modules(m.__path__, prefix):
        module = __import__(modname , fromlist='dummy')
        if not ispkg:
            modules.append(module)
        else:
            modules.extend(__get_modules__(module))
    return modules

def __find_all_commands__(m):
    ''' Browses bx and looks for any class named as a Command'''
    modules = []
    classes = []
    modules = __get_modules__(m)
    forbidden_classes = [] #Test, ScanTest, ExperimentTest]
    for m in modules:
        for name, obj in inspect.getmembers(m):
            if inspect.isclass(obj) and 'Command' in name \
                    and not obj in forbidden_classes:
                classes.append(obj)
    return classes

class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            msg = "readable_dir:{0} is not a valid path".format(prospective_dir)
            raise argparse.ArgumentTypeError(msg)
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            msg = "readable_dir:{0} is not a readable dir".format(prospective_dir)
            raise argparse.ArgumentTypeError(msg)

def check_xnat_item(a, x):
    projects = [e.label() for e in list(x.select.projects())]
    experiments = []
    for p in projects:
        exp = x.array.experiments(project_id=p).data
        experiments.extend([e['ID'] for e in exp])

    if a in projects:
        log.info('Project detected: %s'%a)
        return 0
    elif a in experiments:
        log.info('Experiment detected: %s'%a)
        return 1
    else:
        log.error('%s is not a project/experiment'%a)
        return -1


def download_experiments(x, id, resource_name, validation_report, destdir,
         overwrite=False, test=False):
    t = check_xnat_item(id, x)

    max_rows = 1 if test else None

    experiments = []
    if t == 1:
        experiments = [id]

    elif t == 0:
        for e in x.array.experiments(project_id=id,
                columns=['label']).data[:max_rows]:
            experiments.append(e['ID'])

    log.info('Now initiating download for %s experiments.'%len(experiments))
    for e in tqdm(experiments):
        log.debug(e)
        download_experiment(x, e, resource_name, validation_report,
            overwrite, destdir)


def download_measurements(x, func, id=None, test=False, **kwargs):

    t = check_xnat_item(id, x)
    max_rows = 25 if test else None

    experiments = []
    if t == 1:
        experiments = x.array.experiments(experiment_id=id,
            columns=['label', 'subject_label']).data

    elif t == 0:
        experiments = []
        for e in x.array.experiments(project_id=id,
                columns=['label', 'subject_label']).data[:max_rows]:
            experiments.append(e)
    else:
        print('%s is not a project or an experiment'%t)

    return func(x, experiments, **kwargs)



def parse(parser, command, test=False):
    c = command(parser.command, parser.args, parser.xnat, parser.destdir, parser.overwrite)

    if len(c.args) == 0:
        msg = 'display help message for %s'%command
        log.info(msg)

    elif len(c.args) == command.nargs:
        c.parse(test=test)

    else:
        msg = 'missing argument(s)'
        log.info(msg)



class Command(object):
    def __init__(self, command, args, xnat_instance, destdir, overwrite):
        self.command = command
        self.args = args
        self.xnat = xnat_instance
        self.destdir = destdir
        self.overwrite = overwrite

    def run_id(self, id, func, test=False, **kwargs):
        from bx import parse
        t = parse.check_xnat_item(id, self.xnat)

        max_rows = 1 if test else None
        columns = ['label', 'subject_label']
        experiments = []
        if t == 1:
            experiments = self.xnat.array.experiments(experiment_id=id,
                    columns=columns).data

        elif t == 0:
            for e in self.xnat.array.experiments(project_id=id,
                    columns=columns).data[:max_rows]:
                experiments.append(e)

        return func(self.xnat, experiments, **kwargs)

    def to_excel(self, id, df):
        dt = datetime.today().strftime('%Y%m%d_%H%M%S')
        fn = 'bx_%s_%s_%s.xlsx'%(self.command, id, dt)
        fp = op.join(self.destdir, fn)
        log.info('Saving it in %s'%fp)
        df.to_excel(fp)

def parse_args(command, args, x, destdir=tempfile.gettempdir(), overwrite=False,
        test=False):

    parser = Command(command, args, x, destdir, overwrite=overwrite)

    import bx
    commands = __find_all_commands__(bx)
    commands = {e.__name__.split('.')[-1].lower()[:-7]: e for e in commands}

    if command in commands.keys():
        log.debug('Command: %s'%command)
        if command == 'freesurfer6_hires':
            command = 'freesurfer6'
        parse(parser, commands[command], test=test)

    else:
        msg = '%s not found (valid commands: %s)'%(command, commands)
        log.info(msg)
        raise Exception(msg)


def create_parser():
    import argparse
    cfgfile = op.join(op.expanduser('~'), '.xnat.cfg')
    parser = argparse.ArgumentParser(description='bx')
    parser.add_argument('command', help='BX command')
    parser.add_argument('args', help='BX command', nargs="*")
    parser.add_argument('--config', help='XNAT configuration file',
        required=False, default=cfgfile)
    parser.add_argument('--dest', help='Destination folder',
        required=False, action=readable_dir)
    parser.add_argument('--verbose', '-V', action='store_true', default=False,
        help='Display verbosal information (optional)', required=False)
    parser.add_argument('--overwrite', '-O', action='store_true', default=False,
        help='Overwrite', required=False)
    return parser
