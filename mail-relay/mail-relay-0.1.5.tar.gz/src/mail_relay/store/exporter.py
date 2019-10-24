
class ExporterBucket:
    NAME = u'exporter'
    CURRENT_VERSION = 0

    @staticmethod
    def key():
        return 'exporter'

    @staticmethod
    def serialize(user_id, account_version, bucket_version):
        if bucket_version == 0:
            return ExporterBucket._serialize_v0(user_id, account_version)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def deserialize(blob, bucket_version):
        if bucket_version == 0:
            return ExporterBucket._deserialize_v0(blob)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def _serialize_v0(user_id, account_version):
        return u'{};{}'.format(account_version, user_id)

    @staticmethod
    def _deserialize_v0(blob):
        a = blob.split(';', 1)
        return a[0], a[1]
