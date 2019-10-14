

class Response(object):

    def __init__(self, request_id, code, data):
        self.code = code        # code = 0 表示成功
        self.data = data
        self.message = ""
        self.request_id = request_id
    
    def set_message(self, message):
        self.message = message
    
    @classmethod
    def load_from_dict(cls, data):
        if not isinstance(data, dict):
            raise Exception("Invalid data type, dict is expected, but {} found".format(type(data)))
        return cls(data["request_id"], data["code"], data["data"])
    
    def json(self):
        r = {
            "code": self.code,
            "data": self.data,
            "message": self.message,
            "request_id": self.request_id,
        }
        return r
