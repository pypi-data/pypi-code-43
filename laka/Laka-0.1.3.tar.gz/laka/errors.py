
class ValidateParamsFailedError(Exception):
    def __init__(self, message="validate params failed"):
        Exception.__init__(self, message)


class HandlerNotFound(Exception):
    def __init__(self, message="handler not found"):
        Exception.__init__(self, message)


class ResponseCodeError(Exception):
    def __init__(self, message="invalid code for response"):
        Exception.__init__(self, message)


class ResponseTypeError(Exception):
    def __init__(self, message="response type error"):
        Exception.__init__(self, message)

class InvalidHandler(Exception):
    def __init__(self, message="invalid handler"):
        Exception.__init__(self, message)


class MakeCommandError(Exception):
    def __init__(self, message="failed to init command"):
        Exception.__init__(self, message)


class InvalidMessage(Exception):
    def __init__(self, message="invalid message"):
        Exception.__init__(self, message)


class MakeResponseError(Exception):
    def __init__(self, message="make response error"):
        Exception.__init__(self, message)

