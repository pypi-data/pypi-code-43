import os
import json

import requests

class AkevaAdapter():
    '''
    Initializes a AkevaAdapter. 
    Host can be the name of the secret manager kubernetes pod as well as its internal IP address. Its recommended to use its name.
    '''
    def __init__(self, host=None, port=None):
        if host is None:
            host = os.environ['GCS_SECRET_MANAGEMENT_HOST'] if 'GCS_SECRET_MANAGEMENT_HOST' in os.environ else '0.0.0.0'
        if port is None:
            port = os.environ['GCS_SECRET_MANAGEMENT_PORT'] if 'GCS_SECRET_MANAGEMENT_PORT' in os.environ else 80
        self.host = host
        self.port = port

    def _get_host(self):
        return f'{self.host}:{self.port}'
    
    def _get_secrets_uri(self, resource):
        host = self._get_host()
        return f'http://{host}/api/secrets/{resource}'

    def _create_request(self, resource):
        return requests.request("GET", self._get_secrets_uri(resource))

    def get(self, secret_name):
        '''
        Returns a dict which contains secret data of the secret.
        '''
        response = self._create_request(f'read?secret_name={secret_name}')
        
        if response.status_code == 400:
            raise AkevaBadRequest(response, 'read')

        if response.status_code != 200:
            raise AkevaSMError(response, 'read')

        return response.json()

    def list(self):
        '''
        Returns a dict which contains secret data of all secrets
        '''
        response = self._create_request(f'read/all')
        
        if response.status_code == 400:
            raise AkevaBadRequest(response, 'read all')

        if response.status_code != 200:
            raise AkevaSMError(response, 'read all')

        return response.json()

    def put(self, secret_data):
        '''
        Takes in secret as a dict and stores it in GCS under secret_name.
        `secret_name` must be specified in secret_data.

        Returns dict json message on success.
        '''
        fields='&'.join([f'{key}={value}' for (key, value) in secret_data.items()])
        response = self._create_request(f'write?{fields}')

        if response.status_code == 400:
            raise AkevaBadRequest(response, 'write')

        if response.status_code != 200:
            raise AkevaSMError(response, 'write')

        return response.json()

    def delete(self, secret_name):
        '''
        Deletes a secret.

        Returns dict json message on success. 
        '''
        response = self._create_request(f'delete?secret_name={secret_name}')
        
        if response.status_code == 400:
            raise AkevaBadRequest(response, 'read')

        if response.status_code != 200:
            raise AkevaSMError(response, 'read')

        return response.json()

class AkevaBadRequest(Exception):
    '''
    Creates a bad request exception. It is returned from the secret manager when the user has specified wrong parameters.
    The request_type is used to determine the type of request we were making (so read / read all / write / delete)
    '''
    def __init__(self, response, request_type):
        super().__init__(self._get_message(response, request_type))
    
    def _get_message(self, response, request_type):
        request_type_error_message = self._get_request_type_error_message(request_type)
        resp_str = json.dumps(response.json())
        return f'Error {request_type_error_message}. Response: {resp_str}. Status code: {response.status_code}.'
    
    def _get_request_type_error_message(self, request_type):
        switch = {
            'read': 'reading secret',
            'read all': 'reading all secrets',
            'write': 'writing secret',
            'delete': 'deleting secret',
        }
        return switch.get(request_type, 'UNKNOWN')

class AkevaSMError(Exception):
    '''
    Creates a bad request exception. It is returned from the secret manager when the user has specified wrong parameters.
    The request_type is used to determine the type of request we were making (so read / read all / write / delete)
    '''
    def __init__(self, response, request_type):
        super().__init__(self._get_message(response, request_type))
    
    def _get_message(self, response, request_type):
        request_type_error_message = self._get_request_type_error_message(request_type)
        return f'Secret Manager gave an error during {request_type_error_message}: {response.reason}. Status code: {response.status_code}.'
    
    def _get_request_type_error_message(self, request_type):
        switch = {
            'read': 'reading secret',
            'read all': 'reading all secrets',
            'write': 'writing secret',
            'delete': 'deleting secret',
        }
        return switch.get(request_type, 'UNKNOWN')


### CACHING, default_caching i init i seconds. Allow storing it in secret
### Writing should delete the cache!