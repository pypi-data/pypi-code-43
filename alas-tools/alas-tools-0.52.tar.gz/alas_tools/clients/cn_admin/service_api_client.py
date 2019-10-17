from alas_tools.clients.cn_admin.corenet_api_client import CoreNetApiClient
from alas_tools.common.clients import api_client as clients


class ServiceApiClient(CoreNetApiClient):
    service_endpoint_base_url = '/api/services/app/'

    def _get_all(self):
        request = clients.ApiClientRequest(
            self.service_endpoint_base_url + 'GetAll', self.auth)
        response = self.http_get(request)
        return response

    def _get_by_filter(self, **kwargs):
        url = self.service_endpoint_base_url + 'GetByFilter'
        if 'filter' in kwargs and kwargs['filter'] is not None:
            url = "{}?Filter={filter}".format(url, **kwargs)

        request = clients.ApiClientRequest(url, self.auth)
        response = self.http_get(request)
        return response

    def get_all(self):
        return self.process_request(self._get_all)

    def get_by_filter(self, filter=None):
        """

        :rtype: ApiClientResponse
        """
        return self.process_request(self._get_by_filter, **{
            'filter': filter
        })
