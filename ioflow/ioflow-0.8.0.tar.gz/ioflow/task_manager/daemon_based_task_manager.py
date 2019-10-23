import functools
from threading import Event, Thread

from ioflow.task_manager.status_controller.status_controller_base import \
    StatusControllerBase
from ioflow.task_manager.task_manager import TaskManager


class DaemonBasedTaskManager(TaskManager):
    def __init__(self, status_controller: StatusControllerBase, *args, **kwargs):
        super().__init__()

        t = Thread(target=functools.partial(status_controller, self.pause_event, self.stop_event))
        t.setDaemon(True)
        t.start()
