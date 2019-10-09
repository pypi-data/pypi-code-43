import json
import requests

class PUBGClient:
    BASE_URL = 'https://api.pubg.com/'
    def __init__(self, api_key):
        self.session = requests.Session()
        self.unlimited_session = requests.Session()

        headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': 'Bearer {}'.format(api_key),
                }

        self.session.headers.update(headers)

    def request(self, query):
        endpoint = query.get_endpoint()
        response = self.session.get(endpoint, timeout = 30)
        if response.status_code != 200:
            print('error: status: {}'.format(response.status_code))
            return ''

        return json.loads(response.text)
