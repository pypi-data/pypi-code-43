# -*- coding: utf-8 -*-
from sys import path as sys_path
from drummer.commands.base import BaseCommand
from drummer.logger import get_logger
from drummer.utils.fio import load_class
from drummer.utils.validation import get_dict_from_args
from drummer.errors import Errors
from prettytable import PrettyTable
import inquirer

class TaskExec(BaseCommand):

    def execute(self, cmd_args):

        config = self.config
        verbosity = cmd_args['--verbosity']

        if verbosity == '0':
            level = 'ERROR'
        elif verbosity == '1':
            level = 'WARNING'
        elif verbosity == '2':
            level = 'INFO'
        elif verbosity == '3':
            level = 'DEBUG'
        else:
            raise ValueError(Errors.E0002)

        logger = get_logger(config, streaming=True, level=level)

        logger.debug('Starting task execution command')

        # add task folder to syspath
        sys_path.append(config['taskdir'])

        # init result table
        result_table = PrettyTable()
        result_table.field_names = ['Response', 'Data']
        result_table.align = 'l'

        # read tasks
        try:
            registered_tasks = config['tasks']

        except:
            msg = 'Unable to read task list'
            logger.error('msg')

        try:

            # task choice
            choices = [f'{tsk["classname"]} - {tsk["description"]}'
                for tsk in registered_tasks]

            questions = [
                inquirer.List('task',
                      message = 'Select task to execute',
                      choices = choices,
                      carousel = True,
                  ),
                  inquirer.Text(
                      'arg_list',
                      message = 'Arguments (comma-separated list of key=value)',
                      default = None
                  ),
            ]

            ans = inquirer.prompt(questions)

            choice_idx = choices.index(ans['task'])

            task_to_run = registered_tasks[choice_idx]

            classname = task_to_run['classname']
            filepath = task_to_run['filepath']

            # task arguments
            task_args = get_dict_from_args(ans['arg_list'])

            # loading task class
            RunningTask = load_class(filepath, classname)

            # task execution
            running_task = RunningTask(config, logger)
            response = running_task.run(task_args)

        except Exception as err:
            logger.error(f'Impossible to execute task: {str(err)}')

        else:

            logger.debug('Task has terminated')

            result_table.add_row(['Status', response.status])

            for k, v in response.data.items():
                result_table.add_row([k, v])

            print(result_table)
            print()

        return
