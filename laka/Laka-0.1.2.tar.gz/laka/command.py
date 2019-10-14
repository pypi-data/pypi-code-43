
class Command(object):

    def __init__(self, code, params, request_id):
        if not isinstance(params, dict):
            raise Exception("Invalid params type, dict is expected, but {} found".format(type(params)))
        self.code = code
        self.params = params
        self.request_id = request_id
    
    @classmethod
    def load_from_dict(cls, data):
        """
        命令格式
        {
            "code": 100
            "params": {
                "param1": data1,
                "param2": data2,
            }
        }
        """
        if not isinstance(data, dict):
            raise Exception("Invalid data type, dict is expected, but {} found".format(type(data)))
        if "code" not in data:
            raise Exception("Invalid data, code is expected but not found.")
        if "params" not in data:
            raise Exception("Invalid data, params is expected but not found.")
        return cls(data["code"], data["params"], data["request_id"])
    
    def json(self):
        r = {
            "code": self.code,
            "params": self.params,
            "request_id": self.request_id,
        }
        return r