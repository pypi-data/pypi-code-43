import adapay
from adapay.api import urls
from adapay.api.api_request import ApiRequest


class Member(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建用户
        """
        url = adapay.base_url + urls.member_create
        return ApiRequest.post(url, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        查询用户
        """
        url = adapay.base_url + urls.member_query.format(member_id=kwargs.get('member_id'))
        return ApiRequest.get(url, kwargs)

    @classmethod
    def query_list(cls, **kwargs):
        """
        查询用户
        """
        url = adapay.base_url + urls.member_query_list
        return ApiRequest.get(url, kwargs)

    @classmethod
    def update(cls, **kwargs):
        """
        更新用户
        """
        url = adapay.base_url + urls.member_update
        return ApiRequest.post(url, kwargs)


