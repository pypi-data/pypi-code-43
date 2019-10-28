# -*- coding: utf-8 -*-
"""Job commands.

This module includes all commands related to job management.

All these commands subclass RemoteCommand because they are executed remotely by
Drummered service.
"""
import json
from .base import RemoteCommand
from drummer.utils.validation import check_cron, check_int, get_dict_from_args
from drummer.messages import Request, StatusCode
from drummer.sockets.client import SocketClient
from prettytable import PrettyTable
import inquirer


class JobList(RemoteCommand):

    def __init__(self, config):

        super().__init__(config)

    def execute(self, cmd_args):

        config = self.config

        # test socket connection
        self.test_socket_connection()

        # init result table
        table = PrettyTable()
        table.field_names = ['ID', 'Name', 'Description', 'Cronexp', 'Enabled']
        table.align['Name'] = 'l'
        table.align['Description'] = 'l'
        table.align['Cronexp'] = 'l'

        # prepare request to listener
        request = Request()
        request.set_classname('JobListEvent')
        request.set_classpath(self.CLASSPATH)

        # send request to listener
        sc = SocketClient(config)
        response = sc.send_request(request)

        if response.status == StatusCode.STATUS_OK:

            job_list = response.data['Result']

            for s in job_list:

                uid = s.get('id')
                name = s.get('name')
                description = s.get('description')
                cronexp = s.get('cronexp')
                enabled = s.get('enabled')

                table.add_row([uid, name, description, cronexp, enabled])

            print(table)
            print()

        else:
            print('Impossible to execute the command')


class JobAdd(RemoteCommand):

    def __init__(self, config):

        super().__init__(config)

    def execute(self, cmd_args):

        config = self.config

        # test socket connection
        self.test_socket_connection()

        registered_tasks = config['tasks']

        job = self.ask_basics()

        # get job data from the user
        job['parameters'] = self.set_job_parameters(registered_tasks)

        # prepare request to listener
        request = Request()
        request.set_classname('JobAddEvent')
        request.set_classpath(self.CLASSPATH)
        request.set_data(job)

        # send request to listener
        sc = SocketClient(config)
        response = sc.send_request(request)

        # init result table
        table = PrettyTable()
        table.field_names = ['Status', 'Message']
        table.align['Status'] = 'c'
        table.align['Message'] = 'l'
        table.add_row([response.status, response.data['msg']])
        print(table)
        print()

        return

    def ask_basics(self):

        questions = [
            inquirer.Text(
                'name',
                message = 'Name of job'
            ),
            inquirer.Text(
                'description',
                message = 'Description of job',
            ),
            inquirer.Text(
                'cronexp',
                message = 'Cron expression',
                validate = check_cron,
            ),
            inquirer.Confirm(
                'enabled',
                message = 'Enable the job?',
                default = True,
            )
        ]

        job = inquirer.prompt(questions)

        return job

    def set_task(self, registered_tasks, job_parameters):

        classnames = [tsk['classname'] for tsk in registered_tasks]

        # select a task
        choices = [f'{tsk["classname"]} - {tsk["description"]}' for tsk in registered_tasks]

        questions = [
            inquirer.List('task',
                  message = 'Select task to execute',
                  choices = choices,
                  carousel = True,
              ),
              inquirer.Text(
                  'timeout',
                  message = 'Timeout',
                  default = '600',
                  validate = check_int
              ),
              inquirer.Text(
                  'arg_list',
                  message = 'Arguments (comma-separated list of key=value)',
                  default = None
              ),
        ]

        ans = inquirer.prompt(questions)

        task_idx = choices.index(ans['task'])

        task_to_run = registered_tasks[task_idx]

        classname = task_to_run['classname']

        # set task data
        task = {}
        task['filepath'] = task_to_run['filepath']
        task['timeout'] = ans['timeout']
        task['args'] = get_dict_from_args(ans['arg_list'])
        task['onPipe'] = None
        task['onSuccess'] = None
        task['onFail'] = None

        job_parameters['tasklist'][classname] = task

        return job_parameters, classname

    def set_connection(self, registered_tasks, parameters, base_task):

        question_pipe = [
            inquirer.Confirm('onPipe',
                message = f'[{base_task}] Do you want to pipe another task?',
                default = False,
            )
        ]
        question_success = [
            inquirer.Confirm('onSuccess',
                message = f'[{base_task}] Do you want to execute another task on success?',
                default = False,
            )
        ]
        question_fail = [
            inquirer.Confirm('onFail',
                message = f'[{base_task}] Do you want to execute another task on fail?',
                default = False,
            )
        ]

        ans = inquirer.prompt(question_pipe)

        if ans['onPipe']:
            parameters, next_task = self.set_task(registered_tasks, parameters)
            parameters['tasklist'][base_task]['onPipe'] = next_task
            parameters = self.set_connection(registered_tasks, parameters, next_task)

        ans = inquirer.prompt(question_success)

        if ans['onSuccess']:
            parameters, next_task = self.set_task(registered_tasks, parameters)
            parameters['tasklist'][base_task]['onSuccess'] = next_task
            parameters = self.set_connection(registered_tasks, parameters, next_task)

        ans = inquirer.prompt(question_fail)

        if ans['onFail']:
            parameters, next_task = self.set_task(registered_tasks, parameters)
            parameters['tasklist'][base_task]['onFail'] = next_task
            parameters = self.set_connection(registered_tasks, parameters, next_task)

        return parameters

    def set_job_parameters(self, registered_tasks):

        job_parameters = {'tasklist': {}}

        # get a task and set connections
        job_parameters, classname = self.set_task(registered_tasks, job_parameters)

        job_parameters['root'] = classname
        job_parameters = self.set_connection(registered_tasks, job_parameters, classname)

        # serialize to json
        job_parameters = json.dumps(job_parameters)

        return job_parameters


