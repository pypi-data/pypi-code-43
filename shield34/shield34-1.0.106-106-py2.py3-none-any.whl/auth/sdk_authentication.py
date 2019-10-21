import json

import requests
import urllib3

from shield34_reporter.consts.shield34_properties import Shield34Properties
from shield34_reporter.consts.shield34_properties_constants import Shield34PropertiesConstants
from shield34_reporter.exceptions import Shield34LoginFailedException
from shield34_reporter.model.contracts.sdk_auth_credentials import SdkCredentials


class SdkAuthentication():

    isAuthorized = False
    userToken = ''


    @staticmethod
    def login():
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            Shield34Properties.initialize()
            sdkAuthCredentials = SdkCredentials(Shield34Properties.api_key, Shield34Properties.api_secret, "")
            payload = json.dumps(sdkAuthCredentials .__dict__)
            headers = {'content-type': 'application/json'}
            login_request = requests.post(Shield34Properties.api_base_url + '/auth/project-login', data = payload, headers = headers,verify=True)
            if login_request.status_code == 200:
                SdkAuthentication.isAuthorized = True
                response_as_json = login_request.json()
                SdkAuthentication.userToken = response_as_json['data']['token']
            else:
                raise Shield34LoginFailedException
        except Exception as e:
            raise Shield34LoginFailedException

    @staticmethod
    def is_authorized():
        return SdkAuthentication.isAuthorized

    @staticmethod
    def get_user_token():
        return SdkAuthentication.userToken