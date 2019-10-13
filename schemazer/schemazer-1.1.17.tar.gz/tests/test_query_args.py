import unittest

from commons.errors import RequestErrors
from example.schema import TestSchema
from tests.base import BaseTestCase


class TestQueryArgs(BaseTestCase):
    def test_get_method_with_required_parameter(self):
        response = self.get(
            f'/args.withRequiredParameter?email={self.email}')
        assert response.status_code == 200
        assert response.json['args']['email'] == self.email

    def test_post_method_with_required_parameter(self):
        response = self.post(
            '/args.withRequiredParameter',
            {'email': self.email})
        assert response.status_code == 200
        assert response.json['args']['email'] == self.email

    def test_get_method_with_required_and_default_parameter(self):
        response = self.get(
            '/args.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['args']['email'] ==
                TestSchema.args.withRequiredAndDefaultParameter.parameters[
                    0].default)

    def test_post_method_with_required_and_default_parameter(self):
        response = self.post(
            '/args.withRequiredAndDefaultParameter')
        assert response.status_code == 200
        assert (response.json['args']['email'] ==
                TestSchema.args.withRequiredAndDefaultParameter.parameters[
                    0].default)

    def test_post_method_missing_required_parameter(self):
        response = self.post(
            '/args.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'email'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code

    def test_get_method_missing_required_parameter(self):
        response = self.get(
            '/args.withRequiredParameter')
        assert response.status_code == 200
        assert 'error' in response.json
        assert response.json['error']['failure_param'] == 'email'
        assert response.json['error']['code'] == RequestErrors.BadRequest.code

    def test_post_method_args_to_type_converter(self):
        int_as_string = '123'
        response = self.post(
            '/args.withRequiredAndDefaultParameter',
            {'int': int_as_string}
        )
        assert response.status_code == 200
        assert 'args' in response.json
        assert 'int' in response.json['args']
        assert response.json['args']['int'] == int(int_as_string)

    def test_get_method_args_to_type_converter(self):
        int_as_string = '123'
        response = self.get(
            '/args.withRequiredAndDefaultParameter?int=123'
        )
        assert response.status_code == 200
        assert 'args' in response.json
        assert 'int' in response.json['args']
        assert response.json['args']['int'] == int(int_as_string)


if __name__ == '__main__':
    unittest.main()
