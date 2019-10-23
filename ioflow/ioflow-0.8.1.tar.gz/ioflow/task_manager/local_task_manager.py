from ioflow.task_manager.daemon_based_task_manager import DaemonBasedTaskManager
from ioflow.task_manager.status_controller.local_status_controller import LocalStatusController


class LocalTaskManager(DaemonBasedTaskManager):
    def __init__(self, *args, **kwargs):
        super(LocalTaskManager, self).__init__(LocalStatusController())
