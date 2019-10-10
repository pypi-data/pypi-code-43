import unittest
from contextlib import suppress
from uuid import uuid4

from dq.database import (
    commit_scope, safe_save_to_database, save_to_database, Session)
from dq.errors import ModelError
from tests.models import Table2, User


class TestDatabase(unittest.TestCase):

    def tearDown(self):
        with suppress(Exception), commit_scope() as session:
            session.query(User).delete()
            session.query(Table2).delete()

    def test_replace_insert(self):
        uuid = str(uuid4())
        user = User(uuid=uuid, email='unittest@danqing.io')
        save_to_database(user)

        user = {'uuid': uuid, 'email': 'unittest2@danqing.io'}
        session = Session()
        session.execute(User.__table__.insert(mysql_replace_insert=True), user)
        session.commit()
        user = User.get(uuid)
        assert user.email == 'unittest2@danqing.io'

    def test_save_to_database_noop(self):
        save_to_database(None)

    def test_save_to_database_single(self):
        uuid = str(uuid4())
        user = User(uuid=uuid, email='unittest@danqing.io')
        save_to_database(user)

        user = User.get(uuid)
        assert user.email == 'unittest@danqing.io'

    def test_save_to_database_multi(self):
        uuid = str(uuid4())
        user = User(uuid=uuid, email='unittest@danqing.io')
        t2 = Table2(id=2, user_uuid=uuid)
        save_to_database([user, t2])

        user = User.get(uuid)
        assert user.email == 'unittest@danqing.io'
        t2 = Table2.get(2)
        assert t2.user_uuid == uuid

    def test_save_to_database_error(self):
        self.assertRaises(ModelError, save_to_database, User())

    def test_safe_save_to_database_noop(self):
        assert safe_save_to_database(None)

    def test_safe_save_to_database_single(self):
        uuid = str(uuid4())
        user = User(uuid=uuid, email='unittest@danqing.io')
        assert safe_save_to_database(user)

        user = User.get(uuid)
        assert user.email == 'unittest@danqing.io'

    def test_safe_save_to_database_multi(self):
        uuid = str(uuid4())
        user = User(uuid=uuid, email='unittest@danqing.io')
        t2 = Table2(id=1, user_uuid=uuid)
        assert safe_save_to_database([user, t2])

        user = User.get(uuid)
        assert user.email == 'unittest@danqing.io'
        t2 = Table2.get(1)
        assert t2.user_uuid == uuid

    def test_safe_save_to_database_error(self):
        assert not safe_save_to_database(User())
