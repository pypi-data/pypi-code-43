from requests import Response


class Error(Exception):
    def __init__(self, req: Response):
        self.status_code = req.status_code
        self.text = req.text
        self.url = req.url
        Exception.__init__(self, f'code: {self.status_code} body: `{self.text}` url: {self.url}')


class UnauthorizedError(Exception):
    pass


class NotFoundError(Exception):
    pass


class Forbidden(Exception):
    def __init__(self, token):
        Exception.__init__(self, f"Your tokens permission `{token.permission}` is not high enough.")
