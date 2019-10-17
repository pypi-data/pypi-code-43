from alas_tools.common.clients.client_base import EntityClientBase


class ContactClient(EntityClientBase):
    entity_endpoint_base_url = '/management/contacts/'