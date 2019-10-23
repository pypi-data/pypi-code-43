from ioflow.task_manager.local_task_manager import LocalTaskManager

import tensorflow as tf


class LocalTaskManagerHook(tf.train.SessionRunHook):
    def __init__(self, *args, **kwargs):
        self.task_manager = LocalTaskManager(*args, **kwargs)

    def before_run(self, *args, **kwargs):
        self.task_manager.wait()

    def after_run(self, run_context, run_values):
        if self.task_manager.should_stop():
            run_context.request_stop()
