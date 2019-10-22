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
"""Contains logic for updating and storing Policies."""

import json
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Text

from requests import HTTPError

from pybfe.client.policy._common import aggregate_status
from pybfe.client.policy._test import update_test_status, write_test
from pybfe.datamodel.policy import Assert, CiProperties, Policy, Question, Test

if TYPE_CHECKING:
    from pybfe.client.session import Session


def _get_latest_run(session, name, snapshot):
    # type: (Session, Text, Optional[Text]) -> Optional[Dict]
    """Get the latest run for a given policy name."""
    try:
        policies = json.loads(
            session.get_snapshot_object_text("policies", snapshot=snapshot)
        )
    except HTTPError as e:
        # No matching run
        if e.response.status_code == 404:
            return None
        raise e
    for policy in policies:
        if policy.get("name") == name:
            return policy
    return None


def get_or_create_test(policy, name):
    # type: (Policy, Text) -> Test
    """Get or create the test with the specified name in the specified policy."""
    if name in policy.tests:
        return policy.tests[name]
    test = Test(name)
    policy.tests[name] = test
    return test


def _load_policy_summary(session, policy_name, snapshot):
    # type: (Session, Text, Optional[Text]) -> Optional[List[Dict]]
    """Load the summary for the specified policy from the specified Batfish session."""
    policy_history_rsc = "policies/{}".format(policy_name)
    try:
        return json.loads(
            session.get_snapshot_object_text(policy_history_rsc, snapshot=snapshot)
        )
    except HTTPError as e:
        # Expect 404 when policy does not exist
        if e.response.status_code == 404:
            return None
        raise e


def load_policy(session, policy_name, policy_id=None, snapshot=None):
    # type: (Session, Text, Optional[Text], Optional[Text]) -> Optional[Policy]
    """
    Load the specified policy from the specified Batfish session.

    :param session: session to load the policy from
    :type session: Session
    :param policy_name: name of the policy to load
    :type policy_name: Text
    :param policy_id: unique identifier for the policy run to load, if none is specified the latest run for the specified policy will be loaded
    :type policy_id: Text
    :param snapshot: name of the snapshot to load the policy for, defaults to the Session's current snapshot
    :type snapshot: Text
    :return: Policy if a matching policy exists, otherwise None
    """
    # Get latest policy ID from list of policies if none is provided
    if policy_id is None:
        policy_dict = _get_latest_run(session, policy_name, snapshot)
        if not policy_dict:
            return None
        policy_id = policy_dict.get("id")

    policy_history = _load_policy_summary(session, policy_name, snapshot)
    # Policy doesn't exist
    if policy_history is None:
        return None

    ci_props = None
    timestamp = None
    for policy in policy_history:
        if policy.get("name") == policy_name and policy.get("id") == policy_id:
            ci_props = CiProperties.from_dict(policy.get("ci_props", {}))
            timestamp = policy.get("timestamp")
            break

    policy_details_rsc = "policies/{}/{}".format(policy_name, policy_id)

    # Fetch list of Test dictionaries for the specified policy from service
    tests = list()
    try:
        test_dicts = json.loads(
            session.get_snapshot_object_text(policy_details_rsc, snapshot=snapshot)
        )
    except HTTPError as e:
        # 404 is ok when policy has no tests
        if e.response.status_code != 404:
            raise e
        test_dicts = {}

    for test_dict in test_dicts:
        test_details_rsc = "{}/{}".format(policy_details_rsc, test_dict.get("name"))

        # Fetch list of assertions for each test from service
        test_details_dict = json.loads(
            session.get_snapshot_object_text(test_details_rsc, snapshot=snapshot)
        )
        asserts = [_to_assertion(a) for a in test_details_dict.get("assertions")]
        test_name = test_dict.get("name")
        test_qs = [_to_question(q) for q in test_details_dict.get("questions")]
        tests.append(Test(name=test_name, asserts=asserts, questions=test_qs))

    p = Policy(
        policy_name, policy_id, ci_props=ci_props, tests=tests, timestamp=timestamp
    )
    _update_policy_status(p)
    return p


def _to_assertion(assert_dict):
    # type: (Dict[Text, Any]) -> Assert
    """Convert assertion dictionary into an assertion object."""
    name = str(assert_dict.get("name"))
    status = str(assert_dict.get("status"))
    message = str(assert_dict.get("message"))
    return Assert(
        name=name,
        status=status,
        message=message,
        expected=assert_dict.get("expected"),
        actual=assert_dict.get("actual"),
        key_present=assert_dict.get("key_present"),
        questions=[_to_question(q) for q in assert_dict.get("questions", [])],
    )


