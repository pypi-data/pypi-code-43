from pvHelpers.store import GetDBSession
from pvHelpers.utils import CaseInsensitiveDict, MergeDicts

from .config import ConfigBucket
from .exporter import ExporterBucket
from .key import KeyBucket
from .user import UserBucket


def write_key(user_id, account_version, key, store_path):
    with GetDBSession(store_path) as session:
        try:
            session.begin()
            res = session.execute(
                '''
                INSERT INTO Store (bucket, bucket_version, key, value)
                VALUES (:bucket, :version, :key, :value)
                ''', {
                    'bucket': KeyBucket.NAME,
                    'version': KeyBucket.CURRENT_VERSION,
                    'key': KeyBucket.key(user_id, account_version, key.key_version),
                    'value': KeyBucket.serialize(key, KeyBucket.CURRENT_VERSION)
                }
            )
            session.commit()
            return res.lastrowid
        except Exception:
            session.rollback()
            raise


def read_key(user_id, account_version, key_version, store_path):
    with GetDBSession(store_path) as session:
        result = session.execute(
            '''
            SELECT id, value, bucket_version FROM Store
            WHERE bucket = :bucket AND key = :key
            ''', {
                'bucket': KeyBucket.NAME,
                'key': KeyBucket.key(user_id, account_version, key_version)
            }
        )
        (_, blob, b_v) = result.fetchall()[0]

    return KeyBucket.deserialize(blob, b_v)


def read_keys(user_id, account_version, store_path):
    with GetDBSession(store_path) as session:
        result = session.execute(
            '''
            SELECT id, value, bucket_version FROM Store
            WHERE bucket = :bucket AND key LIKE :key
            ''', {
                'bucket': KeyBucket.NAME,
                'key': KeyBucket.key(user_id, account_version, '%')
            }
        )
        results = result.fetchall()

    return [KeyBucket.deserialize(blob, b_v) for (_, blob, b_v) in results]


def write_user(user, store_path):
    with GetDBSession(store_path) as session:
        try:
            session.begin()
            res = session.execute(
                '''
                INSERT INTO Store (bucket, bucket_version, key, value)
                VALUES (:bucket, :version, :key, :value)
                ''', {
                    'bucket': UserBucket.NAME,
                    'version': UserBucket.CURRENT_VERSION,
                    'key': UserBucket.key(user.user_id, user.account_version),
                    'value': UserBucket.serialize(user, UserBucket.CURRENT_VERSION)
                }
            )
            session.commit()
            return res.lastrowid
        except Exception:
            session.rollback()
            raise


def delete_user(user_id, store_path):
    with GetDBSession(store_path) as session:
        try:
            session.begin()
            session.execute(
                '''
                DELETE FROM Store
                WHERE bucket=:bucket
                AND key LIKE :key
                ''', {
                    'bucket': UserBucket.NAME,
                    'key': UserBucket.key(user_id, '%')
                }
            )
            session.execute(
                '''
                DELETE FROM Store
                WHERE bucket=:bucket
                AND key LIKE :key
                ''', {
                    'bucket': KeyBucket.NAME,
                    'key': KeyBucket.key(user_id, '%', '%')
                }
            )
            session.commit()
        except Exception:
            session.rollback()
            raise


# TODO: add single fetch api
def read_user(user_id, account_version, store_path):
    pass


def read_users(store_path):
    with GetDBSession(store_path) as session:
        result = session.execute(
            '''
            SELECT id, value, bucket_version FROM Store
            WHERE bucket = :bucket
            ''', {
                'bucket': UserBucket.NAME
            }
        )
        results = result.fetchall()

    users = [UserBucket.deserialize(blob, b_v) for (_, blob, b_v) in results]

    for u in users:
        u.user_keys = read_keys(u.user_id, u.account_version, store_path)

    latest_versions = CaseInsensitiveDict()
    for u in users:
        if (-1, u.user_id) in latest_versions and \
           latest_versions[(-1, u.user_id)].account_version < u.account_version:

            latest_versions[(-1, u.user_id)] = u

        else:
            latest_versions[(-1, u.user_id)] = u

    return CaseInsensitiveDict(MergeDicts(
        {(u.account_version, u.user_id): u for u in users},
        latest_versions
    ))


def update_config(config, store_path):
    with GetDBSession(store_path) as session:
        try:
            session.begin()
            res = session.execute(
                '''
                INSERT OR REPLACE INTO Store (bucket, bucket_version, key, value)
                VALUES (:bucket, :version, :key, :value)
                ''', {
                    'bucket': ConfigBucket.NAME,
                    'version': ConfigBucket.CURRENT_VERSION,
                    'key': ConfigBucket.key(),
                    'value': ConfigBucket.serialize(config, UserBucket.CURRENT_VERSION)
                }
            )
            session.commit()
            return res.lastrowid
        except Exception:
            session.rollback()
            raise


def read_config(store_path):
    with GetDBSession(store_path) as session:
        result = session.execute(
            '''
            SELECT id, value, bucket_version FROM Store
            WHERE bucket = :bucket AND key = :key
            ''', {
                'bucket': ConfigBucket.NAME,
                'key': ConfigBucket.key()
            }
        )
        results = result.fetchall()

    if len(results) == 1:
        (_, blob, b_v) = results[0]
        return ConfigBucket.deserialize(blob, b_v)

    # len(results) == 0
    return None


def write_exporter(user_id, account_version, store_path):
    with GetDBSession(store_path) as session:
        try:
            session.begin()
            res = session.execute(
                '''
                INSERT OR REPLACE INTO Store (bucket, bucket_version, key, value)
                VALUES (:bucket, :version, :key, :value)
                ''', {
                    'bucket': ExporterBucket.NAME,
                    'version': ExporterBucket.CURRENT_VERSION,
                    'key': ExporterBucket.key(),
                    'value': ExporterBucket.serialize(user_id, account_version, ExporterBucket.CURRENT_VERSION)
                }
            )
            session.commit()
            return res.lastrowid
        except Exception:
            session.rollback()
            raise


def read_exporter(store_path):
    with GetDBSession(store_path) as session:
        result = session.execute(
            '''
            SELECT id, value, bucket_version FROM Store
            WHERE bucket = :bucket AND key = :key
            ''', {
                'bucket': ExporterBucket.NAME,
                'key': ExporterBucket.key()
            }
        )
        r = result.fetchone()
    if r is not None:
        (_, blob, b_v) = r
        return ExporterBucket.deserialize(blob, b_v)
    return (None, None)
