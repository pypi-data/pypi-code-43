import requests

from lib.logging import error

class Http(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def get(self, url):
        response = requests.get(url, auth=(self.user, self.password))

        if response.status_code == 401:
            error('unauthorized access')
            exit(1)

        return response.text