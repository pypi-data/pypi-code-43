from .authenticator import Authenticator
from base64 import b64encode, b64decode
from urllib.parse import urlparse
import requests
import time
import json


class BackupService(Authenticator):
    def __init__(self, service_url, client_key_id, shared_secret, **kwargs):
        self.service_url = service_url
        self.service_token = 'BackupService'
        self.timeout = kwargs.get('timeout', 5)
        super().__init__(client_key_id, shared_secret, **kwargs)

    def create_signed_upload_links(self, backup_policy, backup_type, backup_name):
        path = '/backups/{}/{}/{}'.format(backup_policy, backup_type, backup_name)

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def get_signed_download_links(self, backup_policy, backup_type, backup_name, backup_id):
        path = '/backups/{}/{}/{}/{}'.format(backup_policy, backup_type, backup_name, backup_id)

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.get(self.service_url + path, headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def list_backups(self, backup_policy, backup_type):
        path = '/backups/{}/{}'.format(backup_policy, backup_type)

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.get(self.service_url + path, headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))
