from pymysql.err import OperationalError
from sqlalchemy import exc

from dq.database import Session
from dq.errors import RecoverableError


def recoverable_error(exception):
    """Use as ``@retry(retry_on_exception=recoverable_error)``."""
    return isinstance(exception, RecoverableError)


def sql_or_recoverable_error(exception):
    """Retries recoverable error and SQL errors.

    This function rolls back the current session if the exception is a SQL one.
    Use as ``@retry(retry_on_exception=sql_or_recoverable_error)``.
    """
    if isinstance(exception, OperationalError):
        if exception.args[0] in (2006, 2013, 2014, 2045, 2055):
            Session.rollback()
            return True
    if isinstance(exception, exc.SQLAlchemyError):
        Session.rollback()
        return isinstance(exception, (
            exc.DisconnectionError, exc.StatementError, exc.TimeoutError,
            exc.DBAPIError,
        ))
    return recoverable_error(exception)
