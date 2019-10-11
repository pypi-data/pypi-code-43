from alas_tools.common.clients.client_base import ApiClientBase


class TestClient(ApiClientBase):
    entity_endpoint_base_url = '/test'

    def get_labels_content_by_code(self, delivery_order_code):
        params = {
            'delivery_order_code': delivery_order_code,
        }
        result = self.http_post_json(self.entity_endpoint_base_url + '/render/generate_by_code', params)

        if result.response.status == 200:
            return result.content["result"]

        return None

    def get_labels_content(self, delivery_order_id):
        params = {
            'delivery_order_id': delivery_order_id,
        }
        result = self.http_post_json(self.entity_endpoint_base_url + '/render/generate', params)
        if result.response.status == 200:
            return result.content["result"]

        return None
