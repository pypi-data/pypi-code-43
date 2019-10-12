import unittest

from example.app import create_app
from example.schema import TestSchema
from schemazer import RequestValidator


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.validator = RequestValidator()
        self.schema = TestSchema()
        self.app = create_app()
        self.client = self.app.test_client()

        self.email = 'example@mail.ru'
        self.apikey = 'da0fbb5f-f453-40d0-9975-07f8daf3aa43'
        self.token = '070fbb5f-f453-40d0-9975-07f8daf3aa43'

    def post(self, url, data=None, **kwargs):
        return self.client.post(url, json=data or {}, **kwargs)

    def get(self, url, **kwargs):
        return self.client.get(url, **kwargs)
