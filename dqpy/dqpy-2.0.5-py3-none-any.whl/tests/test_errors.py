import unittest

from dq import errors


class TestErrors(unittest.TestCase):

    def test_recoverable_error(self):
        e = errors.RecoverableError('recoverable')
        assert e.status_code == 500
        assert e.message == 'recoverable'
        assert e.to_dict() == {'error': 'Internal Error'}
        assert e.__str__() == '500 - recoverable'
        assert e.__repr__() == (
            '<RecoverableError - status: 500, message: recoverable>')

    def test_model_error(self):
        e = errors.ModelError('model')
        assert e.status_code == 500
        assert e.message == 'model'

    def test_integration_error(self):
        e = errors.IntegrationError(None)
        assert e.status_code == 500
        assert not e.message
        assert e.__str__() == '500 - Unspecified DQ Error'

    def test_internal_error(self):
        e = errors.InternalError(None)
        assert e.status_code == 500
        assert not e.message
        assert e.__str__() == '500 - Unspecified DQ Error'

    def test_invalid_input_error(self):
        e = errors.InvalidInputError('invalid')
        assert e.status_code == 400
        assert e.to_dict() == {'error': 'invalid'}
        assert e.__str__() == '400 - invalid'

    def test_not_found_error(self):
        e = errors.NotFoundError()
        assert e.status_code == 404
        assert e.message == 'Not found'

    def test_unauthorized_error(self):
        e = errors.UnauthorizedError()
        assert e.status_code == 401
        assert e.message == 'Unauthorized'

    def test_forbidden_error(self):
        e = errors.ForbiddenError()
        assert e.status_code == 403
        assert e.message == 'Forbidden'
