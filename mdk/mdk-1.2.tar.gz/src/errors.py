"""Define exceptions used by mdk"""

class AuthenticationError(Exception):
    """Raised when an API authentication attempt fails"""
    def __init__(self, message):
        super(AuthenticationError, self).__init__(message)
        self.message = message


class ConfigError(Exception):
    """Raised when a config file cannot be used by mdk as expected"""
    def __init__(self, message):
        super(ConfigError, self).__init__(message)
        self.message = message


class InitializationError(Exception):
    """Raised when a config file cannot be used by mdk as expected"""
    def __init__(self, message):
        super(InitializationError, self).__init__(message)
        self.message = message


class HTTPError(Exception):
    """Raised when an HTTP request fails"""
    def __init__(self, message):
        super(HTTPError, self).__init__(message)
        self.message = message

class RequestError(Exception):
    """Raised when an API authentication attempt fails"""
    def __init__(self, message):
        super(RequestError, self).__init__(message)
        self.message = message


class ServiceError(Exception):
    """Raised when something goes wrong with a docker-compose service"""
    def __init__(self, message):
        super(ServiceError, self).__init__(message)
        self.message = message
