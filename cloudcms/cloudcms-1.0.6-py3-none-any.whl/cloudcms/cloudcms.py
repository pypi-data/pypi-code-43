import json
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from .connection_config import ConnectionConfig
from .platform import Platform
from .request_error import RequestError

class CloudCMS:

    def __init__(self):
        pass

    def connect(self, **kwargs):
        if 'filename' in kwargs:
            with open(kwargs['filename']) as f:
                data = json.load(f)
                self.config = ConnectionConfig(data)
        else:
            self.config = ConnectionConfig(kwargs)
        
        session = OAuth2Session(client=LegacyApplicationClient(client_id=self.config.client_id))
        self.token = session.fetch_token(token_url=self.config.token_url,
                                username=self.config.username,
                                password=self.config.password,
                                client_id=self.config.client_id,
                                client_secret=self.config.client_secret)

        return self.get_platform()

    def token_updater(self, token):
        self.token = token

    def get(self, uri, params={}, output_json=True):
        return self.request('GET', uri, params, output_json=output_json)

    def post(self, uri, params={}, data={}):
        return self.request('POST', uri, params, data)

    def upload(self, uri, name, file, mimetype, params={}):
        files = { 'upload_file': (name, file, mimetype) }
        return self.request('POST', uri, params, files=files)

    def put(self, uri, params={}, data={}):
        return self.request('PUT', uri, params, data)

    def delete(self, uri, params={}):
        return self.request('DELETE', uri, params)

    def request(self, method, uri, params={}, data={}, headers={}, output_json=True, **kwargs):
        # Add "full" to params if not there
        if not 'full' in params:
            params['full'] = True

        # Convert param values to json
        paramsJson = {}
        for (key, param) in params.items():
            if isinstance(param, str):
                paramsJson[key] = param
            else:
                paramsJson[key] = json.dumps(param) 

        url = self.config.base_url + uri

        session = OAuth2Session(client=LegacyApplicationClient(client_id=self.config.client_id),
                                token=self.token,
                                auto_refresh_kwargs=self.config.extra(),
                                auto_refresh_url=self.config.token_url,
                                token_updater=self.token_updater)
                                
        if method == 'GET' or method == 'DELETE':
            response = session.request(method, url, params=paramsJson, headers=headers, **kwargs)
        else:
            response = session.request(method, url, json=data, params=paramsJson, headers=headers, **kwargs)

        if output_json:
            res = response.json()
            if 'error' in res and res['error']:
                raise RequestError(res)
        else:
            res = response.content


        return res

    def get_platform(self):
        data = self.get('')
        return Platform(self, data)
