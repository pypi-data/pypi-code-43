import json
import logging
import sys
import traceback

import websocket


class WebSocket:
    procedures = []
    logger = logging.getLogger(__name__)

    @staticmethod
    def send_message(**kwrags):

        host = kwrags.get('host')
        logger = kwrags.get('logger')

        if not host:
            raise Exception(f'host is not exists.')

        port = kwrags.get('port')
        if not port:
            raise Exception(f'port not exists.')

        if not isinstance(port, int):
            port = int(port)

        channel = kwrags.get('channel')
        if not channel:
            raise Exception(f'channel is not exists.')

        message = kwrags.get('message')
        if not message:
            raise Exception(f'message is not exists.')

        if not isinstance(message, dict):
            raise Exception(f'message is not dict instance')

        try:
            url = f'ws://{host}:{port}/ws/{channel}/'
            ws = websocket.create_connection(url)
            ws.send(json.dumps(message))
            ws.close()
        except Exception as ex:

            exc_info = sys.exc_info()
            message = str(ex)
            stackTrace = traceback.format_exception(*exc_info)

            logging.error(message)

            for x in stackTrace:
                logger.error(x)

            del exc_info

    def on_message(self, message):
        for proc in self.procedures:
            if hasattr(proc, '__call__'):
                proc(message)

    def on_error(self, error):
        self.logger.error(error)

    def on_close(self):
        self.logger.debug(f'### closed ###')

    def on_open(self):
        self.logger.debug(f'### opened ###')

    def remove_proc(self, proc):
        self.procedures.remove(proc)

    def append_proc(self, proc):
        self.procedures.append(proc)

    def send(self, data):
        if isinstance(data, dict):
            self.webSocket.send(json.dumps(data))
        else:
            raise Exception(f'data is not dict.')

    def send_logging(self, msg, type='logging'):
        data = dict(msg=msg, type=type)
        # self.webSocket.send(json.dumps(data))

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

        websocket.enableTrace(True)
        self.webSocket = websocket.WebSocketApp(f'ws://{self.host}:{self.port}/ws/{self.channel}/',
                                                on_message=self.on_message,
                                                on_error=self.on_error,
                                                on_close=self.on_close,
                                                on_open=self.on_open
                                                )
        self.webSocket.run_forever()
