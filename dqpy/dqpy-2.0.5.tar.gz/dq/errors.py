class DQError(Exception):
    """Base exception.

    Clients that wish to catch all exceptions should catch this one.
    The ``status_code`` will be set as the HTTP status code if a view handler
    triggers an error. If there is need to set the exact type of error, use
    ``error_code``.

    4xx errors are due to the user, and as such the message will be passed
    directly back to user. 5xx errors will have the message replaced by the
    generic 'Internal Error' before sending back to user.
    """

    def __init__(self, message='', status_code=None, error_code=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code or 500
        self.error_code = error_code

    def __repr__(self):
        return '<{} - status: {}, message: {}>'.format(
            self.__class__.__name__, self.status_code, self.message
        )

    def __str__(self):
        code = str(self.status_code) + ' - ' if self.status_code else ''
        message = self.message if self.message else 'Unspecified DQ Error'
        return code + message

    def to_dict(self):
        message = self.message if self.status_code < 500 else 'Internal Error'
        return {'error': message}


class RecoverableError(DQError):
    """Exception raised when a recoverable error occurs.

    This may be due to network error, timeout, etc. and is meant to be retried.
    If retrying gives no luck, this is considered a 500 error.
    """

    def __init__(self, message):
        DQError.__init__(self, message=message, status_code=500)


class ModelError(DQError):
    """Exception raised when something is wrong with the models."""

    def __init__(self, message):
        DQError.__init__(self, message=message, status_code=500)


class IntegrationError(DQError):
    """Exception raised when there is a service integration error."""

    def __init__(self, message):
        DQError.__init__(self, message=message, status_code=500)


class InternalError(DQError):
    """Exception raised when there is an internal server error."""

    def __init__(self, message):
        DQError.__init__(self, message=message, status_code=500)


class InvalidInputError(DQError):
    """Exception raised when the user input is not valid."""

    def __init__(self, message='Invalid input'):
        DQError.__init__(self, message=message, status_code=400)


class NotFoundError(DQError):
    """Exception raised when something is not found."""

    def __init__(self, message='Not found'):
        DQError.__init__(self, message=message, status_code=404)


class UnauthorizedError(DQError):
    """Exception raised when the user is not authenticated for an action."""

    def __init__(self, message='Unauthorized'):
        DQError.__init__(self, message=message, status_code=401)


class ForbiddenError(DQError):
    """Exception raised when the user does not have the required permission."""

    def __init__(self, message='Forbidden'):
        DQError.__init__(self, message=message, status_code=403)
