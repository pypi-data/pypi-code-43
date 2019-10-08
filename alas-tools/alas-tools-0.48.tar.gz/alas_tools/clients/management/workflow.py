from alas_tools.common.clients.client_base import EntityClientBase


class WorkflowClient(EntityClientBase):
    entity_endpoint_base_url = '/management/workflows/'