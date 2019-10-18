import requests
import ecdsa
import binascii
import time
import uuid
import base64
import hashlib
import jsonpickle

try:
    #python2
    from urllib import urlencode
except ImportError:
    #python3
    from urllib.parse import urlencode

class HttpClient:
    def __init__(self, base_uri, key_name, private_key):
        self.keyName = key_name
        self.privateKey = private_key
        self.base_uri = base_uri
        self.publicKey = ecdsa.SigningKey.from_string(
            binascii.unhexlify(self.privateKey), curve=ecdsa.NIST256p)

    def get(self, path):
        return requests.get(self._build_url(path), headers=self._get_auth_header("get", self._build_url(path)))

    def get_with_params(self, path, query_params):

        url = self._build_url(path)
        if len(query_params.keys()) > 0:
            url += "?"

        absolute_uri = (url + urlencode(query_params)).lower()
        return requests.get(
            self._build_url(path),
            params=query_params,
            headers=self._get_auth_header("get", absolute_uri)
        )

    def post(self, path, body):
        json_encoded = jsonpickle.encode(body, unpicklable=False)
        return requests.post(
            self._build_url(path),
            data=json_encoded,
            headers=self._get_auth_header("post", self._build_url(path), json_encoded)
        )

    def put(self, path, body):
        json_encoded = jsonpickle.encode(body,  unpicklable=False)
        return requests.put(
            self._build_url(path),
            data=json_encoded,
            headers=self._get_auth_header("put", self._build_url(path), json_encoded)
        )

    def delete(self, path):
        return requests.delete(
            self._build_url(path),
            headers=self._get_auth_header("delete", self._build_url(path))
        )

    def _build_url(self, path):
        return (self.base_uri + path)

    def _get_auth_header(self, method, uri, body=None):
        signature = self._get_signature(method, uri, body)
        return {"Authorization": "ECDSA " + signature}

    def _get_signature(self, method, uri, body=None):
        timestamp = int(time.time())
        nounce = uuid.uuid4()

        content_hash = ""
        if body is not None:
            content = body
            signature = hashlib.sha256(content.encode("utf-8")).digest()
            base64_encoded = base64.b64encode(signature)
            content_hash = base64_encoded.decode("utf-8")

        message = method + uri.lower() + str(timestamp) + str(nounce) + content_hash
        signature_string = base64.b64encode(self.publicKey.sign(
            message.encode("utf-8"), hashfunc=hashlib.sha256))
        the_signature = self.keyName + ":" + str(timestamp) + ":" + str(nounce) + ":" + signature_string.decode("utf-8")

        return the_signature
