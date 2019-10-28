import datetime
import json

from flask import request, current_app


class BaseRequest(object):
    def __init__(self):
        self.server_url = current_app.conf['API_VIDEO_ADDR']

        self.expires = datetime.datetime.utcnow()
        self.token = None
        self.refresh_token = None

    def get_apivideo_tokens(self):
        if self.refresh_token:
            pass
            return
        response = request.post("{base_addr}{path}/{api_key}".format(
            base_addr=current_app.config['API_VIDEO_ADDR'],
            path='/auth',
            api_key=current_app.config['API_VIDEO_KEY']
        ))
        self.expires = datetime.datetime.utcnow()
        self.token = response.json()

    def auth(self):
        if self.expires and self.expires < datetime.datetime.utcnow():
            self.get_apivideo_tokens()
        return self.token

    def _get_header(self, need_auth=False, auth_type='Bearer'):
        base_headers = {
            "Accept": "application/json",
        }
        headers = base_headers.copy()
        if need_auth:
            headers['Authorization'] = auth_type + ' ' + self.auth()
        return headers

    def _get_json_header(self, auth_type='Bearer'):
        headers = self._get_header(auth_type=auth_type)
        headers['Content-Type'] = "application/json"
        return headers

    def _to_json(self, body):
        if body is None:
            return None

        return json.dumps(body)

    def get(self, endpoint, headers=None, need_auth=False, params=None, **kwargs):
        """
        The get's basic function

        :param endpoint: :str: the endpoint you are testing
        :param headers: Is made to modify the headers if needed
        :param need_auth: Define if the request need an authentication from us
        :param params: Adding parameters at the end of the URL
        :param kwargs: Classic kwargs dict
        :return: the request's return
        """
        req_headers = self._get_header(need_auth)
        req_headers.update(headers or {})
        return request.get('{base_url}{endpoint}'.format(
            base_url=self.server_url,
            endpoint=endpoint),
            params=params,
            headers=req_headers,
            **kwargs
        )

    def delete(self, endpoint, params=None, need_auth=False, headers=None):
        """
        The delete basic function

        :param endpoint: :str: the endpoint you are testing
        :param params: The request parameters
        :param need_auth: Define if the request need an authentication from us
        :param headers: Is made to modify the headers if needed
        :return: the request's return
        """
        req_headers = self._get_header(need_auth)
        req_headers.update(headers or {})
        return request.get('{base_url}{endpoint}'.format(
            base_url=self.server_url,
            endpoint=endpoint),
            params=params,
            headers=req_headers,
        )

    def put(self, endpoint, body=None, raw_body=None, need_auth=False, headers=None):
        """
        The post basic function

        :param endpoint: :str: the endpoint you are testing
        :param body: Request body as a dict (will be jsonified before request)
        :param raw_body: Request body as a dict (passed to requests as it is)
        :param need_auth: Define if the request need an authentication from us
        :param headers: Is made to modify the headers if needed
        :return: the request's return
        """
        req_headers = self._get_header(need_auth)
        req_headers.update(headers or {})
        return request.get('{base_url}{endpoint}'.format(
            base_url=self.server_url,
            endpoint=endpoint),
            data=raw_body or self._to_json(body),
            headers=req_headers,
        )

    def post(self, endpoint, body=None, raw_body=None, need_auth=False, headers=None):
        """
        The post basic function

        :param endpoint: :str: the endpoint you are testing
        :param body: Request body as a dict (will be jsonified before request)
        :param raw_body: Request body as a dict (passed to requests as it is)
        :param need_auth: Define if the request need an authentication from us
        :param headers: Is made to modify the headers if needed
        :return: the request's return
        """
        req_headers = self._get_header(need_auth)
        req_headers.update(headers or {})
        return request.get('{base_url}{endpoint}'.format(
            base_url=self.server_url,
            endpoint=endpoint),
            data=raw_body or self._to_json(body),
            headers=req_headers,
        )
