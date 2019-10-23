from ioflow.task_manager.daemon_based_task_manager import DaemonBasedTaskManager
from ioflow.task_manager.status_controller.db_status_controller import DbStatusController


class DbTaskManager(DaemonBasedTaskManager):
    def __init__(self, *args, **kwargs):
        super(DbTaskManager, self).__init__(DbStatusController(*args, **kwargs))
