# -*- coding: utf-8 -*-
from os import path
from sys import exit as sys_exit
from sys import argv as sys_argv
from drummer.utils.fio import load_class
from clips import ArgParser

COMMAND_PATH = 'drummer/commands'

BANNER = """
    ____
   / __ \_______  ______ ___  ____ ___  ___  _____
  / / / / ___/ / / / __ `__ \/ __ `__ \/ _ \/ ___/
 / /_/ / /  / /_/ / / / / / / / / / / /  __/ /
/_____/_/   \__,_/_/ /_/ /_/_/ /_/ /_/\___/_/

"""

class Drummer:
    """Implementation of drummer CLI.

    This class provides the command line application for user commands.

    Attributes:
        config: Dict with environment configuration.
    """

    def __init__(self, config):
        self.config = config

    def process(self, sys_argv):
        """Parses user input and calls the proper command."""

        if len(sys_argv)==1:
            print('Command missing. See -h for usage.')
            sys_exit()

        console = ArgParser('drummer-cli', banner=BANNER, title_fg='orange',
            text_fg='green')

        # sections and commands
        console.add_section('System')
        cmd_00 = console.add_command('service:start',
            help='Start drummer service')

        console.add_section('Tasks')
        cmd_01 = console.add_command('task:list', help='List available tasks')
        cmd_02 = console.add_command('task:exec', help='Execute a task')
        cmd_02.add_argument('-v', '--verbosity', help='Set output verbosity',
            valued=True, default='2')
        cmd_03 = console.add_command('task:update', help='Update task list')

        console.add_section('Jobs')
        cmd_04 = console.add_command('job:list', help='List available jobs')
        cmd_05 = console.add_command('job:add', help='Add a new job')
        cmd_06 = console.add_command('job:remove', help='Remove a job')
        cmd_06.add_argument('job_id', help='ID of job to remove')
        cmd_07 = console.add_command('job:enable', help='Enable a job')
        cmd_07.add_argument('job_id', help='ID of job to enable')
        cmd_08 = console.add_command('job:disable', help='Disable a job')
        cmd_08.add_argument('job_id', help='ID of job to disable')
        cmd_09 = console.add_command('job:exec',
            help='Execute immediately a job')
        cmd_09.add_argument('job_id', help='ID of job to execute')
        cmd_10 = console.add_command('job:get',
            help='Get information about a job')
        cmd_10.add_argument('job_id', help='ID of job to display')

        console.add_section('Utils')
        cmd_11 = console.add_command('sched:import',
            help='Import job schedulation from yaml')
        cmd_11.add_argument('--filename', valued=True, help='YAML file')
        cmd_12 = console.add_command('sched:export',
            help='Export job schedulation to yaml')
        cmd_12.add_argument('--filename', valued=True, help='YAML file')

        args = console.parse_args(sys_argv[1:])

        if args['service:start']:
            classname = 'ServiceStart'
        elif args['task:list']:
            classname = 'TaskList'
        elif args['task:exec']:
            classname = 'TaskExec'
        elif args['task:update']:
            classname = 'TaskUpdate'
        elif args['job:list']:
            classname = 'JobList'
        elif args['job:add']:
            classname = 'JobAdd'
        elif args['job:remove']:
            classname = 'JobRemove'
        elif args['job:enable']:
            classname = 'JobEnable'
        elif args['job:disable']:
            classname = 'JobDisable'
        elif args['job:exec']:
            classname = 'JobExec'
        elif args['job:get']:
            classname = 'JobGet'
        elif args['sched:import']:
            classname = 'SchedImport'
        elif args['sched:export']:
            classname = 'SchedExport'
        else:
            sys_exit()

        # load and execute command
        Command = load_class(COMMAND_PATH, classname, relative=True)
        Command(self.config).execute(args)
