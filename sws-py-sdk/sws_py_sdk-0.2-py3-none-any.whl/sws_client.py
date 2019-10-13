import datetime

from .sws import Sws
""" This is the client.
    It needs a nice description.
"""
class SwsClient(Sws):

    def __init__(self, app_id, secret=None, user_id=0, timeout=3000, service_uri={}, auto_refresh=True):
        """
        Here we set up a mechanism for token refresh to be handled and triggered
        Create SWS object
        config : object
            Configuration options
        appId : str
            Application ID
        secret : str
            Application secret
        user_id : int
            End user ID
        timeout : float
            Request timeout
        service_uri : object
            Base URIs for SWS services
        service_uri.id : str
            Base URI for SWS ID Service
        service_uri.license : str
            Base URI for SWS License Service
        auto_refresh : boolean
            Determines if the client will attempt to refresh the access token if invalid or expired.
        """
        super().__init__(app_id=app_id, secret=secret, user_id=user_id, timeout=timeout, service_uri=service_uri, auto_refresh=auto_refresh)
        if auto_refresh:
            self.set_invalid_access_token_handler(self.handle_invalid_access_token)


    """ Python does not support inline functions very well
        So the handle function is defined here
    """
    def handle_invalid_access_token(self, err):
        # `err.client` is the specific client instance that made the inital request
        # when the `invalid access token` error was received.
        client = err.client
        # Fetch the `last request` object from the service client
        request = client.last_request

        response = self.identity().token_refresh(self.refresh_token)
        #   This token refresh request may have resulted in an error that was
        #   handled by a custom error handler.

        data = response.json()
        
        if 'tokens' in data:
            #   Update the access token property
            self.access_token = data['tokens']['access']['token']
            #   Call the callback
            client.access_token_updated_handler(
              token=self.access_token,
              expires=datetime.datetime.utcfromtimestamp(data['tokens']['access']['expires_at'])
            )
            #   Set a new Authorization header for the request
            del request.headers['Authorization']
            request= client.sws.bearer_auth(r=request)

            #   Re-execute the 'last request'
            return client.fetch_request(request)

