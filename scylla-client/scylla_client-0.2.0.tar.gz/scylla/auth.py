from requests.auth import AuthBase


class HTTPJWTAuth(AuthBase):
    """Attaches HTTP Basic Authentication to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "JWT {}".format(self.token)
        return r
