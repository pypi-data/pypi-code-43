import os
import base64
import json
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding


class PasswordManager(object):

    def __init__(self, endpoint=os.environ.get("GSENHA_ENDPOINT"),
                user=os.environ.get("GSENHA_USER"), password=os.environ.get("GSENHA_PASS"),
                key=os.environ.get("GSENHA_KEY", os.environ.get("GSENHA_KEY_PATH")), verify=None):
        self._token = None
        self._user = user
        self._pass = password
        self._verify = verify
        self._rsa_verifier = self._load_key(key)
        self._headers = {
            "Content-Type": "application/json"
        }
        self._gsenha_endpoint = endpoint

        self._get_token()


    def _load_key(self, gsenha_key):
        if gsenha_key and os.path.exists(gsenha_key):
            with open(gsenha_key) as opened_key:
                gsenha_key = opened_key.read()
        try:
            return load_pem_private_key(gsenha_key.encode('ascii'), password=None, backend=default_backend())
        except ValueError:
            raise Exception("key load error")

    def _get_token(self):

        token_response = requests.post("%s/login" % self._gsenha_endpoint,
            headers=self._headers,
            data=json.dumps({
                "username": self._user,
                "password": self._pass
            }), verify=self._verify)

        if token_response.ok:
            token_json = token_response.json()
            if token_json:
                self._token = token_json.get("token")

    def _get_password(self, folder, name):
        headers = self._headers.copy()
        headers["Authorization"] = "Bearer %s" % self._token
        response = requests.post(
            "%s/search/password" % self._gsenha_endpoint,
            headers=headers,
            data=json.dumps({
                "folder": folder,
                "name": name
            }), verify=self._verify)
        password_json = response.json()
        if password_json.get("status") == "success":
            return password_json.get("password")

    def _decrypt(self, value):
        raw_cipher_data = base64.b64decode(value)
        return str(self._rsa_verifier.decrypt(raw_cipher_data, padding.PKCS1v15()).decode('utf-8'))

    def get_passwords(self, folder, *names):
        return_passwords = dict()
        for name in names:
            password = self._get_password(folder, name)
            if password:
                return_passwords[name] = {
                    "url": self._decrypt(password["url"]),
                    "login": self._decrypt(password["login"]),
                    "password": self._decrypt(password["passwd"]),
                    "description": self._decrypt(password["description"]),
                }
        return return_passwords
