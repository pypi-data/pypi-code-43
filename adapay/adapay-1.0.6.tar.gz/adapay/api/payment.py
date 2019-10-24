"""
2019.8.1 create by yumin.chang
调用支付接口
"""

import adapay

from adapay.api.api_request import ApiRequest
from adapay.api.urls import payment_create, payment_query, payment_close, payment_reverse, payment_reverse_query_list, \
    payment_confirm, payment_confirm_query, payment_confirm_query_list, payment_reverse_query


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
    def create_confirm(cls, **kwargs):
        """
        创建订单确认
        """
        return ApiRequest.post(adapay.base_url + payment_confirm, kwargs)

    @classmethod
    def query_confirm(cls, **kwargs):
        """
        查询订单确认
        """
        url = adapay.base_url + payment_confirm_query.format(payment_confirm_id=kwargs.get('payment_confirm_id'))
        return ApiRequest.get(url, kwargs)

    @classmethod
    def query_confirm_list(cls, **kwargs):
        """
         查询订单确认列表
        """
        return ApiRequest.get(adapay.base_url + payment_confirm_query_list, kwargs)

    @classmethod
    def create_reverse(cls, **kwargs):
        """
        支付撤销
        """
        return ApiRequest.post(adapay.base_url + payment_reverse, kwargs)

    @classmethod
    def query_reverse(cls, **kwargs):
        """
        查询支付撤销
        """
        url = adapay.base_url + payment_reverse_query.format(reverse_id=kwargs.get('reverse_id'))
        return ApiRequest.get(url, kwargs)

    @classmethod
    def query_reverse_list(cls, **kwargs):
        """
        查询支付撤销列表
        """
        return ApiRequest.get(adapay.base_url + payment_reverse_query_list, kwargs)

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


