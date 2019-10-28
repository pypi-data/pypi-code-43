import json

import websocket


class ProgressStack:
    host = None
    port = None
    channel = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

        if not self.host:
            raise Exception(f'Not specified a host.')

        if not self.port:
            raise Exception(f'Not specified a port.')

        if not self.channel:
            raise Exception(f'Not specified a channel.')

    def _send(self, message):
        if not isinstance(message, dict):
            raise Exception(f'Message must be a dict.')
        url = f'ws://{self.host}:{self.port}/ws/{self.channel}/'

        ws = websocket.create_connection(url)
        ws.send(json.dumps(message))
        ws.close()

    def show(self, title, label_contents, id):
        self._send(dict(
            labelContents=label_contents,
            progressBarId=id,
            title=title,
            type='show_progress',
        ))

    def close(self, id):
        self._send(dict(type='close_progress', progressBarId=id))

    def setContentsLabel(self, labelContents, id):
        self._send(dict(type='set_contents_label', labelContents=labelContents, progressBarId=id))

    def setTitleProgress(self, title, id):
        self._send(dict(type='set_title_progress', title=title, progressBarId=id))

    def setPercentsDone(self, percent, id):
        self._send(dict(type='set_percent_done_progress', percent=percent, progressBarId=id))
