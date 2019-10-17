import requests


SINGLE = 'single'
SEQUENCE = 'sequence'
CYCLE = 'cycle'


class MockDupError(Exception):
    pass


class Mock:
    def __init__(self, data):
        self.data = data

    def delete(self):
        """
        delete mock on server and return its info - {is_expired: bool}
        """
        resp = requests.delete(self.data['url'])

        resp.raise_for_status()

        return resp.json()


class MockServer:
    def __init__(self, url='http://127.0.0.1:8080/mocker_api/mocks/'):
        self.url = url

    def create_mock(self, data):
        """
        :param data: dict with keys:
          'name' - optional, '' by default
          'route' - for example '/some_path'
          'method' - a http method like GET, POST, PUT, etc
          'response_type' - optional, choice from ['single', 'sequence', 'cycle'], 'single' by default
          'responses' - list of dicts with keys (or just dict if response_type is single):
            'body' - response body
            'return_code' - http status code, like 200
            'headers' - dict with http headers
        :returns Mock object
        """
        resp = requests.post(self.url, json=data)

        if resp.status_code == 409:
            raise MockDupError(resp.content)

        resp.raise_for_status()

        return Mock(resp.json())

    def create_mocks(self, list_data):
        """
        :param list_data: list of dicts with keys:
          'name' - optional, '' by default
          'route' - for example '/some_path'
          'method' - a http method like GET, POST, PUT, etc
          'response_type' - optional, choice from ['single', 'sequence', 'cycle'], 'single' by default
          'responses' - list of dicts with keys (or just dict if response_type is single):
            'body' - response body
            'return_code' - http status code, like 200
            'headers' - dict with http headers
        :returns list of Mock objects
        """
        resp = requests.post(self.url, json=list_data)

        if resp.status_code == 409:
            raise MockDupError(resp.content)

        resp.raise_for_status()

        return [Mock(m) for m in resp.json()]
