import requests
import json
import ecdsa
import binascii
import time
import uuid
import base64
import hashlib
import urllib
import jsonpickle


class HttpClient:
    def __init__(self, baseUri, keyName, privateKey):
        self.keyName = keyName
        self.privateKey = privateKey
        self.baseUri = baseUri
        self.publicKey = ecdsa.SigningKey.from_string(
            binascii.unhexlify(self.privateKey), curve=ecdsa.NIST256p)

    def get(self, path):
        return requests.get(self._buildUrl(path), headers=self._getAuthHeader("get", self._buildUrl(path)))

    def getWithParams(self, path, queryParams):
        url = self._buildUrl(path)
        if len(queryParams.keys()) > 0:
            url += "?"

        absoluteUri = (url + urllib.parse.urlencode(queryParams)).lower()
        return requests.get(self._buildUrl(path), params=queryParams, headers=self._getAuthHeader("get", absoluteUri))

    def post(self, path, body):
        jsonEncoded = jsonpickle.encode(body)
        return requests.post(self._buildUrl(path), data=jsonEncoded, headers=self._getAuthHeader("post", self._buildUrl(path), jsonEncoded))

    def put(self, path, body):
        jsonEncoded = jsonpickle.encode(body)
        return requests.put(self._buildUrl(path), data=jsonEncoded, headers=self._getAuthHeader("put", self._buildUrl(path), jsonEncoded))

    def delete(self, path):
        return requests.delete(self._buildUrl(path), headers=self._getAuthHeader("delete", self._buildUrl(path)))

    def _buildUrl(self, path):
        return (self.baseUri + path).lower()

    def _getAuthHeader(self, method, uri, body=None):
        signature = self._getSignature(method, uri, body)
        return {"Authorization": "ECDSA " + signature}

    def _getSignature(self, method, uri, body=None):
        timestamp = int(time.time())
        nounce = uuid.uuid4()

        contentHash = ""
        if body is not None:
            content = body
            signature = hashlib.sha256(content.encode("utf-8")).digest()
            base64Encoded = base64.b64encode(signature)
            contentHash = base64Encoded.decode("utf-8")

        message = method + uri + str(timestamp) + str(nounce) + contentHash
        signatureString = base64.b64encode(self.publicKey.sign(
            message.encode("utf-8"), hashfunc=hashlib.sha256))
        theSignature = self.keyName + ":" + str(timestamp) + ":" + str(nounce) + ":" + signatureString.decode("utf-8")

        return theSignature
