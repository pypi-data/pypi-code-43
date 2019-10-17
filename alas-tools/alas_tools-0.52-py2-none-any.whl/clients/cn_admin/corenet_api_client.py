
import alas_tools.common.clients.api_client as clients


class CoreNetApiClient(clients.ApiHttpClientBase):
    endpoint_base_url = '/api/'

    def __init__(self, **kwargs):
        super(CoreNetApiClient, self).__init__(**kwargs)
        self.access_token = None
        self.auth_data = None
        self.auth = kwargs.pop('auth', None)
        self.set_auth(None)

    def set_auth(self, value=None):
        self.auth_data = value
        if value is None:
            self.access_token = None
        else:
            self.access_token = value["result"]["accessToken"]

    def login(self):
        request = clients.ApiClientRequest(
            self.endpoint_base_url + 'TokenAuth/Authenticate', self.auth)
        response = self.http_post(request)
        if response.response.status == 200:
            result = response.get_content()
            self.set_auth(result)

        return response

    def verify_login(self):
        if self.access_token is None:
            self.login()

    def is_authenticated(self):
        return self.access_token is not None

    def _get_headers(self, request):
        """
        :type request: ApiClientRequest
        """
        headers = {}
        if self.access_token is not None:
            headers.update({
                'Authorization': 'Bearer {}'.format(self.access_token),
            })
        if request.json_request:
            headers.update({
                'Content-Type': 'application/json'
            })
        return headers

    def process_request(self, callback, **kwargs):
        """

        :rtype: ApiClientResponse
        """
        intent = 1
        response = None
        while intent > -1:
            self.verify_login()

            response = callback(**kwargs)

            if response.response.status == 401:
                self.login()
            else:
                intent = 0
            intent -= 1

        return response


