"""Endpoints Class file."""

# import base64
# import json
import requests
# import time

from apiclient.discovery import build
from google.auth import default, jwt
from google.auth import credentials as creds
from oauth2client import client


class Endpoints(object):
    """Endpoints class."""

    class Client(object):
        """Endpoints Client class."""

        def __init__(
            self,
            api_key=None,
            base_url='http://localhost:8080',
            api='api',
            version='v1',
            verbose=False,
        ):
            """Initialize a class instance."""
            self.api = api
            self.api_key = api_key
            self.base_url = base_url
            self.verbose = verbose
            self.version = version

            self.api_url = '{}/_ah/api/{}/{}'.format(self.base_url, self.api, self.version)

            # generate discovery url
            self.discovery_url = '{}/_ah/api/discovery/v1/apis/{}/{}/rest'.format(
                self.base_url,
                self.api,
                self.version
            )

            # create credentials from the id_token
            self.credentials = self.create_credentials()

            # create a service connection
            self.service = build(
                self.api,
                self.version,
                developerKey=self.api_key,
                discoveryServiceUrl=self.discovery_url,
                credentials=self.credentials
            )

        def create_credentials(self):
            """Create credentials for talking to an endpoints API."""
            id_token = self.get_id_token_new()
            credentials = creds.Credentials()
            credentials.token = id_token
            return credentials

        def get_id_token_new(self):
            """Return an ID token that can be used to create credentials."""
            credentials, project = default()
            iam = build('iamcredentials', 'v1', credentials=credentials)

            # create audience
            audience = '{}/web-client-id'.format(self.base_url)

            # create service account name
            email = '{}@appspot.gserviceaccount.com'.format(project)
            name = 'projects/-/serviceAccounts/{}'.format(email)

            # create body for request
            body = {
                'audience': audience,
                'delegates': [],
                'includeEmail': True,
            }

            # return token
            return iam.projects().serviceAccounts().generateIdToken(
                name=name,
                body=body,
            ).execute().get('token')

        #
        # Basic Methods (GET, POST, etc.)
        #
        def delete(self, path, credentials=None):
            """Return the response from a DELETE request."""
            url = '{}/{}'.format(self.api_url, path)

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }

            if credentials:
                credentials.apply(headers)

            params = {
                'key': self.api_key
            }

            response = requests.delete(
                url,
                headers=headers,
                params=params,
                verify=False,
            )
            response.raise_for_status()
            return response.json()

        def get(self, path, credentials=None, limit=None, pageToken=None):
            """Return the response from a GET request."""
            url = '{}/{}'.format(self.api_url, path)

            headers = {
                'Accept': 'application/json',
            }

            if credentials:
                credentials.apply(headers)

            params = {
                'key': self.api_key
            }

            if limit:
                params['limit'] = limit
            if pageToken:
                params['pageToken'] = pageToken

            # print(json.dumps(headers, indent=2, sort_keys=True)

            response = requests.get(
                url,
                params=params,
                headers=headers,
                verify=False
            )
            response.raise_for_status()
            return response.json()

        def post(self, path, data, credentials=None):
            """Return the response from a POST request."""
            url = '{}/{}'.format(self.api_url, path)

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }

            if credentials:
                credentials.apply(headers)

            params = {
                'key': self.api_key
            }

            response = requests.post(
                url,
                headers=headers,
                params=params,
                json=data,
                verify=False,
            )
            response.raise_for_status()
            return response.json()

        def put(self, path, data, credentials=None):
            """Return the response from a PUT request."""
            url = '{}/{}'.format(self.api_url, path)

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }

            if credentials:
                credentials.apply(headers)

            params = {
                'key': self.api_key
            }

            response = requests.put(
                url,
                headers=headers,
                params=params,
                json=data,
                verify=False,
            )

            response.raise_for_status()
            return response.json()

        def get_list(self, path, limit=None, credentials=None):
            """Return a list of all items from a request."""
            response = self.get(path, limit=limit, credentials=credentials)
            if not response:
                return []
            items = response.get('items', [])
            pageToken = response.get('nextPageToken')
            while pageToken:
                response = self.get(path, limit=limit, pageToken=pageToken, credentials=credentials)
                items += response.get('items', [])
                pageToken = response.get('nextPageToken')
            return items

        def get_paged_list(self, request, params={}):
            """Return a list of all items from a request."""
            response = request.list(**params).execute()
            if not response:
                return []
            items = response.get('items', [])
            pageToken = response.get('nextPageToken')
            while pageToken:
                params['pageToken'] = pageToken
                response = request.list(**params).execute()
                items += response.get('items', [])
                pageToken = response.get('nextPageToken')
            return items

        def get_dict(self, path, credentials=None, limit=None, key='id'):
            """Return a dict of items from a resquest."""
            items = self.get_list(path, limit, credentials)
            data = {}
            for i in items:
                k = i.get(key)
                data[k] = i
            return data

        def to_dict(self, items, key='id'):
            """Return a dict of items."""
            data = {}
            duplicates = []
            for i in items:
                k = i.get(key)
                if k not in data:
                    data[k] = i
                else:
                    duplicates.append(i)
            return data, duplicates
