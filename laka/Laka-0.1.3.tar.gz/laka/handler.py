from .errors import ResponseCodeError, ResponseTypeError


class Handler(object):
    CommandCode = None
    Param = None

    def __init__(self):
        self.param = None

    def get_param(self, cmd):
        if not self.Param:
            return
        self.param = self.Param.load_from_cmd(cmd)


class HandlerResponse(object):
    pass


class HandlerFailed(HandlerResponse):

    def __init__(self, code):
        if code is None:
            raise ResponseCodeError("response code should not be None")
        self.code = code
        self.data = None


class HandlerOK(HandlerResponse):
    code = None

    def __init__(self, data):
        if self.code is None:
            raise ResponseCodeError("response code should not be None")
        if data and not isinstance(data, dict):
            raise ResponseTypeError("response type error, dict is expected but {} found".format(type(data)))
        self.data = data
    
    @classmethod
    def set_success_code(cls, code):
        cls.code = code