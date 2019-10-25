"""Test roles logic (building, storing, retrieving) with a Batfish service backend."""
from os.path import abspath, dirname, join, realpath

import pytest

from pybfe.client.session import Session
from tests.common_util import requires_bfe

_this_dir = abspath(dirname(realpath(__file__)))
SNAPSHOT_DIR = join(_this_dir, "snapshots", "basic")
NETWORK = "roles_network"


@pytest.fixture()
def session():
    s = Session()
    s.set_network(NETWORK)
    # Snapshot which can be referenced by name
    name = s.init_snapshot(join(_this_dir, "snapshots", "roles_snapshot"))
    yield s
    s.delete_snapshot(name)


@requires_bfe("2019.10.10")
def test_roles(session):
    from pybatfish.datamodel.referencelibrary import NodeRolesData, RoleMapping

    mapping = RoleMapping(None, "(.)(.)", {"function": [1], "index": [2]})
    node_roles = NodeRolesData(None, ["function", "index"], [mapping])
    session.put_node_roles(node_roles)
    function_answer = session.q.roles(roleDimension="function").answer()
    index_answer = session.q.roles(roleDimension="index").answer()

    function_map = function_answer["answerElements"][0]["roleMap"]
    index_map = index_answer["answerElements"][0]["roleMap"]

    assert function_map == {"h": ["h1", "h2"], "r": ["r1", "r2"]}

    assert index_map == {"1": ["h1", "r1"], "2": ["h2", "r2"]}
