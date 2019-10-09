import http.client
import json

from urllib.parse import urlparse


class Ghee:
    def __init__(self, webhook_url):
        self.headers = {'Content-type': 'application/json; charset=UTF-8'}
        self.url = urlparse(webhook_url)

    @property
    def connection(self):
        return http.client.HTTPSConnection(self.url.netloc)

    def __call__(self, message):
        return self.echo(message)

    def echo(self, message):
        return self._send(message)
    
    def _send(self, message):
        foo = {'text': message}
        json_data = json.dumps(foo)

        self.connection.request('POST', self.url.geturl(), json_data, self.headers)

        try:
            response = self.connection.getresponse()
        except http.client.ResponseNotReady:
            return 'could not get response frome the api'
        else:
            return response.read().decode()