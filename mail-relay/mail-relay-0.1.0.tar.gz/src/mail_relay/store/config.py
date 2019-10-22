from mail_relay.config import Config
from pvHelpers.utils import jdumps, jloads


class ConfigBucket:
    NAME = u'config'
    CURRENT_VERSION = 0

    @staticmethod
    def key():
        return 'config'

    @staticmethod
    def serialize(config, bucket_version):
        if bucket_version == 0:
            return ConfigBucket._serialize_v0(config)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def deserialize(blob, bucket_version):
        if bucket_version == 0:
            return ConfigBucket._deserialize_v0(blob)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def _serialize_v0(config):
        return jdumps(config.to_json())

    @staticmethod
    def _deserialize_v0(blob):
        j = jloads(blob)
        return Config.from_json(j)
