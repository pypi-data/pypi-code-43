""" This file exposes endpoints from the SWS Identity Service
"""
import datetime

from requests.auth import HTTPBasicAuth

from sws_py_sdk.service import Service

class Identity(Service):

    def __init__(self, sws):
        super().__init__(sws)
        self.service_uri = sws.service_uris['id']

    def token_refresh(self, refresh_token):
        """ Endpoint for refreshing access tokens
            refresh_token : string
                Refresh token for user that proves they deserve a new access token.
        """
        return self.fetch(
            auth=None,
            endpoint='/api/v1/me/tokens/refresh',
            body={'refresh_token': refresh_token},
            method='POST'
        )

    def login(self, email_address, password, device_id='', device_name=''):
        """ Logs user in with Basic auth
            email_address : str
                User's email address
            password : str
                User's password
            device_id : str
                Some identifier of the machine
            device_name : str
                Human readable name of machine
        """
        return self.fetch(
            auth=HTTPBasicAuth(username=self.sws.app_id, password=self.sws.secret),
            endpoint='/api/v1/login',
            body={
                'email_address': email_address,
                'password': password,
                'device_id': device_id,
                'device_name': device_name
            },
            method='POST'
        )

    def post_users(self, email_address, password, first_name=None, last_name=None, locale=None):
        """ Creates user via the /users endpoint
            email_address : str
                User's email address
            password : str
                User's password
            timestamp : datetime
                The time now, in ISO 8601 format
            first_name : str
                User's first name
            last_name : str
                User's last name
            locale : str
                Either the two letter ISO 639-1 language code,
                or the language code followed by an underscore,
                then the ISO 3166-1 alpha-2 country code.
        """
        return self.fetch(
            auth=HTTPBasicAuth(username=self.sws.app_id,
                               password=self.sws.secret),
            endpoint='/api/v1/users',
            body={
                'email_address': email_address,
                'password': password,
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'first_name': first_name,
                'last_name': last_name,
                'locale': locale
            },
            method='POST'
        )
    def post_groups(self, group_name):
        """ Adds the authenticated client user to a user group
            group_name : str
                User group name
        """
        endpoint = '/api/v1/me' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id)
        endpoint += '/groups'
        return self.fetch(
            auth='bearer',
            endpoint=endpoint,
            body={
                "group_name": group_name
            },
            method='POST'
        )
