import mock
import unittest

from pymysql.err import OperationalError
from sqlalchemy import exc

from dq.errors import RecoverableError
from dq import retry


class TestRetry(unittest.TestCase):

    def test_recoverable_error(self):
        e = RecoverableError('recoverable')
        assert retry.recoverable_error(e)

    @mock.patch('dq.retry.Session.rollback')
    def test_sql_or_recoverable_error_sql(self, mock_rollback):
        e = OperationalError(2013, 'meow')
        assert retry.sql_or_recoverable_error(e)
        mock_rollback.assert_called()

    @mock.patch('dq.retry.Session.rollback')
    def test_sql_or_recoverable_error_sqlalchemy(self, mock_rollback):
        e = exc.TimeoutError()
        assert retry.sql_or_recoverable_error(e)
        mock_rollback.assert_called()

    @mock.patch('dq.retry.Session.rollback')
    def test_sql_or_recoverable_error_sqlalchemy_not(self, mock_rollback):
        e = exc.NoSuchTableError()
        assert not retry.sql_or_recoverable_error(e)
        mock_rollback.assert_called()

    def test_sql_or_recoverable_error_recoverable(self):
        e = RecoverableError('recoverable')
        assert retry.sql_or_recoverable_error(e)
