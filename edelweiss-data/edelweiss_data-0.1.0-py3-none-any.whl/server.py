import abc
import os
import time
import urllib.parse

import requests
# There are a few different libraries called jwt, so python can get confused which one to import.
# But api_jwt only exists in one library, so this style import makes it unambiguous.
from jwt import api_jwt


class JwtAuthBase(requests.auth.AuthBase, metaclass=abc.ABCMeta):
    """Abstract base class for authentication by a jwt. This implements the __call__ method, making it compatible with requests library"""

    def __init__(self):
        super().__init__()
        self._jwt = None

    @abc.abstractmethod
    def generate_jwt(self):
        """child classes should implement this method"""
        raise NotImplementedError

    def is_valid(self):
        if self._jwt is None:
            return False
        claims = api_jwt.decode(self._jwt, verify=False)
        exp = int(claims['exp'])
        return exp > time.time()

    def __call__(self, r):
        """This method implements the AuthBase super class. The requests library calls this method for every request"""
        if not self.is_valid():
            # jwt either does not exist or it has expired, so get a new one
            self._jwt = self.generate_jwt()
        r.headers['Authorization'] = "Bearer {}".format(self._jwt)
        return r


class Auth0Jwt(JwtAuthBase):
    """Authenticates requests by adding a jwt to each request.
       The user must sign in to Auth0 by copying a url into their web browser.

       This is an implementation of the oidc device authorization flow
       https://auth0.com/docs/flows/guides/device-auth/call-api-device-auth"""

    # TODO: We also get a refresh token using this method. We could cache it so the user
    # does not need to visit browser each time.

    def __init__(self, client_id="uW5NZfAifU5srB3lZFVWzxjdS9H8YdP0",
                 domain="edelweiss.eu.auth0.com",
                 cache_jwt=True,
                 token_dir=None):

        self.token_dir = token_dir if token_dir is not None else os.path.expanduser(os.path.join("~", ".edelweiss"))
        self.client_id = client_id
        self.domain = domain
        self.cache_jwt = cache_jwt
        super().__init__()

    @property
    def refresh_token_path(self):
        return os.path.join(self.token_dir, "refresh_token_{}".format(self.client_id))

    def _fetch_device_code(self):
        url = "https://{}/oauth/device/code".format(self.domain)
        payload = {"client_id": self.client_id, "scope": "openid offline_access email"}
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()

    def _prompt_user(self, device_code_response):
        print("Visit this url in your web browser to sign into edelweiss:")
        print(device_code_response["verification_uri_complete"])
        print("Your authorization token is {}".format(device_code_response["user_code"]))
        print()
        print("Waiting for authentication.....")

    def _poll_token(self, device_code_response):
        url = "https://{}/oauth/token".format(self.domain)
        payload = {
            "client_id": self.client_id,
            "device_code": device_code_response["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }

        # Loop and wait for the user to authenticate.
        # Keep looping until the device code response expires.
        expires_at = time.time() + device_code_response['expires_in']
        while time.time() < expires_at:
            response = requests.post(url, data=payload)
            if response.ok:
                print("Authentication successful")
                return response.json()
            if response.json()["error"] == "authorization_pending":
                # We expect a 4xx error code if the user has not authenticated yet.
                time.sleep(device_code_response['interval'])
            else:
                response.raise_for_status()
        raise Exception("Timed out waiting for authentication")

    def authenticate_with_refresh_token(self, refresh_token):
        url = "https://{}/oauth/token".format(self.domain)
        payload = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()

    def _save_token(self, token):
        os.makedirs(self.token_dir, exist_ok=True, mode=0o700)
        fdesc = os.open(self.refresh_token_path, os.O_WRONLY | os.O_CREAT, 0o600)
        with os.fdopen(fdesc, 'w') as fh:
            fh.write(token)

    def _get_cached_refresh_token(self):
        try:
            with open(self.refresh_token_path, "r") as fh:
                return fh.read()
        except FileNotFoundError:
            return None

    def generate_jwt(self):
        refresh_token = self._get_cached_refresh_token()
        if refresh_token is None:
            device_code_response = self._fetch_device_code()
            self._prompt_user(device_code_response)
            token_response = self._poll_token(device_code_response)
            if self.cache_jwt:
                self._save_token(token_response["refresh_token"])
            return token_response["id_token"]
        else:
            token_response = self.authenticate_with_refresh_token(refresh_token)
            return token_response["id_token"]


class DevJwt(JwtAuthBase):
    """Authentication to be used in development only.
       Creates a self-signed jwt without going to Auth0. This is helpful when the dev server is configured to accept self-signed jwt"""

    def __init__(self, email="user@example.com"):
        self._email = email
        super().__init__()

    def generate_jwt(self):
        claims = {
            'exp': int(time.time()) + 3600,
            'email': self._email,
            'email_verified': True,
        }
        jwt = api_jwt.encode(claims, 'secret', algorithm='HS256')
        return str(jwt, 'utf-8')


class Server:
    def __init__(self, base_url):
        self.base_url = base_url
        self.auth = None

    def _absolute_url(self, route):
        return urllib.parse.urljoin(self.base_url, route)

    def authenticate(self, *args, development=False, **kwargs):
        if development:
            self.auth = DevJwt(*args, **kwargs)
        else:
            self.auth = Auth0Jwt(*args, **kwargs)

    def _handle_response(self, response):
        response.raise_for_status()
        return None if response.status_code == 204 else response.json()

    def get(self, route, json=None, data=None):
        '''Sends a GET request to a server.

        :returns: dict with the JSON response.
        :param route: route to which the request will be sent
        :param json: dict with the JSON body to send
        :param data: raw body to send
        '''
        response = requests.get(self._absolute_url(route), json=json, data=data, auth=self.auth)
        return self._handle_response(response)

    def post(self, route, json=None, data=None):
        '''Sends a POST request to a server.

        :returns: dict with the JSON response.
        :param route: route to which the request will be sent
        :param json: dict with the JSON body to send
        :param data: raw body to send
        '''
        response = requests.post(self._absolute_url(route), json=json, data=data, auth=self.auth)
        return self._handle_response(response)

    def upload(self, route, files):
        '''Uploads a POST request that uploads files to a server.

        :returns: dict with the JSON response.
        :param route: route to which the request will be sent
        :param files: a dictionary of files in which the keys are filenames
          and corresponding values are file objects
        '''
        response = requests.post(self._absolute_url(route), files=files, auth=self.auth)
        return self._handle_response(response)

    def delete(self, route):
        '''Sends a DELETE request to a server.

        :returns: dict with the JSON response.
        :param route: route to which the request will be sent
        '''
        response = requests.delete(self._absolute_url(route), auth=self.auth)
        return self._handle_response(response)
