import adapay
from adapay.api import urls
from adapay.api.api_request import ApiRequest


class Account(object):

    @classmethod
    def create_settle(cls, **kwargs):
        """
        创建结算账户
        """
        url = adapay.base_url + urls.settle_account_create
        return ApiRequest.post(url, kwargs)

    @classmethod
    def query_settle(cls, **kwargs):
        """
        查询结算账户
        """
        url = adapay.base_url + \
              urls.settle_account_query.format(settle_account_id=kwargs.get('settle_account_id'))
        return ApiRequest.get(url, kwargs)

    @classmethod
    def delete_settle(cls, **kwargs):
        """
        删除结算账户
        """
        url = adapay.base_url + urls.settle_account_delete
        return ApiRequest.post(url, kwargs)

    @classmethod
    def query_settle_details(cls, **kwargs):
        """
        查询结算账户明细
        """
        url = adapay.base_url + urls.settle_account_detail_query
        return ApiRequest.get(url, kwargs)


