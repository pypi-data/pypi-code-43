import hashlib
import json
import time
from base64 import b64encode

import requests


class Client:
    _auth_base_url = 'https://iam.bluemix.net/identity/token'

    def __init__(self, api_key, app_id, client_secret, base_path='https://imfpush.eu-de.bluemix.net/imfpush/v1/apps'):
        """

        :param base_path: the path of your regional server default: https://imfpush.eu-de.bluemix.net/imfpush/v1/apps
        :param api_key:
        :param app_id:
        :param client_secret:
        """
        self.client_secret = client_secret
        self.app_id = app_id
        self.api_key = api_key
        self._access_token = None
        self._refresh_token = None
        self._expiration = None
        self._token_type = None
        self._user = None
        self._basic_auth = 'Basic %s' % b64encode(b"bx:bx").decode("utf-8")
        self._push_base_url = base_path

    def _set_access_token(self):
        """

        sets the auth header for requests to ibm cloud
        """
        data = {
            'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': self.api_key
        }
        response = requests.post(self._auth_base_url, data, headers={'Authorization': self._basic_auth})
        response.raise_for_status()
        response_dict = json.loads(response.text) if response.text else response.status_code
        self._access_token = response_dict['access_token']
        self._refresh_token = response_dict['refresh_token']
        self._expiration = response_dict['expiration']
        self._token_type = response_dict['token_type']
        self._user = response_dict['ims_user_id']

    def _refresh_access_token(self):
        """

        renews the auth token
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
            'apikey': self.api_key
        }
        response = requests.post(self._auth_base_url, data,
                                 headers={'apikey': self.api_key, 'Authorization': self._basic_auth})
        response.raise_for_status()
        response_dict = json.loads(response.text) if response.text else response.status_code
        self._access_token = response_dict['access_token']
        self._refresh_token = response_dict['refresh_token']
        self._expiration = response_dict['expiration']
        self._token_type = response_dict['token_type']

    def get_auth_header(self):
        """

        :return: auth header for requests to ibm cloud
        """
        if self._expiration and self._expiration > time.time():
            self._refresh_access_token()
        else:
            self._set_access_token()

        return "%s %s" % (self._token_type, self._access_token)

    def register_device(self, token, platform, device_id=None):
        """

        :param token:
        :param platform: A (Apple) , G (Google)
        :param device_id:
        """
        if not device_id:
            device_id = hashlib.md5(token.encode()).hexdigest()
        # try to remove device from system first
        try:
            self.delete_device(device_id)
        except:
            # device not in system
            pass

        data = {
            'deviceId': device_id,
            'platform': platform,
            'token': token
        }
        response = requests.post("%s/%s/devices" % (self._push_base_url, self.app_id), json.dumps(data),
                                 headers={'Content-Type': 'application/json', 'clientSecret': self.client_secret})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def delete_device(self, token=None, device_id=None):
        """

        :param token:
        :param device_id:
        """
        if not device_id and token:
            device_id = hashlib.md5(token.encode()).hexdigest()
        elif not device_id:
            raise Exception("enter either token or device_id")

        response = requests.delete("%s/%s/devices/%s" % (self._push_base_url, self.app_id, device_id),
                                   headers={'clientSecret': self.client_secret})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_subscriptions(self, topic="", device_id="", offset=0, size=100, expand=False):
        """

        :param topic: specify a topic to get the subscribers for it
        :param device_id: specify a deviceId, to get all subscriptions for the device
        :param offset: set a offset for pagination, default 0
        :param size: set the pagination size default=100, maximum 500
        :param expand: if True, retrieve additional information for the results
        """
        response = requests.get("%s/%s/subscriptions?offset=%s&size=%s&expand=%s&deviceId=%s&tagName=%s" % (
            self._push_base_url, self.app_id, offset, size, expand, device_id, topic),
                                headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_device(self, device_id=None, token=None):
        """

        :param device_id:
        :param token:  optional if device id unknown
        :return:
        """
        if not device_id and token:
            device_id = hashlib.md5(token.encode()).hexdigest()
        elif not device_id:
            raise Exception("enter either token or device_id")
        response = requests.get(
            "%s/%s/devices/%s" % (self._push_base_url, self.app_id, device_id),
            headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_devices(self, offset=0, size=100, expand=False):
        """

        :param offset: set a offset for pagination, default 0
        :param size: set the pagination size default=100, maximum 500
        :param expand: if True, retrieve additional information for the results
        """
        response = requests.get(
            "%s/%s/devices?offset=%s&size=%s&expand=%s" % (self._push_base_url, self.app_id, offset, size, expand),
            headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_device_stats(self, days=1):
        """

        requires a premium account to retrieve the stats
        :param days: days from today to return device registration stats
        """
        response = requests.get("%s/%s/devices/report?days=%s" % (self._push_base_url, self.app_id, days),
                                headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_push_stats(self, days=1):
        """

        requires a premium account to retrieve the stats
        :param days: days from today to return push stats
        """
        response = requests.get("%s/%s/messages/report?days=%s" % (self._push_base_url, self.app_id, days),
                                headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_messages(self, offset=0):
        """

        :param offset:
        :return: {
                  "messages": [
                    {
                      "createdTime": "2017-07-08T13:43:10.000Z",
                      "messageId": "fnDWK8bG",
                      "alert": "Sample message text",
                      "href": "http://server/imfpush/v1/myapp/messages/fnDWK8bG"
                    }
                  ]
                }
        """
        response = requests.get("%s/%s/messages/?offset=%s" % (self._push_base_url, self.app_id, offset),
                                headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_message(self,message_id):
        """

        :param message_id:
        :return: Message response object
        """
        response = requests.get("%s/%s/messages/%s" % (self._push_base_url, self.app_id, message_id),
                                headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_message_status(self,message_id):

        """

        :param message_id:
        :return: message send status object
        """
        response = requests.get("%s/%s/messages/%s/status" % (self._push_base_url, self.app_id, message_id),
                                headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def get_message_delivery_status(self,message_id,device_id=""):
        """

        :param message_id:
        :param device_id:
        :return: message send delivery_status object
        """
        response = requests.get("%s/%s/messages/%s/deliverystatus?deviceId=%s" % (self._push_base_url, self.app_id, message_id,device_id),
                                headers={'clientSecret': self.client_secret, 'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def register_topic(self, name, description=""):
        """

        :param name:
        :param description:
        """
        data = {
            'name': name,
            'description': description
        }
        response = requests.post("%s/%s/tags" % (self._push_base_url, self.app_id), json.dumps(data),
                                 headers={'Content-Type': 'application/json', 'clientSecret': self.client_secret,
                                          'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def delete_topic(self, name):
        """

        :param name:
        """
        response = requests.delete("%s/%s/tags/%s" % (self._push_base_url, self.app_id, name),
                                   headers={'clientSecret': self.client_secret,
                                            'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def subscribe(self, topic, device_id=None, token=None):
        """

        :param topic:
        :param device_id:
        :param token: optional if device_id unknown
        """

        if not device_id and token:
            device_id = hashlib.md5(token.encode()).hexdigest()
        elif not device_id:
            raise Exception("enter either token or device_id")

        data = {
            'deviceId': device_id,
            'tagName': topic
        }
        response = requests.post("%s/%s/subscriptions" % (self._push_base_url, self.app_id), json.dumps(data),
                                 headers={'Content-Type': 'application/json', 'clientSecret': self.client_secret})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def unsubscribe(self, topic, device_id=None, token=None):
        """

        :param topic:
        :param device_id:
        :param token: optional if device_id unknown
        """

        if not device_id and token:
            device_id = hashlib.md5(token.encode()).hexdigest()
        elif not device_id:
            raise Exception("enter either token or device_id")

        response = requests.delete(
            "%s/%s/subscriptions?deviceId=%s&tagName=%s" % (self._push_base_url, self.app_id, device_id, topic),
            headers={'Content-Type': 'application/json', 'clientSecret': self.client_secret})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code

    def send_message(self, alert, url=None,
                     platforms=["A", "G"],
                     payload="", device_ids=None, topics=None, badge=1, ttl=3600, type='DEFAULT', title=None,
                     subtitle=None,
                     validate=True):
        """

        :param alert: Message to display
        :param url: default None
        :param platforms: default ["A", "G"], Options are . 'A' for apple (iOS) devices, 'G' for google (Android) devices
        :param payload: default "", optional json string with data to be sent
        :param device_ids: default [], optional if not topics set
        :param topics: default [], optional if not device_ids set
        :param badge: default 1
        :param ttl: default 3600
        :param type: default ["DEFAULT"], opdtions are ['DEFAULT', 'MIXED', 'SILENT']
        :param title: optional
        :param subtitle:  optional IOS only
        :param validate: optional validate device targets
        """
        data = {
            "target": {"platform": platforms},
            "message": {
                "alert": alert
            },
            "settings": {
                "gcm": {
                    "timeToLive": ttl
                },
                "apns": {
                    "timeToLive": ttl
                }
            }
        }
        if topics:
            data["target"]["tagNames"] = topics
        elif device_ids:
            data["target"]["deviceIds"] = device_ids
        if payload:
            data["settings"]["gcm"]["payload"] = payload
            data["settings"]["apns"]["payload"] = payload
        if badge:
            data["settings"]["apns"]["badge"] = badge
        if url:
            data["message"]["url"] = url
        if type:
            data["settings"]["gcm"]["type"] = type
            data["settings"]["apns"]["type"] = type
        if title:
            data["settings"]["gcm"]["androidtitle"] = title
            data["settings"]["apns"]["title"] = title
        if subtitle:
            data["settings"]["apns"]["subtitle"] = title
        if validate:
            data["validate"] = validate

        response = requests.post("%s/%s/messages" % (self._push_base_url, self.app_id), json.dumps(data),
                                 headers={'Content-Type': 'application/json', 'clientSecret': self.client_secret,
                                          'Authorization': self.get_auth_header()})
        response.raise_for_status()
        return json.loads(response.text) if response.text else response.status_code
