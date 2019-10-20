# -*- coding: utf-8 -*-
from drummer.jobs.loader import JobLoader
import sched
import time

class Extender(sched.scheduler):

    def __init__(self, config, message_queue):

        # init scheduler
        super().__init__(time.time, time.sleep)

        # threading queue
        self.message_queue = message_queue

        # list of jobs
        self.jobs = JobLoader(config).load_jobs()

    def ext_action(self, job):
        """ re-schedules next execution time and writes into the scheduler queue """

        # write to the queue
        self.message_queue.put(job)

        # get next exec time
        exec_time = job.get_next_exec_time()

        # schedule next job
        self.enterabs(exec_time, 1, self.ext_action, argument=(job,), kwargs={})

        return

    def run(self):

        # create job objects
        for job in self.jobs:

            # get next exec time of job
            exec_time = job.get_next_exec_time()

            # enter next schedulation
            self.enterabs(exec_time, 1, self.ext_action, argument=(job,), kwargs={})

        # run scheduled events
        super().run()
