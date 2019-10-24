from pvHelpers.crypto import PVKeyFactory
from pvHelpers.utils import b64dec


class KeyBucket:
    NAME = u'key'
    CURRENT_VERSION = 0

    @staticmethod
    def key(user_id, account_version, key_version):
        return '{};{};{}'.format(key_version, account_version, user_id.lower())

    @staticmethod
    def serialize(user_key, bucket_version):
        if bucket_version == 0:
            return KeyBucket._serialize_v0(user_key)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def deserialize(blob, bucket_version):
        if bucket_version == 0:
            return KeyBucket._deserialize_v0(blob)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def _serialize_v0(user_key):
        return user_key.serialize()

    @staticmethod
    def _deserialize_v0(blob):
        return PVKeyFactory.userKeyFromSerializedBuffer(b64dec(blob))
