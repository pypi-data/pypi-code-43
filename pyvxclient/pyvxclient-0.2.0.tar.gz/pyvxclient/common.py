import json as json_lib


class ApiResponse(object):

    def __init__(self, json=None, status_code=None):
        self.status_code = status_code
        self.json = json

    def __str__(self):
        return json_lib.dumps({"status_code": self.status_code, "json": self.json})
