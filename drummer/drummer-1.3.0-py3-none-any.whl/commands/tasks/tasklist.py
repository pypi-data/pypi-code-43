# -*- coding: utf-8 -*-
from sys import path as sys_path
from drummer.commands.base import BaseCommand
from prettytable import PrettyTable


class TaskList(BaseCommand):

    def execute(self, cmd_args):

        config = self.config

        # add task folder to syspath
        sys_path.append(config['taskdir'])

        table = PrettyTable()
        table.field_names = ['No.', 'Name', 'Description']
        table.align['Name'] = 'l'
        table.align['Description'] = 'l'

        registered_tasks = config['tasks']

        print('\nList of registered tasks:')

        for ii,tsk in enumerate(registered_tasks):
            table.add_row([ii, tsk['classname'], tsk['description']])
        print(table)
        print()
