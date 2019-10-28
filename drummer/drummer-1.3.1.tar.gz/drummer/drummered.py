# -*- coding: utf-8 -*-
from .workers import Scheduler, Listener
from .tasks.manager import TaskManager
from .jobs.manager import JobManager
from .jobs.loader import JobLoader
from .utils.fio import load_class
from .logger import get_logger
from .utils import Queued
from time import sleep


class Drummered:

    def __init__(self, config):

        # get configuration
        self.config = config

        # get logger
        self.logger = get_logger(config)
        self.logger.info('Starting Drummer service...')

        # create task queues
        self.queue_tasks_todo = Queued()
        self.queue_tasks_done = Queued()

        # create scheduler package
        self.scheduler_bundle = self.create_scheduler()

        # create listener package
        self.listener_bundle = self.create_listener()

    def start(self):

        # [INIT]
        # ----------------------------------------------- #

        # get config
        config = self.config

        # get logger
        logger = self.logger

        # create job manager
        job_manager = JobManager(config, logger)

        # load internal queues
        queue_tasks_todo = self.queue_tasks_todo
        queue_tasks_done = self.queue_tasks_done

        # load config parameters
        idle_time = config['idle-time']

        # create task runner
        task_manager = TaskManager(config, logger)


        # [MAIN LOOP]
        # ----------------------------------------------- #
        while True:

            # [HEALTH CHECK]
            # ----------------------------------------------- #

            # check whether scheduler is alive
            if not self.scheduler_bundle['handle'].is_alive():
                self.logger.warning('Scheduler has exited, it will be restarted')
                self.scheduler_bundle = self.create_scheduler()

            # check whether listener is alive
            if not self.listener_bundle['handle'].is_alive():
                self.logger.warning('Listener has exited, it will be restarted')
                self.listener_bundle = self.create_listener()


            # [MESSAGE CHECK]
            # ----------------------------------------------- #

            # check for messages from listener
            job_manager = self.check_messages_from_listener(job_manager)

            # check for messages from scheduler
            job_manager = self.check_messages_from_scheduler(job_manager)


            # [TASK/JOB CHECK]
            # ----------------------------------------------- #

            # check for finished tasks
            queue_tasks_done = task_manager.load_results(queue_tasks_done)

            # check for task timeouts
            task_manager.check_timeouts()

            # check tasks to be executed
            queue_tasks_todo = task_manager.run_task(queue_tasks_todo)

            # update todo queue
            queue_tasks_todo, queue_tasks_done = job_manager.update_status(queue_tasks_todo, queue_tasks_done)

            # idle time
            sleep(idle_time)

        return

    def load_event(self, request):

        config = self.config

        # load event class to exec
        classname = request.classname
        classpath = request.classpath

        # execute the event and get result
        EventToExec = load_class(classpath, classname, relative=True)

        response, follow_up = EventToExec(config).execute(request)

        return response, follow_up

    def check_messages_from_listener(self, job_manager):

        logger = self.logger

        # get listener components
        listener_bundle = self.listener_bundle
        listener_queue_w2m = listener_bundle['queue_w2m']

        # check for requests from listener
        if not listener_queue_w2m.empty():

            # handle request from listener
            logger.info('Serving a new request from console')

            # get the request
            request = listener_queue_w2m.get()

            # run the request
            response, follow_up = self.load_event(request)

            # send the response
            listener_queue_m2w = listener_bundle['queue_m2w']
            listener_queue_m2w.put(response)

            # process the event follow-up
            if follow_up.action:
                self.process_follow_up(job_manager, follow_up)

        return job_manager

    def check_messages_from_scheduler(self, job_manager):

        logger = self.logger

        scheduler_bundle = self.scheduler_bundle
        scheduler_queue_w2m = scheduler_bundle['queue_w2m']

        queue_tasks_todo = self.queue_tasks_todo

        while not scheduler_queue_w2m.empty():

            # pick job to be executed
            job = scheduler_queue_w2m.get()

            # handle request from scheduler
            logger.info(f'Job "{job}" is going to be executed')

            # add job to be managed
            queue_tasks_todo = job_manager.add_job(job, queue_tasks_todo)

        return job_manager

    def create_listener(self):

        config = self.config
        logger = self.logger

        logger.info('Starting Listener')

        listener = Listener(config)
        listener_queue_w2m, listener_queue_m2w = listener.get_queues()

        listener.start()
        pid = listener_queue_w2m.get()

        logger.info(f'Listener successfully started with pid {pid}')

        listener_bundle = {
            'handle': listener,
            'queue_w2m': listener_queue_w2m,
            'queue_m2w': listener_queue_m2w,
        }

        return listener_bundle

    def create_scheduler(self):

        config = self.config
        logger = self.logger

        logger.info('Starting Scheduler')

        scheduler = Scheduler(config)
        scheduler_queue_w2m = scheduler.get_queues()

        scheduler.start()
        pid = scheduler_queue_w2m.get()

        logger.info(f'Scheduler successfully started with pid {pid}')

        scheduler_bundle = {
            'handle': scheduler,
            'queue_w2m': scheduler_queue_w2m
        }
        return scheduler_bundle

    def process_follow_up(self, job_manager, follow_up):

        scheduler_bundle = self.scheduler_bundle

        if follow_up.action == 'RELOAD':

            self.logger.info('Schedulation has changed, restarting Scheduler')

            # terminate current scheduler
            scheduler_bundle['handle'].terminate()
            scheduler_bundle['handle'].join()

            # start new scheduler
            self.scheduler_bundle = self.create_scheduler()

        elif follow_up.action == 'EXECUTE':

            schedule_id = follow_up.value
            self.logger.info(f'Schedulation {schedule_id} is sent to queue for immediate execution')

            job = JobLoader(self.config).load_job_by_id(schedule_id)

            # add job to be managed
            self.queue_tasks_todo = job_manager.add_job(job, self.queue_tasks_todo)

        return job_manager
