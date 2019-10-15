"""
2019.8.1 create by yumin.chang
调用支付接口
"""

import adapay

from adapay.api.api_request import ApiRequest
from adapay.api.urls import payment_create, payment_query, payment_close


class Payment(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建订单
        """
        if not kwargs.get('currency'):
            kwargs['currency'] = 'cny'

        return ApiRequest.post(adapay.base_url + payment_create, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        支付查询
        """
        url = adapay.base_url + payment_query.format(payment_id=kwargs.get('payment_id'))
        return ApiRequest.get(url, kwargs)

    @classmethod
    def close(cls, **kwargs):
        """
        关单请求
        """
        url = adapay.base_url + payment_close.format(kwargs['payment_id'])
        return ApiRequest.post(url, kwargs)


