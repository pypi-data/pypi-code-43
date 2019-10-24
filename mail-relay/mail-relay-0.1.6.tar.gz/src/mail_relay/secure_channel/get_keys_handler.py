from pvHelpers.crypto import PVKeyFactory
from pvHelpers.utils import b64enc, jdumps, utf8Encode

from .base_handler import SecureMessageManager
from .base_handler import SecureMessageSendingStates as States
from .base_handler import TransferTypes
from .key_exchange_manager import KeyExchangeManager


class GetMessageManager(SecureMessageManager):
    __transfer_side__ = u'connect'

    def __init__(self, relay_server_url, user_id, connect_to, transfer_type, pin_verifier, callback):
        super(GetMessageManager, self).__init__(relay_server_url, user_id, connect_to)

        self.transfer_type = transfer_type
        self.pin_verifier = pin_verifier
        self.callback = callback

        self.protocol_version = 1

        self._got_ok = False
        self._other_ephemral_public_key_serialized = None

    def _advance_state(self):
        if self.state == States.NOT_CONNECTED:
            self.state = States.WAITING_FOR_HANDSHAKE

        elif self.state == States.WAITING_FOR_HANDSHAKE:
            self.state = States.WAITING_FOR_HASH

        elif self.state == States.WAITING_FOR_HASH:
            self.state = States.WAITING_FOR_PUBLIC_KEY

        elif self.state == States.WAITING_FOR_PUBLIC_KEY:
            self.state = States.WAITING_FOR_ENCRYPTED_MESSAGE

        elif self.state == States.WAITING_FOR_ENCRYPTED_MESSAGE:
            self.state = States.DONE

        elif self.state == States.DONE:
            pass

    def get_secure_channel(self, new_device_req=None, user_req=None, useless_signature=None):
        if self.state != States.NOT_CONNECTED:
            raise ValueError('Unexpected state {}'.format(self.state))
        try:
            while True:
                if self.state == States.NOT_CONNECTED:
                    self.connect_to_relay_server()
                    self.send_handshake()
                    self._advance_state()
                elif self.state == States.WAITING_FOR_HANDSHAKE:
                    message = self.read_relay_socket()
                    common_protocol = self.resolve_common_protocol(message)
                    if common_protocol is None:
                        raise RuntimeError(u'no commmon dh protocol {}'.format(message))

                    self.init_dh(KeyExchangeManager.new(common_protocol))
                    self._advance_state()
                elif self.state == States.WAITING_FOR_HASH:
                    message = self.read_relay_socket()
                    self.other_ephemeral_public_key_hash = message['public_key_hash']

                    if self.transfer_type == TransferTypes.TRANSFER:
                        self.relay_websocket.send(jdumps({
                            'action': u'key_transfer',
                            'user_id': self.user_id,
                            'device_req': new_device_req.serialized_req,
                            'signature': b64enc(
                                self._dh_manager.ephemeral_key.signing_key.sign(
                                    utf8Encode(new_device_req.serialized_req))),
                            'message': self._dh_manager.ephemeral_key.public_user_key.serialize()
                        }))
                    else:
                        raise ValueError('Unexpected transfer type {}'.format(self.transfer_type))

                    self._advance_state()
                elif self.state == States.WAITING_FOR_PUBLIC_KEY:
                    message = self.read_relay_socket()

                    # Wait for an 'ok' (server received our pk) and their public key.
                    if message.get('message') is None:
                        self._got_ok = True
                    else:
                        self._other_ephemral_public_key_serialized = message['message']

                    # Don't advance until we got:
                    #  - server ok
                    #  - other side ephemeral key
                    if self._got_ok and self._other_ephemral_public_key_serialized is not None:
                        # make sure other side ephemeral key matches it's hash
                        key_hash = KeyExchangeManager.ephemeral_key_hash(self._other_ephemral_public_key_serialized)
                        if key_hash != self.other_ephemeral_public_key_hash:
                            raise ValueError('''Unmatching public key hashes.
                                                Initial hash {}
                                                Provided ephemeral key hash {}'''.format(
                                                    self.other_ephemeral_public_key_hash, key_hash))

                        self._dh_manager.other_ephemeral_key = PVKeyFactory.deserializePublicUserKey(
                            self._other_ephemral_public_key_serialized, is_protobuf=False)

                        status = self.pin_verifier(self._dh_manager.pin)
                        if not status:
                            raise ValueError('Pin not verified.')

                        self._advance_state()
                elif self.state == States.WAITING_FOR_ENCRYPTED_MESSAGE:
                    message = self.read_relay_socket()
                    secret_message = self._dh_manager.decrypt(message['message'])

                    if self.transfer_type == TransferTypes.TRANSFER:
                        device_req_sign = message['device_signature']
                        status = self.callback(secret_message, device_req_sign)
                    elif self.transfer_type == TransferTypes.RECOVERY:
                        device_req_sign = None
                        req_approver_sign = message['approver_signature']
                        approver_id = message['approver_id']
                        approver_key_version = message['approver_key_version']

                        status = self.callback(secret_message, req_approver_sign, approver_id, approver_key_version)
                    elif self.transfer_type == TransferTypes.EXPORT:
                        status = self.callback(secret_message)
                    else:
                        raise ValueError('Unexpected transfer type {}'.format(self.transfer_type))

                    if not status:
                        raise RuntimeError('callback failure')
                    self._advance_state()
                elif self.state == States.DONE:
                    return
        finally:
            self.stop()
