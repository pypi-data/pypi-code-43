"""
2019.8.1 create by jun.hu
退款接口
"""

import adapay
from adapay.api.api_request import ApiRequest
from adapay.api.urls import refund_create, refund_query


class Refund(object):

    @classmethod
    def create(cls, **kwargs):
        """
        发起退款流程
        """

        url = adapay.base_url + refund_create.format(kwargs.get('payment_id', ''))
        return ApiRequest.post(url, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        退款流程查询
        """

        return ApiRequest.get(adapay.base_url + refund_query, kwargs)


