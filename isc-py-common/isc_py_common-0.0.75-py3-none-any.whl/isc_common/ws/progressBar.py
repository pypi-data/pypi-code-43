import json

import websocket


class ProgressBar:
    host = None
    port = None
    channel = None
    user_id = None
    id = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

        if not self.host:
            raise Exception(f'Not specified a host.')

        if not self.port:
            raise Exception(f'Not specified a port.')

        if not self.channel:
            raise Exception(f'Not specified a channel.')

        if not self.id:
            raise Exception(f'Not specified a id.')

    def _send(self, message):
        if not isinstance(message, dict):
            raise Exception(f'Message must be a dict.')
        url = f'ws://{self.host}:{self.port}/ws/{self.channel}/'

        ws = websocket.create_connection(url)
        ws.send(json.dumps(message))
        ws.close()

    def show(self):
        self._send(dict(type='show_progress', progressBarId=self.id))

    def close(self):
        self._send(dict(type='close_progress', progressBarId=self.id))

    def setTitle(self, title):
        self._send(dict(type='set_title_progress', title=title, progressBarId=self.id))

    def setPercentsDone(self, percent):
        self._send(dict(type='set_percent_done_progress', percent=percent, progressBarId=self.id))
