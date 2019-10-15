"""
An asynchronous client for Google Cloud KMS
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
import io
from typing import Dict
from typing import Optional
from typing import Union

from gcloud.rest.auth import SyncSession  # pylint: disable=no-name-in-module
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import Token  # pylint: disable=no-name-in-module

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session

try:
    import ujson as json
except ImportError:
    import json  # type: ignore

API_ROOT = 'https://cloudkms.googleapis.com/v1'
LOCATION = 'global'
SCOPES = [
    'https://www.googleapis.com/auth/cloudkms',
]


class KMS(object):
    def __init__(self, keyproject     , keyring     , keyname     ,
                 service_file                                  = None,
                 location      = LOCATION, session                    = None,
                 token                  = None)        :
        self.api_root = ('{}/projects/{}/'
                         'locations/{}/keyRings/{}/'
                         'cryptoKeys/{}'.format((API_ROOT), (keyproject), (location), (keyring), (keyname)))

        self.session = SyncSession(session)
        self.token = token or Token(service_file=service_file, scopes=SCOPES,
                                    session=self.session.session)

    def headers(self)                  :
        token = self.token.get()
        return {
            'Authorization': 'Bearer {}'.format((token)),
            'Content-Type': 'application/json',
        }

    # https://cloud.google.com/kms/docs/reference/rest/v1/projects.locations.keyRings.cryptoKeys/decrypt
    def decrypt(self, ciphertext     ,
                      session                    = None)       :
        url = '{}:decrypt'.format((self.api_root))
        body = json.dumps({
            'ciphertext': ciphertext,
        }).encode('utf-8')

        s = SyncSession(session) if session else self.session
        resp = s.post(url, headers=self.headers(), data=body)

        plaintext      = (resp.json())['plaintext']
        return plaintext

    # https://cloud.google.com/kms/docs/reference/rest/v1/projects.locations.keyRings.cryptoKeys/encrypt
    def encrypt(self, plaintext     ,
                      session                    = None)       :
        url = '{}:encrypt'.format((self.api_root))
        body = json.dumps({
            'plaintext': plaintext,
        }).encode('utf-8')

        s = SyncSession(session) if session else self.session
        resp = s.post(url, headers=self.headers(), data=body)

        ciphertext      = (resp.json())['ciphertext']
        return ciphertext
