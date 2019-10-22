from pvHelpers.crypto import (ASYMM_KEY_PROTOCOL_VERSION,
                              PVKeyFactory,
                              SIGN_KEY_PROTOCOL_VERSION,
                              SYMM_KEY_PROTOCOL_VERSION)
from pvHelpers.crypto.box import AsymmBox, AsymmBoxV3
from pvHelpers.crypto.utils import HexEncode, Sha512Sum
from pvHelpers.utils import b64dec, b64enc, utf8Decode, utf8Encode


class DHProtocols(object):
    V1 = 1  # usage of ASYMM_KEY_PROTOCOL_VERSION.V2
    V2 = 2  # usage of ASYMM_KEY_PROTOCOL_VERSION.V3

    Current = V2


class KeyExchangeManager(object):
    __supported_protocols__ = [DHProtocols.V1, DHProtocols.V2]

    def __init__(self, protocol_version, ephemeral_key):
        self.ephemeral_key = ephemeral_key
        self.protocol_version = protocol_version
        self.other_ephemeral_key = None

    @classmethod
    def new(cls, protocol_version=None):
        if protocol_version is None:
            protocol_version = DHProtocols.Current

        if protocol_version == DHProtocols.V1:
            ephemeral_key = PVKeyFactory.newUserKey(
                0,
                encryption_key=PVKeyFactory.newAsymmKey(ASYMM_KEY_PROTOCOL_VERSION.V2),
                signing_key=PVKeyFactory.newSignKey(SIGN_KEY_PROTOCOL_VERSION.V1))
        elif protocol_version == DHProtocols.V2:
            ephemeral_key = PVKeyFactory.newUserKey(
                0,
                encryption_key=PVKeyFactory.newAsymmKey(ASYMM_KEY_PROTOCOL_VERSION.V3),
                signing_key=PVKeyFactory.newSignKey(SIGN_KEY_PROTOCOL_VERSION.V3))
        else:
            raise NotImplementedError('Unknown DH protocol {}'.format(protocol_version))

        return KeyExchangeManager(protocol_version, ephemeral_key)

    @staticmethod
    def ephemeral_key_hash(serialized_key):
        encoded = utf8Encode(serialized_key)
        digest = Sha512Sum(encoded)
        return HexEncode(digest)

    @property
    def pin(self):
        if self.other_ephemeral_key is None:
            raise RuntimeError('other side\'s public key is not set')

        if self.protocol_version == DHProtocols.V1:
            box = AsymmBox(self.ephemeral_key.encryption_key, self.other_ephemeral_key.public_key)
            return box.getPin()
        elif self.protocol_version == DHProtocols.V2:
            shared_key = AsymmBoxV3.get_shared_key(
                self.ephemeral_key.encryption_key, self.other_ephemeral_key.public_key)
            digest = Sha512Sum(shared_key)
            return HexEncode(digest)[:8]

        raise NotImplementedError('Unknown transfer protocol {}'.format(self.protocol_version))

    def encrypt(self, message):
        if self.other_ephemeral_key is None:
            raise RuntimeError('other side\'s public key is not set')

        if self.protocol_version == DHProtocols.V1:
            box = AsymmBox(self.ephemeral_key.encryption_key, self.other_ephemeral_key.public_key)
            return b64enc(box.encrypt(utf8Encode(message), is_text=True))
        elif self.protocol_version == DHProtocols.V2:
            shared_key = AsymmBoxV3.get_shared_key(
                self.ephemeral_key.encryption_key, self.other_ephemeral_key.public_key)
            key = PVKeyFactory.newSymmKey(SYMM_KEY_PROTOCOL_VERSION.V1, secret=shared_key)
            cipher = key.encrypt(utf8Encode(message))
            return b64enc(cipher)

        raise NotImplementedError('Unknown transfer protocol {}'.format(self.protocol_version))

    def decrypt(self, cipher):
        if self.other_ephemeral_key is None:
            raise RuntimeError('other side\'s public key is not set')

        if self.protocol_version == DHProtocols.V1:
            box = AsymmBox(self.ephemeral_key.encryption_key, self.other_ephemeral_key.public_key)
            return utf8Decode(box.decrypt(b64dec(cipher)))
        elif self.protocol_version == DHProtocols.V2:
            shared_key = AsymmBoxV3.get_shared_key(
                self.ephemeral_key.encryption_key, self.other_ephemeral_key.public_key)
            key = PVKeyFactory.newSymmKey(SYMM_KEY_PROTOCOL_VERSION.V1, secret=shared_key)
            plaintext = key.decrypt(b64dec(cipher))
            return utf8Decode(plaintext)

        raise NotImplementedError('Unknown transfer protocol {}'.format(self.protocol_version))