def _to_question(question_dict):
    # type: (Dict[Text, Any]) -> Question
    """Convert question dictionary into a question object."""
    return Question(name=question_dict.get("name"))


def _get_policy_details(policy):
    # type: (Policy) -> List[Dict]
    """Get policy details (Test summaries) for this policy."""
    return [policy.tests[t].get_summary() for t in policy.tests]


def _update_policies_summary(policy, session, snapshot):
    # type: (Policy, Session, Text) -> None
    """Add this policy run to the list of policies on the remote service."""
    policies_resource = "policies"
    policy_summary = policy.get_summary()

    # Insert policy summary to latest-runs-summary
    try:
        latest_policy_summaries = json.loads(
            session.get_snapshot_object_text(policies_resource, snapshot=snapshot)
        )
        for i in range(len(latest_policy_summaries)):
            prev_policy = latest_policy_summaries[i]
            if prev_policy.get("name") == policy.name:
                del latest_policy_summaries[i]
                break
        latest_policy_summaries.append(policy_summary)
    except HTTPError as e:
        # No run summaries exist yet, add this as the first
        if e.response.status_code == 404:
            latest_policy_summaries = [policy_summary]
        else:
            raise e
    session.put_snapshot_object(
        policies_resource, json.dumps(latest_policy_summaries), snapshot=snapshot
    )


def _update_policy_history(policy, session, snapshot):
    # type: (Policy, Session, Text) -> None
    """Add this policy run to the policy's history on the remote service."""
    policy_history_resource = "policies/{}".format(policy.name)
    policy_summary = policy.get_summary()

    # Append policy summary to run history data
    try:
        policy_history = json.loads(
            session.get_snapshot_object_text(policy_history_resource, snapshot=snapshot)
        )
        # Replace existing policy data with the same name and id
        # This happens when the policy is written multiple times while it is being run, e.g. after each test
        for i, prev_run in enumerate(policy_history):
            if prev_run.get("name") == policy.name and prev_run.get("id") == policy.id:
                del policy_history[i]
                break
        policy_history.append(policy_summary)
    except HTTPError as e:
        # No run history exists yet, add this as the first
        if e.response.status_code == 404:
            policy_history = [policy_summary]
        else:
            raise e
    session.put_snapshot_object(
        policy_history_resource, json.dumps(policy_history), snapshot=snapshot
    )


def _write_policy_details(policy, session, snapshot):
    # type: (Policy, Session, Text) -> None
    """Add policy details (Test summaries) for this policy to the remote service."""
    specific_policy_resource = "policies/{}/{}".format(policy.name, policy.id)
    session.put_snapshot_object(
        specific_policy_resource,
        json.dumps(_get_policy_details(policy)),
        snapshot=snapshot,
    )


def _write_policy(policy, session, snapshot):
    # type: (Policy, Session, Text) -> None
    """
    Write policy data to the specified session.

    Updates three things: list of all policies, history for this policy, and policy details for this policy run.
    """
    _update_policies_summary(policy, session, snapshot)
    _update_policy_history(policy, session, snapshot)
    _write_policy_details(policy, session, snapshot)


def write_policy(policy, session, snapshot=None):
    # type: (Policy, Session, Optional[Text]) -> None
    """
    Write policy run and child details to the specified session.

    :param policy: policy to write
    :type policy: Policy
    :param session: session to write the policy run details to
    :type session: Session
    :param snapshot: name of the snapshot the policy is associated with
    :type snapshot: Text
    """
    snap = session.get_snapshot(snapshot)
    # Update status (of children and self) before writing summaries
    _update_policy_status(policy)
    _write_policy(policy, session=session, snapshot=snap)
    for t in policy.tests:
        write_test(policy.tests[t], policy, session=session, snapshot=snap)


def _update_policy_status(policy):
    # type: (Policy) -> None
    """Update test and policy statuses based on their children (asserts and tests, respectively)."""
    # Update tests first since policy status depends on test status
    count = 0
    if policy.tests:
        for t in policy.tests:
            update_test_status(policy.tests[t])
        count = len(policy.tests)

    not_passing_count, status = aggregate_status(
        [policy.tests[t] for t in policy.tests]
    )
    policy.count = count
    policy.not_pass_count = not_passing_count
    policy.status = status
