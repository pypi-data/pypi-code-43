class APIError(Exception):
    """def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        if self.response is not None:
            self.query_id"""
    pass


class InvalidEndpoint(APIError):
    pass


class HttpError(APIError):
    pass


class InvalidResponse(APIError):
    pass


class NetworkError(APIError):
    pass
