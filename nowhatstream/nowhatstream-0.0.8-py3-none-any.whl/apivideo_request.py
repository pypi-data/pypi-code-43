import requests
import json

from flask import current_app


class BaseRequest(object):
    def __init__(self):
        self.server_url = current_app.config['API_VIDEO_ADDR']

        self.expires = 0
        self.token = None
        self.refresh_token = None

    def get_apivideo_tokens(self):
        if self.refresh_token and self.expires > 500:
            return
        elif self.refresh_token and self.expires < 500:
            response = self.api_post('/auth/refresh', body={'refreshToken': self.refresh_token})
        else:
            response = self.api_post('/auth/api-key', body={'apiKey': current_app.config['API_VIDEO_KEY']})
        if response.status_code != 200:
            raise Exception("ERROR: APIVIDEO Authentification failed")

        self.expires = response.json().get('expires_in')
        self.token = response.json().get('access_token')
        self.refresh_token = response.json().get('refresh_token')

    def auth(self):
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

    def api_get(self, endpoint, headers=None, need_auth=False, params=None, **kwargs):
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
        response = requests.get('{base_url}{endpoint}'.format(
                base_url=self.server_url,
                endpoint=endpoint),
            params=params,
            headers=req_headers,
            **kwargs
        )
        return response

    def api_delete(self, endpoint, params=None, need_auth=False, headers=None):
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
        response = requests.delete('{base_url}{endpoint}'.format(
                base_url=self.server_url,
                endpoint=endpoint),
            params=params,
            headers=req_headers,
        )
        return response

    def api_put(self, endpoint, body=None, raw_body=None, need_auth=False, headers=None):
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
        response = requests.put('{base_url}{endpoint}'.format(
                base_url=self.server_url,
                endpoint=endpoint),
            data=raw_body or self._to_json(body),
            headers=req_headers,
        )
        return response

    def api_post(self, endpoint, body=None, raw_body=None, files=None, need_auth=False, headers=None):
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
        response = requests.post('{base_url}{endpoint}'.format(
                base_url=self.server_url,
                endpoint=endpoint),
            data=raw_body or self._to_json(body),
            files=files,
            headers=req_headers,
        )
        return response

    def api_patch(self, endpoint, body=None, raw_body=None, need_auth=False, headers=None):
        """
        The patch basic function

        :param endpoint: :str: the endpoint you are testing
        :param body: Request body as a dict (will be jsonified before request)
        :param raw_body: Request body as a dict (passed to requests as it is)
        :param need_auth: Define if the request need an authentication from us
        :param headers: Is made to modify the headers if needed
        :return: the request's return
        """
        req_headers = self._get_header(need_auth)
        req_headers.update(headers or {})
        response = requests.patch('{base_url}{endpoint}'.format(
                base_url=self.server_url,
                endpoint=endpoint),
            data=raw_body or self._to_json(body),
            headers=req_headers,
        )
        return response
