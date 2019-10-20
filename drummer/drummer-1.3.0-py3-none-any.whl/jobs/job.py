# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from drummer.tasks.managed import ManagedTask
from croniter import croniter

class Job:
    """A data container for Job data.

    A Job is an active instance of a schedulation.

    Attributes:
        name (str): Name of the job.
        description (str): Description of the job.
        _root (str): First task of the job.
        _tasks (list): List of <ManagedTask> objects.
        _cron (obj): Cron expression of job.
    """

    def __init__(self, sched):
        """Initializes a <Job> object basing on schedulation data."""

        # job name/description
        self.name = sched.name
        self.description = sched.description
        # job root task and task data
        parameters = json.loads(sched.parameters)
        self._root = parameters['root']
        self._tasks = self.create_tasks(parameters)
        # job cron
        self._cron = croniter(sched.cronexp, datetime.now())

    def __str__(self):
        return f'{self.name} - {self.description}'

    def __eq__(self, other):
        return self.name == other.name

    def create_tasks(self, parameters):
        """Creates tasks of job basing on their parameters.

        Args:
            parameters (dict): Parameters of job tasks.

        Returns:
            list: List of <ManagedTask> objects.
        """

        task_data = parameters['tasklist']

        tasks = []
        for tsk in task_data:

            # build and add task
            task = ManagedTask(tsk, task_data[tsk])
            tasks.append(task)

        return tasks

    def get_root(self):
        return self._root

    def get_task_by_name(self, classname):

        task_data = [tsk for tsk in self._tasks if tsk.classname==classname][0]

        return task_data

    def get_next_exec_time(self):

        # get next execution absolute time
        cron_time = self._cron.get_next(datetime)
        next_exec_time = time.mktime(cron_time.timetuple())

        return next_exec_time
