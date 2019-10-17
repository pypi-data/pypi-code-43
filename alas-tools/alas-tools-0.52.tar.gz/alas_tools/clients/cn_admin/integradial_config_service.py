from alas_tools.clients.cn_admin.service_api_client import ServiceApiClient
from alas_tools.common.clients import api_client as clients


class IntegradialConfigApiServiceClient(ServiceApiClient):
    service_endpoint_base_url = '/api/services/app/IntergradialConfig/'
    # GetIntergradialConfigForUser?User=ariobueno

    def _get_by_user(self, **kwargs):
        url = self.service_endpoint_base_url + 'GetIntergradialConfigForUser'
        url = "{}?User={user}".format(url, **kwargs)

        request = clients.ApiClientRequest(url, self.auth)
        response = self.http_get(request)
        return response

    def get_by_user(self, user):
        """

        :rtype: ApiClientResponse
        """
        return self.process_request(self._get_by_user, **{
            'user': user
        })
