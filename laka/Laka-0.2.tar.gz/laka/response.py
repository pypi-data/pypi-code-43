from .errors import MakeResponseError


class Response(object):

    def __init__(self, request_id, code, data, message):
        self.code = code
        self.data = data
        self.message = message
        self.request_id = request_id
    
    @classmethod
    def load_from_dict(cls, data):
        if not isinstance(data, dict):
            raise MakeResponseError("Invalid data type, dict is expected, but {} found".format(type(data)))
        if not data.get("request_id"):
            raise MakeResponseError("request_id is necessary for response")
        if data.get("code", None) is None:
            raise MakeResponseError("code is necessary for response")
        return cls(data["request_id"], data["code"], data.get("data"), data.get("message"))
    
    def json(self):
        return self.__dict__

