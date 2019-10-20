from example.schema import TestSchema
from schemazer.commons.errors import RequestErrors
from tests.base import BaseTestCase


class TestCookies(BaseTestCase):
    def test_get_method_with_required_cookie(self):
        self.client.set_cookie('localhost', 'apikey', self.apikey)
        response = self.get(
            f'/cookies.withRequiredParameter')
        assert response.status_code == 200
        assert response.json['cookies']['apikey'] == self.apikey

    def test_post_method_with_required_cookie(self):
        self.client.set_cookie('localhost', 'apikey', self.apikey)
        response = self.post(
            '/cookies.withRequiredParameter')
        assert response.status_code == 200
        assert response.json['cookies']['apikey'] == self.apikey

    def test_get_method_with_required_and_default_cookie(self):
        response = self.get(
            '/cookies.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['cookies']['apikey'] ==
                TestSchema.cookies.withRequiredAndDefaultParameter.cookies[
                    0].default)

    def test_post_method_with_required_and_default_cookie(self):
        response = self.post(
            '/cookies.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['cookies']['apikey'] ==
                TestSchema.cookies.withRequiredAndDefaultParameter.cookies[
                    0].default)

    def test_post_method_missing_required_cookie(self):
        response = self.post(
            '/cookies.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'apikey'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code

    def test_get_method_missing_required_cookie(self):
        response = self.get(
            '/cookies.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'apikey'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code
