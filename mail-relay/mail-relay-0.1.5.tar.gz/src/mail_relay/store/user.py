from pvHelpers.crypto import PVKeyFactory
from pvHelpers.user import LocalDevice, LocalUser, OrganizationInfo
from pvHelpers.utils import b64dec, jdumps, jloads, NOT_ASSIGNED


class UserBucket:
    NAME = u'user'
    CURRENT_VERSION = 0

    @staticmethod
    def key(user_id, account_version):
        return '{};{}'.format(account_version, user_id.lower())

    @staticmethod
    def serialize(user, bucket_version):
        if bucket_version == 0:
            return UserBucket._serialize_v0(user)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def deserialize(blob, bucket_version):
        if bucket_version == 0:
            return UserBucket._deserialize_v0(blob)
        else:
            raise ValueError(u'unsupported bucket bucket_version {}'.format(bucket_version))

    @staticmethod
    def _serialize_v0(user):
        return jdumps({
            'user_id': user.user_id,
            'account_version': user.account_version,
            'display_name': user.display_name,
            'mail_cid': user.mail_cid,
            'org_info': None if user.org_info is None else {
                'id': user.org_info.org_id,
                'name': user.org_info.org_name,
                'department': user.org_info.dept_name,
                'role': user.org_info.role
            },
            'device': {
                'id': user.device.id,
                'name': user.device.name,
                'key': user.device.key.serialize(),
                'metadata': user.device.metadata,
                'status': user.device.status
            }
        })

    @staticmethod
    def _deserialize_v0(blob):
        j = jloads(blob)
        jd, jo = j['device'], j['org_info']
        d = LocalDevice(
            jd['id'], jd['name'], PVKeyFactory.userKeyFromSerializedBuffer(b64dec(jd['key'])),
            jd['metadata'], jd['status'])
        o = jo and OrganizationInfo(jo['id'], jo['name'], jo['department'], jo['role'])
        return LocalUser(
            j['user_id'], j['account_version'], j['display_name'],
            j['mail_cid'], o, NOT_ASSIGNED(), u'', [], d)
