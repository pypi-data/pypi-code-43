

class Scenario(object):
    def __init__(self, path, operation, response_code, response_body=None):
        if response_body is None:
            response_body = {}
        self.path = self.__remove_trailing_slash_from_path(path)
        self.operation = operation.upper()
        self.response_code = int(response_code)
        self.response_body = response_body

    def matches(self, path, operation):
        path = self.__remove_trailing_slash_from_path(path)
        return path == self.path and operation.upper() == self.operation

    def get_expected_response(self):
        return {
            'responseCode': self.response_code,
            'responseBody': self.response_body
        }

    def __remove_trailing_slash_from_path(self, path):
        if path.endswith('/'):
            path = path[:-1]
        return path
