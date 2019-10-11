from alas_tools.clients.management.task import TaskClient
from alas_tools.common.clients.client_base import ApiClientBase


class MaintenanceClient(ApiClientBase):
    def process_operation(self, operation, params):
        return TaskClient(**self.args).enqueue('maintenance', {
            'operation': operation,
            'params': params
        })
