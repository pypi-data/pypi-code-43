# -*- coding: utf-8 -*-
import ast
from os import walk as os_walk
from os import path
from drummer.logger import get_logger
from drummer.commands.base import BaseCommand
from drummer.utils.fio import load_class, write_yaml
from drummer.tasks import Task
from prettytable import PrettyTable

class TaskUpdate(BaseCommand):

    def execute(self, cmd_args):

        config = self.config

        level = 'INFO'
        logger = get_logger(config, streaming=True, level=level)
        logger.info('Updating task list...')

        task_dir = config['taskdir']

        # get python files in task folder
        filepaths = []
        for dir_name, _, file_list in os_walk(task_dir):
            for fname in file_list:
                if fname.endswith('.py'):
                    filepaths.append(path.join(dir_name, fname))

        # get list of tasks
        task_list = []
        for filepath in filepaths:

            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()

            parsed = ast.parse(text)

            classname = None
            method_name = None

            for node in ast.walk(parsed):

                if isinstance(node, ast.ClassDef):

                    CandidateTask = load_class(filepath, node.name)
                    if issubclass(CandidateTask, Task):
                        classname = node.name

                elif isinstance(node, ast.FunctionDef) and node.name == 'run':
                    method_name = node.name

            if classname and method_name:
                task_data = dict(classname=classname, filepath=filepath,
                    description='Task automatically parsed by Drummer')
                task_list.append(task_data)

                logger.info(f'Added task {classname} from file {filepath}')

        tasks_filename = path.join(config['base_dir'], 'config/drummer-tasks.yml')
        write_yaml(tasks_filename, task_list)

        logger.info(f'Task update completed.')
