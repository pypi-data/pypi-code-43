#   Copyright 2019 Intentionet
#
#   Licensed under the proprietary License included with this package;
#   you may not use this file except in compliance with the License.
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Test Policy and related (Test, Assert) objects."""

import json

from pybfe.client.policy._common import aggregate_status
from pybfe.client.policy._policy import (
    _get_policy_details,
    load_policy,
    _update_policy_status,
    write_policy,
)
from pybfe.client.policy._test import _get_test_details, update_test_status, write_test
from pybfe.datamodel.policy import (
    Assert,
    CiProperties,
    Policy,
    Question,
    STATUS_ERROR,
    STATUS_FAIL,
    STATUS_PASS,
    Test,
)
from tests.common_util import MockPolicyTest, MockSession


def test_test_update():
    """Test updating test status after adding assertions."""
    t = Test("t1")

    t.add_assert(Assert(name="a1", status=STATUS_PASS, message="message"))
    update_test_status(t)
    # Adding a single passing assertion should make the test pass
    assert t.get_status() == STATUS_PASS
    # Count should increment for each added assert
    assert t.count == 1
    assert t.not_pass_count == 0

    t.add_assert(Assert(name="a2", status=STATUS_FAIL, message="message"))
    update_test_status(t)
    # Adding a single failing assertion should make the test fail
    assert t.get_status() == STATUS_FAIL
    assert t.count == 2
    # Not-pass-count should only increase when a non-passing assert is added
    assert t.not_pass_count == 1

    t.add_assert(Assert(name="a3", status=STATUS_PASS, message="message"))
    update_test_status(t)
    # Status should still be failing after adding another passing assertion
    assert t.get_status() == STATUS_FAIL
    assert t.count == 3
    assert t.not_pass_count == 1


def test_test_write():
    """Test writing test details to a mock service."""
    session = MockSession()
    policy = Policy(name="p1", id_="pid1")
    t = Test("t1")
    q1 = Question(name="q1")
    a1 = Assert(name="a1", status=STATUS_PASS, message="message1", questions=[q1])
    a2 = Assert(name="a2", status=STATUS_FAIL, message="message2")
    a3 = Assert(name="a3", status=STATUS_FAIL, message="message3")
    t.add_assert(a1)
    t.add_assert(a2)
    t.add_assert(a3)
    q = Question(name="q")
    t.add_question(q)

    # Write the policy to the mock service
    write_test(t, policy, session, "ss1")

    t_details = json.loads(
        session.get_snapshot_object_text("policies/p1/pid1/t1", snapshot="ss1")
    )
    expected_assertions = [a1.get_summary(), a2.get_summary(), a3.get_summary()]
    # Make sure the expected assertions show up in the written test details
    assert expected_assertions == t_details.get("assertions")


def test_policy_update():
    """Test updating a policy after adding tests."""
    p = Policy(name="p1", id_="pid1")
    p.tests = {
        "t1": MockPolicyTest(STATUS_PASS),
        "t2": MockPolicyTest(STATUS_PASS, [Assert("a1", STATUS_FAIL, "msg")]),
    }
    _update_policy_status(p)
    # Confirm status/counts are updated for constituent tests after update
    assert p.status == STATUS_FAIL
    assert p.count == 2
    assert p.not_pass_count == 1


def test_policy_write():
    """Test writing policy details to a mock service."""
    session = MockSession()
    a1 = Assert(name="a1", status=STATUS_PASS, message="message")
    t1 = Test("t1", asserts=[a1])

    p1_old = Policy(name="p1", id_="pid_old")
    write_policy(p1_old, session, snapshot="ss1")

    p1 = Policy(name="p1", id_="pid1", tests=[t1])
    # This overwrites the previous p1 run in the latest-run-summary
    write_policy(p1, session, snapshot="ss1")

    p2 = Policy(name="p2", id_="pid1")
    write_policy(p2, session, snapshot="ss1")

    # Confirm latest-run-summary contains the latest run of both policies
    policies = json.loads(session.get_snapshot_object_text("policies", snapshot="ss1"))
    assert policies == [p1.get_summary(), p2.get_summary()]

    # Confirm policy history contains both runs for p1
    p1_history = json.loads(
        session.get_snapshot_object_text("policies/p1", snapshot="ss1")
    )
    assert p1_history == [p1_old.get_summary(), p1.get_summary()]

    # Confirm policy history contains the only run for p2
    p2_history = json.loads(
        session.get_snapshot_object_text("policies/p2", snapshot="ss1")
    )
    assert p2_history == [p2.get_summary()]

    # Confirm details of the first run of p1 were written correctly
    p1_old_remote = json.loads(
        session.get_snapshot_object_text("policies/p1/pid_old", snapshot="ss1")
    )
    assert p1_old_remote == _get_policy_details(p1_old)

    # Confirm details of the second run of p1 were written correctly
    p1_remote = json.loads(
        session.get_snapshot_object_text("policies/p1/pid1", snapshot="ss1")
    )
    assert p1_remote == _get_policy_details(p1)
    t1_remote = json.loads(
        session.get_snapshot_object_text("policies/p1/pid1/t1", snapshot="ss1")
    )
    assert t1_remote == _get_test_details(t1)

    # Confirm details of p2 were written correctly
    p2_remote = json.loads(
        session.get_snapshot_object_text("policies/p2/pid1", snapshot="ss1")
    )
    assert p2_remote == _get_policy_details(p2)


def test_policy_write_updates():
    """Test re-writing policy details to a mock service."""
    session = MockSession()
    a1 = Assert(name="a1", status=STATUS_PASS, message="message")
    t1 = Test("t1", asserts=[a1])
    p1 = Policy(name="p1", id_="pid", tests=[t1])
    write_policy(p1, session, snapshot="ss1")

    a2 = Assert(name="a2", status=STATUS_PASS, message="message")
    t1.add_assert(a2)
    # This should overwrite the previous p1 history
    write_policy(p1, session, snapshot="ss1")

    # Confirm latest-run-summary contains the updated run of p1
    policies = json.loads(session.get_snapshot_object_text("policies", snapshot="ss1"))
    assert policies == [p1.get_summary()]

    # Confirm policy history contains the updated run of p1 only
    p1_history = json.loads(
        session.get_snapshot_object_text("policies/p1", snapshot="ss1")
    )
    assert p1_history == [p1.get_summary()]

    # Confirm details of the of p1 were written correctly
    p1_remote = json.loads(
        session.get_snapshot_object_text("policies/p1/pid", snapshot="ss1")
    )
    assert p1_remote == _get_policy_details(p1)


def test_policy_load():
    """Test loading a policy from a mock service."""
    p1_pid1_t1_a1_q1 = Question(name="q1")
    p1_pid1_t1_a1 = Assert(
        name="a1", status=STATUS_PASS, message="message", questions=[p1_pid1_t1_a1_q1]
    )
    p1_pid1_t1_q = Question(name="q")
    p1_pid1_t1 = Test(name="t1", asserts=[p1_pid1_t1_a1], questions=[p1_pid1_t1_q])
    p1_pid1_ci_prop1 = CiProperties(url="url1")
    p1_pid1 = Policy(
        name="p1",
        id_="pid1",
        ci_props=p1_pid1_ci_prop1,
        tests=[p1_pid1_t1],
        timestamp="fake_time_1",
    )
    _update_policy_status(p1_pid1)
    p1_pid2 = Policy(name="p1", id_="pid2", tests=[], timestamp="fake_time_2")
    _update_policy_status(p1_pid2)

    object_text_dict = {
        "ss1": {
            # Latest policies list includes only the "latest" run of p1: pid1
            "policies": json.dumps([p1_pid1.get_summary()]),
            "policies/p1/pid1": json.dumps(_get_policy_details(p1_pid1)),
            "policies/p1/pid1/t1": json.dumps(_get_test_details(p1_pid1_t1)),
            "policies/p1/pid2": json.dumps(_get_policy_details(p1_pid2)),
            # Policy history contains boths runs of p1
            "policies/p1": json.dumps([p1_pid1.get_summary(), p1_pid2.get_summary()]),
        }
    }
    session = MockSession(object_text_dict, snapshot="ss1")

    # Confirm the specified policy is loaded when a policy name and ID are provided
    assert (
        load_policy(session, "p1", "pid2", "ss1").get_summary() == p1_pid2.get_summary()
    )

    # Confirm the latest policy is loaded when no policy ID or snapshot is specified
    loaded_policy = load_policy(session, "p1")
    assert loaded_policy.get_summary() == p1_pid1.get_summary()
    # Confirm the right test is loaded
    tests = loaded_policy.tests
    assert set(tests.keys()) == {"t1"}
    assert p1_pid1_t1.get_summary() == tests["t1"].get_summary()
    # Finally, confirm the right assert is loaded
    asserts = tests["t1"].asserts
    assert [p1_pid1_t1_a1.get_summary()] == [a.get_summary() for a in asserts]


def test_aggregate_status_empty():
    """Test status aggregation for a dict with no Asserts or Tests."""
    # No failing asserts/tests means the overall status is passing
    assert aggregate_status([]) == (0, STATUS_PASS)


def test_aggregate_status_error():
    """Test status aggregation for an array of statuses including an error."""
    # Any number of error asserts means the overall status is failing
    assert aggregate_status(
        [
            Assert("a1", STATUS_PASS, "message"),
            Assert("a2", STATUS_ERROR, "message"),
            Assert("a3", STATUS_PASS, "message"),
        ]
    ) == (1, STATUS_FAIL)


def test_aggregate_status_fail():
    """Test status aggregation for an array of statuses including a failure."""
    # Any number of failing asserts means the overall status is failing
    assert aggregate_status(
        [
            Assert("a1", STATUS_PASS, "message"),
            Assert("a2", STATUS_PASS, "message"),
            Assert("a3", STATUS_FAIL, "message"),
        ]
    ) == (1, STATUS_FAIL)


def test_aggregate_status_pass():
    """Test status aggregation for an array of statuses including only passing statuses."""
    # All passing asserts means the overall status is passing
    assert aggregate_status(
        [Assert("a1", STATUS_PASS, "message"), Assert("a2", STATUS_PASS, "message")]
    ) == (0, STATUS_PASS)
