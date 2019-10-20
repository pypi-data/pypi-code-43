from example.schema import TestSchema
from schemazer.commons.errors import RequestErrors
from tests.base import BaseTestCase


class TestSystemParameters(BaseTestCase):
    def test_get_method_system_parameter_from_query(self):
        response = self.get(
            f'/systems.withRequiredParameter?token={self.token}')
        assert response.status_code == 200
        assert response.json['systems']['token'] == self.token

    def test_post_method_system_parameter_from_query(self):
        response = self.post(
            '/systems.withRequiredParameter',
            {'token': self.token})
        assert response.status_code == 200
        assert response.json['systems']['token'] == self.token

    def test_get_method_system_parameter_from_header(self):
        response = self.get(
            f'/systems.withRequiredParameter',
            headers={'Auth-Token': self.token}
        )
        assert response.status_code == 200
        assert response.json['systems']['token'] == self.token

    def test_post_method_system_parameter_from_header(self):
        response = self.post(
            '/systems.withRequiredParameter',
            {},
            headers={'Auth-Token': self.token})
        assert response.status_code == 200
        assert response.json['systems']['token'] == self.token

    def test_get_method_system_parameter_from_cookie(self):
        self.client.set_cookie('localhost', 'auth_token', self.token)
        response = self.get(
            f'/systems.withRequiredParameter')
        assert response.status_code == 200
        assert response.json['systems']['token'] == self.token

    def test_post_method_system_parameter_from_cookie(self):
        self.client.set_cookie('localhost', 'auth_token', self.token)
        response = self.post(
            '/systems.withRequiredParameter',
            {})
        assert response.status_code == 200
        assert response.json['systems']['token'] == self.token

    def test_post_method_missing_required_system_parameter(self):
        response = self.post(
            '/systems.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'token'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code

    def test_get_method_missing_required_system_parameter(self):
        response = self.get(
            '/systems.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'token'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code

    def test_get_method_default_system_parameter(self):
        response = self.get(
            '/systems.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['systems']['token'] ==
                TestSchema.systems.withRequiredAndDefaultParameter.systems[
                    0].default)

    def test_post_method_default_system_parameter(self):
        response = self.post(
            '/systems.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['systems']['token'] ==
                TestSchema.systems.withRequiredAndDefaultParameter.systems[
                    0].default)
