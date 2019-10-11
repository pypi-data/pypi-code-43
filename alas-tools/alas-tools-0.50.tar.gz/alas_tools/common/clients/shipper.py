from alas_tools.common.clients.api_client import ApiHttpClientBase, ApiClientRequest


class ShipperThirdPartyApiClient(ApiHttpClientBase):
    entity_endpoint_base_url = '/dispatchs/v0/'

    def __init__(self, **kwargs):
        super(ShipperThirdPartyApiClient, self).__init__(**kwargs)
        self.apikey = kwargs["alas_key"]

    def _get_headers(self, request):
        """
        :type request: ApiClientRequest
        """
        headers = super(ShipperThirdPartyApiClient, self)._get_headers(request)
        headers.update({
                "apikey": self.apikey
            })
        return headers

    def get_order(self, id_dispatch):

        url = "{}dispatch/{}".format(self.entity_endpoint_base_url, id_dispatch)
        request = ApiClientRequest(url, json_request=False)
        return self.http_get(request)

    def get_status(self, id_dispatch):
        url = "{}status/{}".format(self.entity_endpoint_base_url, id_dispatch)
        request = ApiClientRequest(url, json_request=False)
        return self.http_get(request)

    def send_status(self, status):
        url = "{}status/".format(self.entity_endpoint_base_url)
        request = ApiClientRequest(url, status)
        return self.http_put(request)
