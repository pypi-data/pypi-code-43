from inscribe.errors import InscribeAPIException
import json
import pysher
import requests
import time

class PusherFactory():
    def __init__(self, pusher_key: str, base_url: str, user_id: str, api_key: str):
        self.pusher_key = pusher_key
        self.base_url = base_url
        self.user_id = user_id
        self.api_key = api_key
        self.channel = None
        self._setup_pusher()
    
    def get_pusher_channel(self):
        time.sleep(5)
        return self.channel
    
    def _setup_pusher(self):
        self.pusher = pysher.Pusher(self.pusher_key, cluster="us3")
        self.pusher.connection.bind('pusher:connection_established', self._pusher_connect_handler)
        self.pusher.connect()

    def _pusher_connect_handler(self, data):
        socket_id = json.loads(data)['socket_id']
        channel_name = f"private-inscribe-user_{self.user_id}"
        auth_token = self._get_pusher_auth(socket_id, channel_name).split(":")[1]
        self.channel = self.pusher.subscribe(channel_name, auth=f"{self.pusher_key}:{auth_token}")
    
    def _get_pusher_auth(self, socket_id, channel_name):
        try:
            response = requests.post(f"{self.base_url}/pusher/auth/", data={
                'socket_id': socket_id,
                'channel_name': channel_name
            }, headers={'Authorization': self.api_key})

            if response.status_code == 200:
                return response.json()['auth']
            else:
                self.pusher.disconnect()
                raise InscribeAPIException("Could not authenitcate, check your user_id and api_key.") 
        except requests.exceptions.HTTPError:
            self.pusher.disconnect()
            raise InscribeAPIException("Could not authenticate pusher stream.")
        except ValueError:
            self.pusher.disconnect()
            raise InscribeAPIException("Could not parse pusher authentication response from API.")
