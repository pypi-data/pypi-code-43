import sys
import threading
import time

import requests


class Dutate(object):
    def __init__(self, token):

        self.headers = {
            'Authorization': 'Bearer %s' % token
        }
        self.python_version = int('%d%d' % (sys.version_info[0], sys.version_info[1]))

    def _track_event(self, event_name, extra=None):

        payload = {
            'name': event_name,
            'extra': extra,
            'timestamp': int(time.time())
        }

        url = 'https://api.dutate.com/track/event/%s/' % event_name
        requests.post(url, json=payload, headers=self.headers)

    def track(self, event_name, extra=None):
        threading.Thread(target=self._track_event, args=(event_name, extra)).start()