class JobRemove(RemoteCommand):

    def __init__(self, config):

        super().__init__(config)

    def execute(self, cmd_args):

        config = self.config

        # test socket connection
        self.test_socket_connection()

        # prepare request to listener
        request = Request()
        request.set_classname('JobRemoveEvent')
        request.set_classpath(self.CLASSPATH)
        request.set_data(cmd_args)

        # send request to listener
        sc = SocketClient(config)
        response = sc.send_request(request)

        # init result table
        table = PrettyTable()
        table.field_names = ['Status', 'Message']
        table.align['Status'] = 'c'
        table.align['Message'] = 'l'
        table.add_row([response.status, response.data['msg']])
        print(table)
        print()

        return


class JobEnable(RemoteCommand):

    def __init__(self, config):

        super().__init__(config)

    def execute(self, cmd_args):

        config = self.config

        # test socket connection
        self.test_socket_connection()

        # prepare request to listener
        request = Request()
        request.set_classname('JobEnableEvent')
        request.set_classpath(self.CLASSPATH)
        request.set_data(cmd_args)

        # send request to listener
        sc = SocketClient(config)
        response = sc.send_request(request)

        # init result table
        table = PrettyTable()
        table.field_names = ['Status', 'Message']
        table.align['Status'] = 'c'
        table.align['Message'] = 'l'
        table.add_row([response.status, response.data['msg']])
        print(table)
        print()

        return


class JobDisable(RemoteCommand):

    def __init__(self, config):

        super().__init__(config)

    def execute(self, cmd_args):

        config = self.config

        # test socket connection
        self.test_socket_connection()

        # prepare request to listener
        request = Request()
        request.set_classname('JobDisableEvent')
        request.set_classpath(self.CLASSPATH)
        request.set_data(cmd_args)

        # send request to listener
        sc = SocketClient(config)
        response = sc.send_request(request)

        # init result table
        table = PrettyTable()
        table.field_names = ['Status', 'Message']
        table.align['Status'] = 'c'
        table.align['Message'] = 'l'
        table.add_row([response.status, response.data['msg']])
        print(table)
        print()

        return


class JobExec(RemoteCommand):

    def __init__(self, config):

        super().__init__(config)

    def execute(self, cmd_args):

        config = self.config

        # test socket connection
        self.test_socket_connection()

        # prepare request to listener
        request = Request()
        request.set_classname('JobExecEvent')
        request.set_classpath(self.CLASSPATH)
        request.set_data(cmd_args)

        # send request to listener
        sc = SocketClient(config)
        response = sc.send_request(request)

        # init result table
        table = PrettyTable()
        table.field_names = ['Status', 'Message']
        table.align['Status'] = 'c'
        table.align['Message'] = 'l'
        table.add_row([response.status, response.data['msg']])
        print(table)
        print()

        return


class JobGet(RemoteCommand):

    def __init__(self, config):

        super().__init__(config)

    def execute(self, cmd_args):

        config = self.config

        # test socket connection
        self.test_socket_connection()

        # init overview table
        table_overview = PrettyTable()
        table_overview.field_names = ['ID', 'Name', 'Description', 'Cronexp', 'Enabled']
        table_overview.align['Name'] = 'l'
        table_overview.align['Description'] = 'l'
        table_overview.align['Cronexp'] = 'l'

        # init task table
        table_task = PrettyTable()
        table_task.field_names = ['No.', 'Task', 'Filepath', 'Timeout', 'Args', 'onPipe', 'onSuccess', 'onFail']
        table_task.align = 'l'

        # prepare request to listener
        request = Request()
        request.set_classname('JobGetEvent')
        request.set_classpath(self.CLASSPATH)
        request.set_data(cmd_args)

        # send request to listener
        sc = SocketClient(config)
        response = sc.send_request(request)

        if response.status == StatusCode.STATUS_OK:

            schedule_info = response.data['Result']

            uid = schedule_info.get('id')
            name = schedule_info.get('name')
            description = schedule_info.get('description')
            cronexp = schedule_info.get('cronexp')
            enabled = schedule_info.get('enabled')

            table_overview.add_row([uid, name, description, cronexp, enabled])

            print()
            print('Job overview:')
            print(table_overview)
            print()

            job_parameters = json.loads(schedule_info.get('parameters'))

            for ii,(task_name,task_params) in enumerate(job_parameters['tasklist'].items()):

                if (task_name==job_parameters['root']): task_name = task_name+'*'

                filepath = task_params['filepath']
                timeout = task_params['timeout']
                args = task_params['args']
                onPipe = task_params['onPipe']
                onSuccess = task_params['onSuccess']
                onFail = task_params['onFail']

                table_task.add_row([ii, task_name, filepath, timeout, args, onPipe, onSuccess, onFail])

            print('Job tasks:')
            print(table_task)
            print(' *Root task')
            print()

        else:
            print('Impossible to get schedule info')
