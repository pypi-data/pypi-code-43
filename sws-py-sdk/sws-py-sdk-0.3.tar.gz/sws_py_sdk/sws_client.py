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
        super().__init__(app_id=app_id, secret=secret, user_id=user_id, timeout=timeout, service_uri=service_uri, invalid_access_token_handler=self._handle_invalid_access_token)
        self.auto_refresh = auto_refresh
        self.access_token_updated_callback = None

    def set_access_token_updated_callback(self, callback):
        """
        Sets a callback for when the access token has been updated when auto_refresh is true.
        :param function callback: Callback to execute when the access token has been updated.
        :return: Nothing.
        """
        self.access_token_updated_callback = callback

    def _handle_invalid_access_token(self, service, response):
        """
        Handles the case where a response came back from a service where the access token was not valid or was expired.

        If `auto_refresh` is true, will attempt to refresh the access token then attempt to make the last request again,
        otherwise returns the original response.

        :param Service service: The service which failed to fulfill a request due to an invalid access token.
        :param requests.Response response: The response given due to the invalid access token.
        :return: A HTTP response.
        :rtype: requests.Response
        """
        if self.auto_refresh:
            last_request = service.last_request
            response = self.identity().token_refresh(self.refresh_token)
            #   This token refresh request may have resulted in an error that was
            #   handled by a custom error handler.

            data = response.json()

            if 'tokens' in data:
                #   Update the access token property
                self.access_token = data['tokens']['access']['token']
                #   Call the callback
                if self.access_token_updated_callback:
                    self.access_token_updated_callback(
                      token=self.access_token,
                      expires=datetime.datetime.utcfromtimestamp(data['tokens']['access']['expires_at'])
                    )

                #   Set a new Authorization header for the request
                last_request.headers['Authorization'] = f'Bearer {self.access_token}'

                #   Re-execute the 'last request'
                return service.fetch_request(last_request)
        return response

