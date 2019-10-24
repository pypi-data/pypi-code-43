import json

import requests

BASE_URL = 'http://dadard.fr:7000/api/v1/'
SUB_CHECK_ENDPOINT = 'sub'
PROFILE_CHECK_ENDPOINT = 'profile/infos'
STATUS_OK = 'ok'
STATUS_KO = 'ko'
TRUE = 'true'
FALSE = 'false'


class CommonCaller(object):
    def __init__(self, api_name, profile_key):
        self.profile_key = profile_key
        self.api_name = api_name

    def check_sub_and_key(self):
        return self.check_profile_key() and self.check_is_subscribed()

    def check_profile_key(self):
        params = "api_key={pk}".format(pk=self.profile_key)
        url = f"{BASE_URL}{PROFILE_CHECK_ENDPOINT}?{params}"

        r = requests.get(url)
        status = json.loads(r.content.decode())['status']
        if status == STATUS_OK:
            return True

        return False

    def call_sub(self):
        params = "api_name={an}&api_key={pk}".format(an=api_name, pk=profile_key)
        url = f"{BASE_URL}{SUB_CHECK_ENDPOINT}?{params}"

        r = requests.get(url)
        return json.loads(r.content.decode())

    def check_is_subscribed(self):
        response = call_sub(profile_key, api_name)
        status = response['status']
        if status == STATUS_OK:
            is_subscribed = response['content']['is_subscribed']
            if is_subscribed == TRUE:
                return True

        return False

    def check_is_not_subscribed(self):
        response = call_sub(profile_key, api_name)
        status = response['status']
        if status == STATUS_OK:
            is_subscribed = response['content']['is_subscribed']
            if is_subscribed == FALSE:
                return True

        return False
