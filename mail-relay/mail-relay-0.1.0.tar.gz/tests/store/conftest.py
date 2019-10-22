import os

from mail_relay.store.migrate import migrate
import pytest


@pytest.fixture(scope='module')
def store(tmpdir_factory):
    s = tmpdir_factory.mktemp('store')
    store_path = os.path.abspath(os.path.join(str(s), 'test.sqlite'))
    migrate(store_path)
    return store_path
