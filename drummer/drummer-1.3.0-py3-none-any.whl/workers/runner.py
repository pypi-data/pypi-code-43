# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
from os import getpid as os_getpid
from os import path
from drummer.utils.fio import load_class
from drummer.messages import Response, StatusCode

class Runner(Process):
    """This class implements a worker.

    Workers run as separate processes and execute commands and tasks.
    """

    def __init__(self, config, logger, active_task):

        # worker init
        super().__init__()

        # queue worker -> master
        self.queue_w2m = Queue(1)

        self.config = config
        self.logger = logger

        self.active_task = active_task

    def get_queues(self):
        #return self.queue_w2m, self.queue_m2w
        return self.queue_w2m

    def run(self):

        # get pid and send to master
        pid = os_getpid()
        self.queue_w2m.put(pid)

        # begin working
        self.work()

    def work(self):

        config = self.config
        logger = self.logger

        # get shared queues
        queue_w2m = self.queue_w2m

        # get the task to exec
        active_task = self.active_task

        # load class to exec
        classname = active_task.task.classname
        filepath = active_task.task.filepath

        timeout = active_task.task.timeout
        args = active_task.task.args

        try:
            # loading task class
            RunningTask = load_class(filepath, classname)

            # task execution
            running_task = RunningTask(config, logger)
            response = running_task.run(args)

        except Exception as err:

            response = Response()
            response.set_status(StatusCode.STATUS_ERROR)
            response.set_data({'result': str(err)})

        finally:

            # queue_done
            active_task.result = response
            queue_w2m.put(active_task)
