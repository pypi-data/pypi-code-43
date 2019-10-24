import json
import os

import requests

BASE_URL = 'http://dadard.fr:7000/api/v1/'
SUB_CHECK_ENDPOINT = 'sub'
PROFILE_CHECK_ENDPOINT = 'profile/infos'
STATUS_OK = 'ok'
STATUS_KO = 'ko'
TRUE = 'true'
FALSE = 'false'

p = {}


class CommonCaller(object):
    def __init__(self, api_name, profile_key):
        self.profile_key = profile_key
        self.api_name = api_name
        self.headers = {'Authorization': self.profile_key}

    def check_sub_and_key(self):
        return self.check_profile_key() and self.check_is_subscribed()

    def check_profile_key(self):
        url = f"{BASE_URL}{PROFILE_CHECK_ENDPOINT}"

        r = requests.get(url, headers=self.headers, proxies=p)
        status = json.loads(r.content.decode())['status']
        if status == STATUS_OK:
            return True

        return False

    def call_sub(self):
        params = "api_name={an}".format(an=self.api_name)
        url = f"{BASE_URL}{SUB_CHECK_ENDPOINT}?{params}"

        r = requests.get(url, headers=self.headers, proxies=p)
        return json.loads(r.content.decode())

    def check_is_subscribed(self):
        response = self.call_sub()
        status = response['status']
        if status == STATUS_OK:
            is_subscribed = response['content']['is_subscribed']
            if is_subscribed == TRUE:
                return True

        return False

    def check_is_not_subscribed(self):
        response = self.call_sub()
        status = response['status']
        if status == STATUS_OK:
            is_subscribed = response['content']['is_subscribed']
            if is_subscribed == FALSE:
                return True

        return False
