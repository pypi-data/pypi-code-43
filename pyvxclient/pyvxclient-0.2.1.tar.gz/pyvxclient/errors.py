import json


class ClientError(Exception):
    default_code = None

    def __init__(self, message, code=None):
        super(ClientError, self).__init__()
        self.code = code or self.__class__.default_code
        self.message = message

    def __str__(self):
        msg = None
        try:
            msg = json.dumps(self.message)
        except:
            pass
        return '{} ({})'.format(msg, self.code) if self.code else msg


class WrongCredentials(ClientError):
    pass


class NotAuthorized(ClientError):
    pass


class NoSwaggerDef(ClientError):
    pass


class EndpointURLNotFound(ClientError):
    pass


class Forbidden(ClientError):
    default_code = 403


class BadRequest(ClientError):
    default_code = 400


class Unauthorized(ClientError):
    default_code = 401


class ServerError(ClientError):
    pass
