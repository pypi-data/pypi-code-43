import os

import adapay
from adapay.api import urls
from adapay.api.api_request import ApiRequest


class CorpMember(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建企业用户
        """
        url = adapay.base_url + urls.corp_member_create
        file_path = kwargs.get('attach_file')
        files = {'attach_file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream')}
        kwargs.pop('attach_file')
        return ApiRequest.post(url, kwargs, files)

    @classmethod
    def query(cls, **kwargs):
        """
        查询企业用户
        """
        url = adapay.base_url + urls.corp_member_query.format(member_id=kwargs.get('member_id'))
        return ApiRequest.get(url, kwargs)


