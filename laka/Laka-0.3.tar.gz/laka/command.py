from .param import Param
from .errors import MakeCommandError


class Command(object):

    def __init__(self, code, params, request_id):
        if isinstance(params, Param):
            params = params.json()
        if not isinstance(params, dict):
            raise MakeCommandError("Invalid params type, dict is expected but {} found".format(type(param)))
        self.code = code
        self.params = params
        self.request_id = request_id
    
    @classmethod
    def load_from_dict(cls, data):
        """
        命令格式
        {
            "code": 100,
            "request_id":"123",
            "params": {
                "param1": data1,
                "param2": data2,
            }
        }
        """
        if not isinstance(data, dict):
            raise MakeCommandError("Invalid data type, dict is expected but {} found".format(type(data)))
        if "code" not in data:
            raise MakeCommandError("Invalid data, code is not found in data.")
        if "params" not in data:
            raise MakeCommandError("Invalid data, params is not found in data.")

        return cls(data["code"], data["params"], data["request_id"])
    
    def json(self):
        return self.__dict__