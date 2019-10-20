from example.schema import TestSchema
from schemazer.commons.errors import RequestErrors
from tests.base import BaseTestCase


class TestHeaders(BaseTestCase):
    def test_get_method_with_required_header(self):
        response = self.get(
            f'/headers.withRequiredParameter',
            headers={'Apikey': self.apikey})
        assert response.status_code == 200
        assert response.json['headers']['Apikey'] == self.apikey

    def test_post_method_with_required_header(self):
        response = self.post(
            '/headers.withRequiredParameter',
            headers={'Apikey': self.apikey})
        assert response.status_code == 200
        assert response.json['headers']['Apikey'] == self.apikey

    def test_get_method_with_required_and_default_header(self):
        response = self.get(
            '/headers.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['headers']['Apikey'] ==
                TestSchema.headers.withRequiredAndDefaultParameter.headers[
                    0].default)

    def test_post_method_with_required_and_default_header(self):
        response = self.post(
            '/headers.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['headers']['Apikey'] ==
                TestSchema.headers.withRequiredAndDefaultParameter.headers[
                    0].default)

    def test_post_method_missing_required_header(self):
        response = self.post(
            '/headers.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'Apikey'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code

    def test_get_method_missing_required_header(self):
        response = self.get(
            '/headers.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'Apikey'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code
