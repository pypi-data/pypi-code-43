import ast
import json
import unittest
from contextlib import suppress
from uuid import uuid4

import arrow

from dq.database import commit_scope, save_to_database
from tests.models import Table2, User, UserType


class TestORM(unittest.TestCase):

    def tearDown(self):
        with suppress(Exception), commit_scope() as session:
            session.query(Table2).delete()
            session.query(User).delete()

    def test_string(self):
        t2 = Table2(id=1, key=1, key2=1, user_type=UserType.admin,
                    created_at=arrow.get('2017-10-21'))
        t2_str = str(t2)
        assert t2_str.startswith('<Table2 ')
        assert ast.literal_eval(t2_str[8:-1]) == {
            'id': 1,
            'user_uuid': None,
            'user_type': 'admin',
            'key2': True,
            'created_at': 1508544000,
        }

    def test_to_dict(self):
        uuid = str(uuid4())
        now = arrow.get()
        t2 = Table2(id=1, user_uuid=uuid, key=1, key2=1,
                    user_type=UserType.regular, created_at=now)

        t2_dict = t2.to_dict()
        t2_inflate = t2.inflate_to_dict()
        assert t2_inflate == t2_dict
        assert t2_dict == {
            'id': 1,
            'user_uuid': uuid,
            'user_type': 'regular',
            'key2': True,
            'created_at': now.timestamp,
        }

    def test_to_json(self):
        uuid = str(uuid4())
        now = arrow.get()
        t2 = Table2(id=1, user_uuid=uuid, key=1, key2=1,
                    user_type=UserType.regular, created_at=now)
        t2_json = t2.to_json()
        assert json.loads(t2_json) == {
            'id': 1,
            'user_uuid': uuid,
            'user_type': 'regular',
            'key2': True,
            'created_at': now.timestamp,
        }

    def test_from_dict(self):
        uuid = str(uuid4())
        now = arrow.get()
        t2_dict = {
            'id': 1,
            'user_uuid': uuid,
            'key': 1,
            'key2': 1,
            'created_at': now.timestamp,
        }
        t2 = Table2.from_dict(t2_dict)
        assert t2.created_at == arrow.get(now.timestamp)
        assert not t2.key2

    def test_get_by(self):
        uuid = str(uuid4())
        t2 = Table2(id=1, user_uuid=uuid)
        save_to_database(t2)

        t2 = Table2.get_by('user_uuid', uuid)
        assert t2.id == 1

    def test_get_by_for_update(self):
        uuid = str(uuid4())
        t2 = Table2(id=1, user_uuid=uuid)
        save_to_database(t2)

        t2 = Table2.get_by('user_uuid', uuid, for_update=True)
        assert t2.id == 1
        t2.key2 = 10
        save_to_database(t2)
        t2 = Table2.get_by('user_uuid', uuid)
        assert t2.key2 == 10

    def test_get_by_empty(self):
        t2 = Table2(id=1, user_uuid=str(uuid4()))
        save_to_database(t2)
        assert not Table2.get_by('user_uuid', None)

    def test_get_multi(self):
        uuid = str(uuid4())
        t21 = Table2(id=1, user_uuid=uuid, key=1, key2=1)
        t22 = Table2(id=2, user_uuid=uuid, key=1, key2=2)
        t23 = Table2(id=3, user_uuid=uuid, key=1, key2=3)
        t24 = Table2(id=4, user_uuid=uuid, key=1, key2=4)
        t25 = Table2(id=5, user_uuid=uuid, key=1, key2=5)
        save_to_database([t21, t22, t23, t24, t25])

        results = Table2.get_multi('key', 1, 'key2', offset=2, limit=2)
        assert len(results) == 2
        assert results[0].key2 == 3
        assert results[1].key2 == 2

        results = Table2.get_multi('key', 1, 'key2', desc=False, limit=7)
        assert len(results) == 5
        assert results[0].key2 == 1

    def test_get_by_deleted(self):
        uuid = str(uuid4())
        t2 = Table2(id=1, user_uuid=uuid, deleted_at=arrow.get())
        save_to_database(t2)

        assert not Table2.get_by('user_uuid', uuid)

    def test_get_by_deleted_contains(self):
        uuid = str(uuid4())
        t2 = Table2(id=1, user_uuid=uuid)
        save_to_database(t2)

        t2 = Table2.get_by('user_uuid', uuid, contains_deleted=True)
        assert t2.id == 1

    def test_get_by_user(self):
        uuid = str(uuid4())
        t21 = Table2(id=1, user_uuid=uuid, key=1, key2=1,
                     created_at=arrow.get('2011-10-21'))
        t22 = Table2(id=2, user_uuid=uuid, key=1, key2=2,
                     created_at=arrow.get('2012-10-21'))
        t23 = Table2(id=3, user_uuid=uuid, key=1, key2=3,
                     created_at=arrow.get('2013-10-21'))
        t24 = Table2(id=4, user_uuid=uuid, key=1, key2=4,
                     created_at=arrow.get('2014-10-21'))
        t25 = Table2(id=5, user_uuid=uuid, key=1, key2=5,
                     created_at=arrow.get('2015-10-21'))
        save_to_database([t21, t22, t23, t24, t25])

        results = Table2.get_by_user(uuid, offset=2, limit=2)
        assert len(results) == 2
        assert results[0].key2 == 3
        assert results[1].key2 == 2
