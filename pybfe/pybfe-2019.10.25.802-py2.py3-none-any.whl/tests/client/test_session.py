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
"""Test Enterprise Session functions."""
import json

import pytest
import responses

from pybfe.client.policy._policy import _update_policy_status, write_policy
from pybfe.client.session import Session
from pybfe.datamodel.policy import Policy
from tests.common_util import MockSession


def test_get_policy_by_name_local():
    """Test fetching a policy that exists locally."""
    s = MockSession()
    # Build and store a policy in a mock session
    p1 = Policy(name="p1", id_="pid1")
    s.policies = {"ss1": {"p1": p1}}

    # Confirm the local policy is retrieved successfully
    assert (
        s._get_policy_by_name(policy_name="p1", policy_id="pid1", snapshot="ss1") == p1
    )


def test_get_policy_by_name_missing():
    """Test trying to fetch a non-existent policy."""
    s = MockSession()

    # No matching policy should be fetched, since none exist
    with pytest.raises(ValueError) as e:
        s._get_policy_by_name(policy_name="bogus", policy_id="bogus", snapshot="ss1")
    assert "policy does not exist" in str(e.value)


def test_get_policy_by_name_remote():
    """Test fetching a policy that only exists remotely."""
    s = MockSession()
    p1 = Policy(name="p1", id_="pid1", tests=[])
    _update_policy_status(p1)
    # Write p1 to the (remote) mock service
    write_policy(p1, s, "ss1")

    # Confirm the remote policy is retrieved when its name is specified
    assert (
        s._get_policy_by_name(
            policy_name="p1", policy_id="pid1", snapshot="ss1"
        ).get_summary()
        == p1.get_summary()
    )


def test_get_policy_by_name_local_first():
    """Test fetching a policy that exists locally and remotely."""
    s = MockSession()
    p1_remote = Policy(name="p1", id_="pid1", tests=[])
    _update_policy_status(p1_remote)
    # Write p1 to the (remote) mock service
    write_policy(p1_remote, s, "ss1")

    # Build and store a policy in a mock session
    p1_local = Policy(name="p1", id_="pid1")
    s.policies = {"ss1": {"p1": p1_local}}

    # Confirm the local policy is fetched instead of the remote policy
    get_policy = s._get_policy_by_name(
        policy_name="p1", policy_id="pid1", snapshot="ss1"
    )
    assert get_policy == p1_local


@responses.activate
def test_service_restriction_fail():
    """Test that a session cannot be established to a plain Bf backend."""
    version_url = "http://localhost:9996/v2/version"

    def bf_callback(request):
        return 200, {}, json.dumps({"Batfish": "1.2.3", "Z3": "1.2.3"})

    responses.add_callback(responses.GET, version_url, callback=bf_callback)
    with pytest.raises(ValueError) as e:
        # Trying to connect to a backend that does not have a Batfish-Extension-Pack version should fail
        assert Session(load_questions=False)
    assert "only establish a session with a Batfish Enterprise" in str(e.value)


@responses.activate
def test_service_restriction_succeed():
    """Test that a session can be established to BfE backend."""
    version_url = "http://localhost:9996/v2/version"

    def bfe_callback(request):
        return (
            200,
            {},
            json.dumps(
                {"Batfish": "1.2.3", "Batfish-Extension-Pack": "1.2.3", "Z3": "1.2.3"}
            ),
        )

    responses.add_callback(responses.GET, version_url, callback=bfe_callback)
    # Trying to connect to a backend that has a Batfish-Extension-Pack version should succeed
    assert Session(load_questions=False)


def test_skip_inferring_policy_data_without_policy_id():
    assert Session._get_policy_name() is None
    assert Session._get_test_name() is None


def test_infer_policy_data_from_pytest(monkeypatch):
    """Test we fall back on pytest env when policy/test IDs are missing."""
    monkeypatch.setenv("bf_policy_id", "42")
    assert Session._get_policy_name() == "test_session"
    assert Session._get_test_name() == "test_infer_policy_data_from_pytest"
