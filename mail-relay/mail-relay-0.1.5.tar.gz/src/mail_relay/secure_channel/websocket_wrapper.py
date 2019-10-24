from pvHelpers.logger import g_log
from pvHelpers.utils import EncodingException, jloads, utf8Decode
import websocket


WS_READ_TIMEOUT = 0.1
WS_CONN_TIMEOUT = 4


class WSData:
    def __init__(self, data):
        self.message = data


class WSNoData:
    def __init__(self):
        pass


class WSError:
    def __init__(self, message=u''):
        self.message = message


class WSWebSocketWrapper:
    '''client-side low level websocket wrapper'''

    def __init__(self, path, conn_timeout=WS_CONN_TIMEOUT, read_timeout=WS_READ_TIMEOUT):
        self.websocket = websocket.create_connection(path, timeout=conn_timeout)
        self.websocket.settimeout(read_timeout)

    def receive(self):
        try:
            opcode, data = self.websocket.recv_data(control_frame=True)
        except websocket.WebSocketTimeoutException as e:
            return WSNoData()
        except websocket.WebSocketException as e:
            g_log.exception(e)
            return WSError(u'WSWebSocketWrapper.receive: excepion: {}'.format(e))

        if opcode in [websocket.ABNF.OPCODE_PING, websocket.ABNF.OPCODE_PONG]:
            return WSNoData()
        elif opcode == websocket.ABNF.OPCODE_CLOSE:
            return WSError(u'WSWebSocketWrapper.receive: Close frame recevied')
        elif opcode == websocket.ABNF.OPCODE_BINARY:
            return WSError('WSWebSocketWrapper.receive: Binary frame not expected')

        if data is None:
            return WSError(u'WSWebSocketWrapper.receive: Data can\'t be None')

        try:
            data = jloads(utf8Decode(data))
        except EncodingException as e:
            g_log.exception(e)
            return WSError(u'WSWebSocketWrapper.receive: Failed to parse json')

        return WSData(data)

    def send(self, data):
        self.websocket.send(data)

    def close(self):
        try:
            return self.websocket.close()
        except (ValueError, websocket.WebSocketException) as e:
            g_log.exception(e)
