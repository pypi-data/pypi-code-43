from random import randint
from urllib.parse import urljoin

import requests

from quotes_api.config import DEFAULT_URL
from quotes_api.exceptions import InvalidQuote


class QuotesClient:
    def __init__(self):
        self.session = requests.Session()

    def get_quotes(self):
        response = self.session.get(DEFAULT_URL)
        return response.json()["quotes"]

    def get_quote(self, id):
        if id not in range(0, 19):
            raise InvalidQuote("only 1 at 10 is a valid quote")

        url = urljoin(DEFAULT_URL, str(id))
        response = self.session.get(url)
        return response.json()["quote"]

    def get_random_quote(self):
        quote_number = randint(0, 10)
        return self.get_quote(quote_number)
