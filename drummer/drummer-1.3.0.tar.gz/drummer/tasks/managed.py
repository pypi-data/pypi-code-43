# -*- coding: utf-8 -*-
import uuid

class ManagedTask:
    """Task instance managed by scheduler. """

    def __init__(self, classname, data):

        self.classname = classname
        self.filepath = data['filepath']
        self.timeout = int(data['timeout'])
        self.args = data['args']
        self.on_pipe = data['onPipe']
        self.on_done = data['onSuccess']
        self.on_fail = data['onFail']


class ActiveTask(ManagedTask):
    """An active instance of a <ManagedTask>.

    ActiveTask is passed to Runner for execution and its result is loaded by
    job manager.
    """

    def __init__(self, task, job_name):
        """ Initialization.

        Args:
            task (ManagedTask): Task object.
            job_name (str): Name of the job to which task is related.
        """

        # task composition
        self.task = task

        # execution attributes
        self.uid = uuid.uuid4().hex
        self.related_job = job_name
        self.result = None
