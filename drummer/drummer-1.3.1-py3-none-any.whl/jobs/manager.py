# -*- coding: utf-8 -*-
from drummer.tasks.managed import ActiveTask
from drummer.errors import Errors
from drummer.messages import StatusCode


class JobManager:
    """Manages jobs to be executed. """

    def __init__(self, config, logger):

        # get logger
        self.logger = logger

        # managed jobs
        self._jobs = {}
        self._pending_tasks = {}

    def add_job(self, job, queue_tasks_todo):
        """Adds a new job to be executed."""

        # update job list
        #self.jobs.append(job)
        self._jobs[job.name] = job

        # send to queue the first task
        root_classname = job.get_root()

        queue_tasks_todo = self.add_to_queue(job, root_classname, queue_tasks_todo)

        return queue_tasks_todo

    def add_to_queue(self, job, classname, queue_tasks_todo):
        """Adds a new task to the "todo" queue."""

        # get task data
        task = job.get_task_by_name(classname)
        active_task = ActiveTask(task, job.name)

        queue_tasks_todo.put(active_task)
        self.logger.debug(f'Task {task.classname} has been inserted in queue for execution')

        # update pending tasks for job
        if job.name in self._pending_tasks:
            self._pending_tasks[job.name] += 1
        else:
            self._pending_tasks[job.name] = 1
        self.logger.debug(f'Job {job.name} has now {self._pending_tasks[job.name]} pending tasks')

        return queue_tasks_todo

    def update_status(self, queue_tasks_todo, queue_tasks_done):
        """Loads task results and update job status. """

        while not queue_tasks_done.empty():

            # get task executed
            executed_task = queue_tasks_done.get()

            next_tasks = self.get_next_tasks(executed_task)

            if next_tasks:

                for task in next_tasks:
                    # add next task to todo queue
                    self.logger.debug(f'Adding task {task} to queue for execution')
                    job = self.get_job(executed_task.related_job)
                    queue_tasks_todo = self.add_to_queue(job, task, queue_tasks_todo)

            elif self._pending_tasks[executed_task.related_job] == 0:

                # job is finished, remove it
                self.logger.debug(f'No more tasks for job {executed_task.related_job}')
                self.remove_job(executed_task.related_job)

        return queue_tasks_todo, queue_tasks_done

    def get_next_tasks(self, executed_task):
        """Gets a list of next tasks to be executed.

        Tasks can be up to two: the task on_pipe and the task on_done/on_fail.
        """

        next_tasks = []

        # take result of executed task
        result = executed_task.result

        # check result consistency
        if result.status in (StatusCode.STATUS_OK, StatusCode.STATUS_WARNING, StatusCode.STATUS_ERROR):
            self._pending_tasks[executed_task.related_job] -= 1
            self.logger.debug(f'Job {executed_task.related_job} has now {self._pending_tasks[executed_task.related_job]} pending tasks')
        else:
            self.logger.errror(Errors.E0104)
            return next_tasks

        # get next task classname
        if executed_task.task.on_pipe:
            next_tasks.append(executed_task.task.on_pipe)
        if executed_task.task.on_done and result.status == StatusCode.STATUS_OK:
            next_tasks.append(executed_task.task.on_done)
        elif executed_task.task.on_fail and result.status == StatusCode.STATUS_ERROR:
            next_tasks.append(executed_task.task.on_fail)

        self.logger.debug(f'Task(s) {next_tasks} found for next execution')

        return next_tasks

    def get_job(self, name):
        """Gets a job by name. """
        return self._jobs[name]

    def remove_job(self, name):
        """Terminates a job and deletes its data. """

        if name in self._jobs:
            del self._jobs[name]
            del self._pending_tasks[name]
            self.logger.debug(f'Job {name} has been removed from execution queue')
        else:
            self.logger.error(f'Job {name} not found in memory')
