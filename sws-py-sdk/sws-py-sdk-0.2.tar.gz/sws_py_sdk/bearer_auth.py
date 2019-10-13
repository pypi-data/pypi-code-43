from requests.auth import AuthBase

class BearerAuth(AuthBase):

    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, request):
        """ When instance is called it will set correct bearer auth for the request
            request : Request
                Instance of Requests.Request
        """
        request.headers['Authorization'] = "Bearer %s" %self.access_token
        return request