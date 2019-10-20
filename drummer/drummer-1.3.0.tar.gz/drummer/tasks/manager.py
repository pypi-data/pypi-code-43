# -*- coding: utf-8 -*-
from datetime import datetime
from drummer.workers import Runner

class TaskManager:
    """Class for managing tasks to be run."""

    def __init__(self, config, logger):

        # get facilities
        self.config = config
        self.logger = logger

        # management of runners
        self.execution_data = []

    def run_task(self, queue_tasks_todo):
        """Picks a task from local queue and starts a new runner to execute it.

        Tasks are executed only if there are runners available (see max-runners
        parameter).
        """

        config = self.config
        logger = self.logger

        max_runners = config['max-runners']

        if not queue_tasks_todo.empty() and len(self.execution_data) < max_runners:

            # pick a task
            active_task = queue_tasks_todo.get()
            name = active_task.task.classname
            uid = active_task.uid
            logger.info(f'Task {name} is going to run with UID {uid}')

            # start a new runner for task
            logger.debug('Starting a new <Runner> process')
            runner = Runner(config, logger, active_task)

            # get runner queue
            queue_runner_w2m = runner.get_queues()

            # start runner process
            runner.start()

            # get pid
            pid = queue_runner_w2m.get()
            logger.info(f'Runner has successfully started with pid {pid}')

            # add task data object
            self.execution_data.append({
                'classname':    active_task.task.classname,
                'uid':          active_task.uid,
                'handle':       runner,
                'queue':        queue_runner_w2m,
                'timestamp':    datetime.now(),
                'timeout':      active_task.task.timeout,
            })

        return queue_tasks_todo

    def load_results(self, queue_tasks_done):
        """Loads task result from runners and save to local queue """

        logger = self.logger

        idx_runners_to_terminate = []

        # check tasks executed by runners
        for ii, data in enumerate(self.execution_data):

            if not data['queue'].empty():

                # pick the task
                executed = data['queue'].get() # active_task
                task_name = data['classname']
                uid = data['uid']

                logger.info(f'Task {task_name} (UID {uid}) has terminated with result {executed.result.status}')
                logger.info(f'Task {uid} says: {str(executed.result.data)}')

                # update done queue
                queue_tasks_done.put(executed)

                # prepare runners to clean
                idx_runners_to_terminate.append(ii)

        # clean-up finished runners
        if idx_runners_to_terminate:
            self._cleanup_runners(idx_runners_to_terminate)

        return queue_tasks_done

    def check_timeouts(self):

        logger = self.logger

        for ii, runner_data in enumerate(self.execution_data):

            total_seconds = (datetime.now() - runner_data['timestamp']).total_seconds()

            if (total_seconds > runner_data['timeout']):

                classname = runner_data['classname']
                uid = runner_data['uid']
                logger.info(f'Timeout exceeded, task {classname} (UID: {uid}) will be terminated')
                self._cleanup_runners([ii])

        return True

    def _cleanup_runners(self, idx_runners_to_terminate):
        """Performs clean-up of runners marked for termination.

        Runners are explicitly terminated and their queues are removed.
        """

        # clean handles
        execution_data = []
        for ii,execution in enumerate(self.execution_data):

            if ii in idx_runners_to_terminate:
                execution['handle'].terminate()
                execution['handle'].join()
            else:
                execution_data.append(execution)

        self.execution_data = execution_data
