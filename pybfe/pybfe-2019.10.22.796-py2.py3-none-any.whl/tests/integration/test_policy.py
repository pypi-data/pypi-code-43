"""Test policy logic (building, storing, retrieving) with a Batfish service backend."""

import uuid
from os.path import abspath, dirname, join, realpath

import pytest
from pybatfish.exception import BatfishAssertException
from requests import HTTPError

from pybfe.client.policy._policy import load_policy
from pybfe.client.session import Session
from pybfe.datamodel.policy import STATUS_FAIL, STATUS_PASS
from tests.common_util import requires_bfe

_this_dir = abspath(dirname(realpath(__file__)))


@pytest.fixture()
def session():
    return Session()


@pytest.fixture()
def network(session):
    name = session.set_network()
    yield name
    session.delete_network(name)


@pytest.fixture()
def basic_snapshot(session, network):
    name = uuid.uuid4().hex
    session.init_snapshot(join(_this_dir, "snapshots", "basic"), name)
    yield name
    session.delete_snapshot(name)


@pytest.fixture()
def basic_snapshot2(session, network):
    name = uuid.uuid4().hex
    session.init_snapshot(join(_this_dir, "snapshots", "basic"), name)
    yield name
    session.delete_snapshot(name)


def test_policy_no_upload(session, basic_snapshot, monkeypatch):
    """Test that running policies without policy metadata does not error and does not upload any policy data to the backend."""
    # Run an assertion and validate facts as our policy
    session.asserts.assert_no_incompatible_bgp_sessions()
    expected_facts_new = join(_this_dir, "facts", "basic_fail")
    session.validate_facts(expected_facts=expected_facts_new)
    # Should not get any errors up to this point

    # Confirm we get a 404 when fetching the latest-policy-run summaries
    # Since no policy results should be uploaded when no metadata is specified
    with pytest.raises(HTTPError) as e:
        session.get_snapshot_object_text("policies", basic_snapshot)
        assert e.response.status_code == 404


def test_assert_policy(session, basic_snapshot, monkeypatch):
    """Test that running assertions creates the correct policy on the backend."""
    # Assert-metadata like policy name, test name, etc. are read from env vars
    monkeypatch.setenv("bf_policy_name", "p1")
    monkeypatch.setenv("bf_policy_id", "pid1")
    monkeypatch.setenv("bf_test_name", "t1")

    # No incompatible bgp sessions in the snapshot, so assertion should pass
    monkeypatch.setenv("bf_assert_name", "bgp")
    session.asserts.assert_no_incompatible_bgp_sessions()

    # There is an undefined reference, so assertion should fail
    monkeypatch.setenv("bf_assert_name", "ref")
    with pytest.raises(BatfishAssertException):
        session.asserts.assert_no_undefined_references()

    p1 = load_policy(session, "p1")
    # Resulting Policy should be failing due to 1 of 1 test failing
    assert p1.status == STATUS_FAIL
    assert p1.count == 1
    assert p1.not_pass_count == 1
    # Test should fail due to 1 of 2 asserts failing
    test = p1.tests["t1"]
    assert test.get_status() == STATUS_FAIL
    assert test.count == 2
    assert test.not_pass_count == 1
    # bgp assert should be passing
    assert test.asserts[0].get_status() == STATUS_PASS

    # undef ref assert should be failing
    assert test.asserts[1].get_status() == STATUS_FAIL


@requires_bfe("2019.09.01")
def test_assert_policy_question(session, basic_snapshot, monkeypatch):
    """Test that running an assertion creates the correct policy question on the backend."""
    # Assert-metadata like policy name, test name, etc. are read from env vars
    monkeypatch.setenv("bf_policy_name", "p1")
    monkeypatch.setenv("bf_policy_id", "pid1")
    monkeypatch.setenv("bf_test_name", "t1")
    monkeypatch.setenv("bf_assert_name", "bgp")

    # Run an assertion with an underlying question
    session.asserts.assert_no_incompatible_bgp_sessions()

    p1 = load_policy(session, "p1")
    assert p1.count == 1
    test = p1.tests["t1"]
    assert test.count == 1
    # bgp assertion should have one bgp question associated with it
    bgp_qs = test.asserts[0].get_questions()
    assert len(bgp_qs) == 1
    assert "bgp" in bgp_qs[0].get_name()


def test_validate_facts_policy(session, basic_snapshot, monkeypatch):
    """Test that running validate facts creates the correct policy on the backend."""
    # Policy name and id are read from env vars
    monkeypatch.setenv("bf_policy_name", "p1")
    monkeypatch.setenv("bf_policy_id", "pid1")

    # Policy p1 should fail since basic_snapshot is missing Logging servers
    expected_facts_new = join(_this_dir, "facts", "basic_fail")
    session.validate_facts(expected_facts=expected_facts_new)

    p1_new = load_policy(session, "p1")
    # Policy should be failing due to 1 of 1 test failing
    assert p1_new.status == STATUS_FAIL
    assert p1_new.count == 1
    assert p1_new.not_pass_count == 1
    # Test name should correspond to the node checked
    expected_test_name = session._get_fact_test_name("basic")
    assert expected_test_name in p1_new.tests
    # Test should fail due to 2 of 3 asserts failing
    test = p1_new.tests[expected_test_name]
    assert test.get_status() == STATUS_FAIL
    assert test.count == 3
    assert test.not_pass_count == 2

    expected_statuses = {
        "NTP.NTP_Servers": STATUS_PASS,
        "Syslog.Logging_Servers": STATUS_FAIL,
        "Extra_Key": STATUS_FAIL,
    }
    # NTP assert should be passing and Logging and Expected_Key asserts should be failing
    for a in test.asserts:
        assert_name = a.get_name()
        assert assert_name in expected_statuses
        assert expected_statuses[assert_name] == a.get_status()


