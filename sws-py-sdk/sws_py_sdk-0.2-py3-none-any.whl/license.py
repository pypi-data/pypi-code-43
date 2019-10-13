""" This file exposes endpoints from the SWS Identity Service
"""

from requests.auth import HTTPBasicAuth

from sws_py_sdk.service import Service

class License(Service):

    def __init__(self, sws):
        super().__init__(sws)
        self.service_uri = sws.service_uris['license']

    def get_licenses(self, app_name="", app_version="", term=""):
        """ Get user's licenses
            app_name : str
                Filter by the application that license is for
            app_version : string
                Semantic version of application
            term : str
                License term: permanent, subscription,  timelimited.
        """
        return self.fetch(
            auth='bearer',
            endpoint= '/api/v1/me/licenses' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id) + '/licenses',
            body={'app_name': app_name, 'app_version': app_version, 'term': term}
        )
