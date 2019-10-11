"""Endpoints Class file."""

import httplib2
import requests
import time

from apiclient.discovery import build
from google.auth import crypt, jwt
from oauth2client import client
from google.oauth2 import service_account


class Endpoints(object):
    """Endpoints class."""

    class Client(object):
        """Endpoints Client class."""

        def __init__(
            self,
            api_key=None,
            base_url='http://localhost:8080',
            api='bitsdb',
            service_account_file='etc/service_account.json',
            version='v1',
            verbose=False,
        ):
            """Initialize a class instance."""
            self.api = api
            self.api_key = api_key
            self.base_url = base_url
            self.service_account_json_file = service_account_file
            self.verbose = verbose
            self.version = version

            self.api_url = '%s/_ah/api/%s/%s' % (self.base_url, self.api, self.version)

            # generate discovery url
            self.discovery_url = '%s/_ah/api/discovery/v1/apis/%s/%s/rest' % (
                self.base_url,
                self.api,
                self.version
            )

            # get an id_token fro the service account
            self.id_token = self.get_id_token()

            # create credentials from the id_token
            self.credentials = client.AccessTokenCredentials(
                self.id_token,
                'my-user-agent/1.0'
            )

            # create an authorized httplib2 Http() object
            self.http = self.credentials.authorize(httplib2.Http())

            # create a bitsdb service connection
            self.service = build(
                self.api,
                self.version,
                developerKey=self.api_key,
                discoveryServiceUrl=self.discovery_url,
                http=self.http,
            )

        def generate_signed_jwt(self):
            """Generate a signed java web token for service account."""
            # get service account email address for token
            email = service_account.Credentials.from_service_account_file(
                self.service_account_json_file
            ).service_account_email

            # create a signer
            signer = crypt.RSASigner.from_service_account_file(self.service_account_json_file)

            # get time now
            now = int(time.time())

            # create jwt payload
            payload = {
                # issued at - time
                'iat': now,
                # expires after one hour.
                'exp': now + 3600,
                # issuer - client email
                'iss': email,
                # the URL of the target service.
                'target_audience': 'https://broad-bitsdb-api.appspot.com/web-client-id',
                # Google token endpoints URL
                'aud': 'https://www.googleapis.com/oauth2/v4/token'
            }

            # sign the payload with the signer
            return jwt.encode(signer, payload)

        def get_id_token(self):
            """Return an access token for connecting to BITSdb."""
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            params = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': self.generate_signed_jwt()
            }
            url = 'https://www.googleapis.com/oauth2/v4/token'
            # send the JWT to Google Token endpoints to request Google ID token
            response = requests.post(url, data=params, headers=headers)
            response.raise_for_status
            return response.json().get('id_token')