def test_multiple_policy_runs(session, basic_snapshot, monkeypatch):
    """Test that running running a policy multiple times generates multiple results on the backend."""
    monkeypatch.setenv("bf_policy_name", "p1")
    monkeypatch.setenv("bf_policy_id", "p1_pass")
    # Policy p1 should pass since we're not yet checking for Logging servers
    # in expected facts
    expected_facts_pass = join(_this_dir, "facts", "basic")
    session.validate_facts(expected_facts=expected_facts_pass)

    monkeypatch.setenv("bf_policy_id", "p1_fail")
    # Policy p1 should fail now since basic_snapshot is missing Logging servers
    expected_facts_fail = join(_this_dir, "facts", "basic_fail")
    session.validate_facts(expected_facts=expected_facts_fail)

    # Confirm the old policy can be loaded
    # even though it isn't the most recent with the specified policy name
    p1_pass = load_policy(session, "p1", "p1_pass")
    # Policy should be passing
    assert p1_pass.status == STATUS_PASS

    # Confirm the most recent run of the specified policy is retrieved when
    # no policy ID is specified
    p1_fail = load_policy(session, "p1")
    assert p1_fail.id == "p1_fail"
    # Policy should be failing
    assert p1_fail.status == STATUS_FAIL


def test_multiple_sessions(session, network, basic_snapshot, monkeypatch):
    """Test that running assertions on the same snapshot across multiple sessions creates the correct policy on the backend."""
    # Assert-metadata like policy name, test name, etc. are read from env vars
    monkeypatch.setenv("bf_policy_name", "p1")
    monkeypatch.setenv("bf_policy_id", "pid1")
    monkeypatch.setenv("bf_test_name", "t1")

    # No incompatible bgp sessions in the snapshot, so assertion should pass
    monkeypatch.setenv("bf_assert_name", "bgp")
    session.asserts.assert_no_incompatible_bgp_sessions()

    # Build a second session, unrelated to the first
    tmp_s = Session()
    tmp_s.set_network(network)
    tmp_s.set_snapshot(basic_snapshot)

    # There is an undefined reference, so assertion should fail
    # Even though this assertion is run on another session, it should be associated with the original snapshot and should affect the original policy results
    monkeypatch.setenv("bf_assert_name", "ref")
    with pytest.raises(BatfishAssertException):
        tmp_s.asserts.assert_no_undefined_references()

    p1 = load_policy(session, "p1")
    # Resulting Policy should be failing due to 1 of 1 test failing
    assert p1.status == STATUS_FAIL
    assert p1.count == 1
    assert p1.not_pass_count == 1
    # Test should fail due to 1 of 2 asserts failing
    test = p1.tests["t1"]
    assert test.get_status() == STATUS_FAIL
    assert test.count == 2
    assert test.not_pass_count == 1
    # bgp assert should be passing
    assert test.asserts[0].get_status() == STATUS_PASS
    # undef ref assert should be failing
    assert test.asserts[1].get_status() == STATUS_FAIL


def test_multiple_snapshots(
    session, network, basic_snapshot, basic_snapshot2, monkeypatch
):
    """Test that running assertions across multiple snapshots creates the correct policies on the backend."""
    # Assert-metadata like policy name, test name, etc. are read from env vars
    monkeypatch.setenv("bf_policy_name", "p1")
    monkeypatch.setenv("bf_policy_id", "pid1")
    monkeypatch.setenv("bf_test_name", "t1")
    monkeypatch.setenv("bf_assert_name", "bgp")

    # Run a passing assert on the first snapshot
    session.asserts.assert_no_incompatible_bgp_sessions(snapshot=basic_snapshot)
    # Should see the new policy exists for basic_snapshot only
    assert session._check_policy_exists_locally("p1", "pid1", basic_snapshot)
    assert not session._check_policy_exists_locally("p1", "pid1", basic_snapshot2)
    assert session._check_policy_exists_remotely("p1", "pid1", basic_snapshot)
    assert not session._check_policy_exists_remotely("p1", "pid1", basic_snapshot2)

    # Run a failing assert on the second snapshot
    with pytest.raises(BatfishAssertException):
        session.asserts.assert_no_undefined_references(snapshot=basic_snapshot2)
    # Should now see the new policy exists for basic_snapshot2 as well
    assert session._check_policy_exists_locally("p1", "pid1", basic_snapshot2)
    assert session._check_policy_exists_remotely("p1", "pid1", basic_snapshot2)

    # The metadata will be the same for both policies, but the results should be
    # distinct since they are associated with different snapshots
    p1_ss1 = load_policy(session, "p1", snapshot=basic_snapshot)
    p1_ss2 = load_policy(session, "p1", snapshot=basic_snapshot2)

    # First policy should be passing
    assert p1_ss1.status == STATUS_PASS
    # Second policy should be failing
    assert p1_ss2.status == STATUS_FAIL
