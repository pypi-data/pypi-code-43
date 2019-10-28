from hashlib import sha1
from datetime import timedelta, datetime

from sqlhelp import select, insert
from sqlalchemy import create_engine
import pytz


class dbcache:
    __slots__ = ('ns', 'engine')

    def __init__(self, uri, namespace='cache'):
        self.engine = create_engine(uri)
        self.ns = namespace

    def _remove_expired(self, cn):
        cn.execute(
            f'delete from "{self.ns}".things '
            f'where idate + validity < now()'
        )

    def _txlock(self, cn, key):
        lockid = hash(key + self.ns.encode('utf-8'))
        cn.execute(
            f'select pg_advisory_xact_lock({lockid})'
        )

    def get(self, key):
        with self.engine.begin() as cn:
            self._txlock(cn, key)
            self._remove_expired(cn)
            q = select(
                'value'
            ).table(
                f'{self.ns}.things'
            ).where(
                key=sha1(key).hexdigest()
            )
            value = q.do(cn).scalar()
            if value:
                return value.tobytes()

    def _set(self, cn, hkey, value, lifetime):
        sql = (
            f'insert into {self.ns}.things (key, value, validity) '
            'values (%(key)s, %(value)s, %(validity)s) '
            'on conflict (key) do update set '
            ' value = %(value)s, '
            ' validity = %(validity)s, '
            ' idate = %(idate)s'
        )
        cn.execute(
            sql,
            key=hkey,
            value=value,
            validity=lifetime,
            idate=datetime.utcnow().replace(tzinfo=pytz.utc)
        )

    def set(self, key, value, lifetime=timedelta(minutes=10)):
        with self.engine.begin() as cn:
            self._txlock(cn, key)
            self._remove_expired(cn)
            hkey = sha1(key).hexdigest()
            self._set(cn, hkey, value, lifetime)

    def getorset(self, key, valuemaker, lifetime=timedelta(minutes=10)):
        assert callable(valuemaker)
        with self.engine.begin() as cn:
            self._txlock(cn, key)
            self._remove_expired(cn)
            hkey = sha1(key).hexdigest()
            q = select(
                'value'
            ).table(
                f'{self.ns}.things'
            ).where(
                key=hkey
            )
            value = q.do(cn).scalar()
            if value is not None:
                return value.tobytes()
            value = valuemaker()
            self._set(cn, hkey, value, lifetime)
            return value
