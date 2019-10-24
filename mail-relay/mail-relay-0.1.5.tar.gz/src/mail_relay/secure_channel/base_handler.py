import time

from pvHelpers.utils import jdumps

from .key_exchange_manager import KeyExchangeManager
from .websocket_wrapper import WSData, WSError, WSWebSocketWrapper


class SecureMessageSendingStates():
    NOT_CONNECTED = 1
    WAITING_FOR_HANDSHAKE = 2
    WAITING_FOR_HASH = 3
    WAITING_FOR_PUBLIC_KEY = 4
    WAITING_FOR_VERIFICATION = 5
    WAITING_FOR_OK = 6
    WAITING_FOR_ENCRYPTED_MESSAGE = 7
    DONE = 8


class TransferTypes(object):
    TRANSFER = u'key_transfer'


class SecureMessageManager(object):
    __handshake_protocol__ = 1

    def __init__(self, relay_server_url, user_id, connect_to):
        self.relay_server_url = relay_server_url
        self.user_id = user_id
        self.connect_to = connect_to

        self.state = SecureMessageSendingStates.NOT_CONNECTED
        self.relay_websocket = None
        self.stopped = False

        self.other_ephemeral_public_key_hash = None

    def _advance_state(self):
        raise NotImplementedError()

    def connect_to_relay_server(self):
        if self.state != SecureMessageSendingStates.NOT_CONNECTED:
            raise RuntimeError('Unexpected state {}'.format(self.state))

        self.relay_websocket = WSWebSocketWrapper(u'{}/relay_ws'.format(self.relay_server_url))

    def send_handshake(self):
        user_id = self.user_id if self.__transfer_side__ == 'connect' or self.connect_to is None else self.connect_to
        return self.relay_websocket.send(jdumps({
            'handshake_protocol': self.__handshake_protocol__,
            'accept_protocols': KeyExchangeManager.__supported_protocols__,
            'user_id': user_id,
            'connect_to': self.connect_to,
            'action': '{}_handshake'.format(self.__transfer_side__),
            'type': self.transfer_type
        }))

    def init_dh(self, dh_manager):
        self._dh_manager = dh_manager
        user_id = self.user_id if self.__transfer_side__ == 'connect' or self.connect_to is None else self.connect_to
        self.relay_websocket.send(jdumps({
            'user_id': user_id,
            'action': self.__transfer_side__,
            'type': self.transfer_type,
            'public_key_hash': self._dh_manager.ephemeral_key_hash(
                self._dh_manager.ephemeral_key.public_user_key.serialize()),
            'protocol_version': self.protocol_version
        }))

    def resolve_common_protocol(self, handshake_message):
        common_protocols = \
            set(handshake_message['accept_protocols']) \
            .intersection(set(KeyExchangeManager.__supported_protocols__))

        if len(common_protocols) == 0:
            return None
        return max(common_protocols)

    def read_relay_socket(self):
        while True:
            data = self.relay_websocket.receive()
            if isinstance(data, WSData):
                if data.message['action'] != 'ok':
                    if data.message['data']['status'] == u'forbidden':
                        raise ValueError(u'key transfer forbidden by organization')
                return data.message['data']
            elif isinstance(data, WSError):
                raise ValueError(data.message)

            time.sleep(0.05)

    def stop(self):
        if self.stopped:
            return
        self.stopped = True

        if self.relay_websocket:
            self.relay_websocket.close()
