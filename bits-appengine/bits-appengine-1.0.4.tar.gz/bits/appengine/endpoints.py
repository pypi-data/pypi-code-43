# -*- coding: utf-8 -*-
"""Endpoints Class file."""

import requests
import time

from apiclient.discovery import build
from google.auth import default, jwt
from oauth2client import client


class Endpoints(object):
    """Endpoints class."""

    class Client(object):
        """Endpoints Client class."""

        def __init__(
            self,
            api_key=None,
            base_url='http://localhost:8080',
            api='bitsdb',
            version='v1',
            verbose=False,
        ):
            """Initialize a class instance."""
            self.api = api
            self.api_key = api_key
            self.base_url = base_url
            self.verbose = verbose
            self.version = version

            self.api_url = '%s/_ah/api/%s/%s' % (self.base_url, self.api, self.version)

            # generate discovery url
            self.discovery_url = '%s/_ah/api/discovery/v1/apis/%s/%s/rest' % (
                self.base_url,
                self.api,
                self.version
            )

            # create credentials from the id_token
            self.credentials = client.AccessTokenCredentials(
                self.get_id_token(),
                'my-user-agent/1.0'
            )

            # create a bitsdb service connection
            self.service = build(
                self.api,
                self.version,
                developerKey=self.api_key,
                discoveryServiceUrl=self.discovery_url,
                credentials=self.credentials
            )

        def generate_signed_jwt(self):
            """Generate a signed java web token for service account."""
            # generate default credentials
            credentials, _ = default()

            # get time now
            now = int(time.time())

            # create jwt payload
            payload = {
                # issued at - time
                'iat': now,
                # expires after one hour.
                'exp': now + 3600,
                # issuer - client email
                'iss': credentials.service_account_email,
                # the URL of the target service.
                'target_audience': '{}/web-client-id'.format(self.base_url),
                # Google token endpoints URL
                'aud': 'https://www.googleapis.com/oauth2/v4/token'
            }

            # sign the payload with the signer
            return jwt.encode(credentials.signer, payload)

        def get_id_token(self):
            """Return an access token for connecting to BITSdb."""
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            params = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': self.generate_signed_jwt()
            }
            url = 'https://www.googleapis.com/oauth2/v4/token'
            # send the JWT to Google Token endpoints to request Google ID token
            return requests.post(url, data=params, headers=headers).json().get('id_token')
