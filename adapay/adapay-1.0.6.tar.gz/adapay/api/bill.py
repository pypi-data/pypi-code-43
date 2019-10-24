import adapay
from adapay.api import urls
from adapay.api.api_request import ApiRequest


class Bill(object):

    @classmethod
    def download(cls, **kwargs):
        url = adapay.base_url + urls.bill_download
        return ApiRequest.post(url, kwargs)


