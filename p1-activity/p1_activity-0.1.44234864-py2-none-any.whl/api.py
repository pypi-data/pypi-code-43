import os
import json

import requests
from rest_framework import status


K_API_BASE_URL = os.environ['ACTIVITY_BASE_API_URL']
K_API_KEY = os.environ['ACTIVITY_API_KEY']


class ActivityAPI(object):
    BASE_URL = K_API_BASE_URL

    def get_headers(self, original_headers={}):
        headers = original_headers.copy()
        headers['content-type'] = 'application/json'
        headers['api-key'] = K_API_KEY
        return headers

    def get(self, endpoint, params=None, headers={}):
        try:
            req = requests.get(self.BASE_URL + endpoint, params=params,
                               headers=self.get_headers(headers))
            req.raise_for_status()
            return json.loads(req.content)
        except requests.exceptions.HTTPError as e:
            raise ClientError(req.status_code, req.content, str(e))
        except Exception as e:
            raise ClientError(status.HTTP_408_REQUEST_TIMEOUT,
                              'Terjadi Kesalahan Pada Sistem, Silakan Mencoba Kembali', str(e))

    def post(self, endpoint, data={}, headers={}):
        try:
            req = requests.post(self.BASE_URL + endpoint, json=data,
                                headers=self.get_headers(headers))
            req.raise_for_status()
            return json.loads(req.content)
        except requests.exceptions.HTTPError as e:
            raise ClientError(req.status_code, req.content, str(e))
        except Exception as e:
            raise ClientError(status.HTTP_408_REQUEST_TIMEOUT,
                              'Terjadi Kesalahan Pada Sistem, Silakan Mencoba Kembali', str(e))

    def patch(self, endpoint, data={}, headers={}):
        try:
            req = requests.patch(self.BASE_URL + endpoint, json=data,
                                 headers=self.get_headers(headers))
            return json.loads(req.content)
        except requests.exceptions.HTTPError as e:
            raise ClientError(req.status_code, req.content, str(e))
        except Exception as e:
            raise ClientError(status.HTTP_408_REQUEST_TIMEOUT,
                              'Terjadi Kesalahan Pada Sistem, Silakan Mencoba Kembali', str(e))

    def delete(self, endpoint, headers={}):
        try:
            req = requests.delete(self.BASE_URL + endpoint, headers=self.get_headers(headers))
            req.raise_for_status()
            return json.loads(req.content)
        except requests.exceptions.HTTPError as e:
            raise ClientError(req.status_code, req.content, str(e))
        except Exception as e:
            raise ClientError(status.HTTP_408_REQUEST_TIMEOUT,
                              'Terjadi Kesalahan Pada Sistem, Silakan Mencoba Kembali', str(e))

    def check_base_url(self):
        if self.BASE_URL is None:
            raise Exception('Base URL is not specified')


class ClientError(Exception):

    def __init__(self, code, message, error):
        Exception.__init__(self, "%d: %s - %s" % (code, message, error))
        self.code = code
        self.message = message
        self.error = error
