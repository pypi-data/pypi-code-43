"""Test Session functionality with Batfish service backend."""
from os.path import abspath, dirname, join, realpath

import pytest
from requests import HTTPError

from pybfe.client.session import Session
from tests.common_util import requires_bfe

_this_dir = abspath(dirname(realpath(__file__)))

SNAPSHOT_DIR = join(_this_dir, 'snapshots', 'basic')


@pytest.fixture()
def session():
    s = Session()
    # Snapshot which can be referenced by name
    other_name = s.init_snapshot(join(_this_dir, 'snapshots', 'basic2'))
    # Current snapshot
    name = s.init_snapshot(join(_this_dir, 'snapshots', 'basic'))
    yield s
    s.delete_snapshot(name)
    s.delete_snapshot(other_name)


@requires_bfe('2019.09.01')
def test_network_object(session):
    """Confirm network object up/download works as expected."""
    key = 'key'
    data = 'data'

    # No error putting the object
    session.put_network_object(key, data)

    # Reading the object back should result in the data we put there
    assert session.get_network_object_text(key) == data

    session.delete_network_object(key)
    # Should get 404 when trying to get an object after it was deleted
    with pytest.raises(HTTPError) as e:
        session.get_network_object_text(key)
        assert e.response.status_code == 404


def test_snapshot_object(session):
    """Confirm snapshot object up/download works as expected."""
    key = 'key'
    data = 'data'

    # No error putting the object
    session.put_snapshot_object(key, data, snapshot=session.snapshot)

    # Reading the object back should result in the data we put there
    assert session.get_snapshot_object_text(key,
                                            snapshot=session.snapshot) == data


def test_snapshot_input_object(session):
    """Confirm snapshot input-object download works as expected."""
    key = join('configs', 'basic.cfg')
    # Get the config content from disk
    with open(join(SNAPSHOT_DIR, key), 'r') as f:
        data = f.read()

    # Reading a config input-object from backend should match original config
    assert session.get_snapshot_input_object_text(key,
                                                  snapshot=session.snapshot) == data


def test_validate_facts(session):
    """Confirm fact validation returns the expected dictionary of mismatched facts."""
    validation_results = session.validate_facts(
        expected_facts=join(_this_dir, 'facts', 'basic_fail'))

    assert validation_results == {
        'basic': {
            'Syslog.Logging_Servers': {
                'actual': [],
                'expected': ['1.2.3.5'],
            },
            'Extra_Key': {
                'expected': 'something',
                'key_present': False,
            }
        }
    }, 'Logging_Servers should be different and Extra_Key should be missing'


@requires_bfe('2019.09.01')
def test_validate_facts_specific_snapshot(session):
    """Confirm fact validation works when a snapshot is specified."""
    non_current_snapshot = session.list_snapshots()[-1]
    # Non-current snapshot should match facts in facts/basic2/ but not facts/basic/
    validation_results = session.validate_facts(
        expected_facts=join(_this_dir, 'facts', 'basic2'),
        snapshot=non_current_snapshot)

    assert validation_results == {}, 'No differences between expected and actual facts'
