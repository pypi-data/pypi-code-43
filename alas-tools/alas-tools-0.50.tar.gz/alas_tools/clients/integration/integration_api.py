from alas_tools.common.clients.client_base import EntityClientBase


class IntegrationApiClient(EntityClientBase):
    entity_endpoint_base_url = '/api/delivery-orders'

    def send_delivery_order(self, delivery_order, api_key):
        self.headers.update({
            "x-alas-ce0-api-key": api_key
        })

        result = self.http_post_json(self.entity_endpoint_base_url, delivery_order)
        return result
