
import http.client
import json

from urllib.parse import urlparse


class Ghee:
    def __init__(self, webhook_url):
        self.headers = {'Content-type': 'application/json; charset=UTF-8'}
        self.url = urlparse(webhook_url)
        self.connection = http.client.HTTPSConnection(self.url.netloc)
        
    def echo(self, message):
        return self._send(message)
    
    def _send(self, message):
        foo = {'text': message}
        json_data = json.dumps(foo)

        self.connection.request('POST', self.url.geturl(), json_data, self.headers)

        response = self.connection.getresponse()
        print(response.read().decode())