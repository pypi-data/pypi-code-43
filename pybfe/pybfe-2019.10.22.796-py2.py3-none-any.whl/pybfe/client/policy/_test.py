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
"""Contains logic for updating and storing Tests."""

import json
from typing import Any, Dict, List, TYPE_CHECKING, Text

from pybfe.client.policy._common import aggregate_status
from pybfe.datamodel.policy import Policy, Test

if TYPE_CHECKING:
    from pybfe.client.session import Session


def _get_test_details(test):
    # type: (Test) -> Dict[Text, List[Any]]
    """Get test details (Assert summaries) for this test."""
    return {
        "assertions": [a.get_summary() for a in test.asserts],
        "questions": [q.get_summary() for q in test.questions],
    }


def write_test(test, policy, session, snapshot):
    # type: (Test, Policy, Session, Text) -> None
    """Write test details (Assert summaries) to the remote service in the specified session."""
    test_summary_resource = "policies/{}/{}/{}".format(
        policy.name, policy.id, test.name
    )
    data = _get_test_details(test)
    session.put_snapshot_object(
        test_summary_resource, json.dumps(data), snapshot=snapshot
    )


def update_test_status(test):
    # type: (Test) -> None
    """Update test status based on assertion statuses."""
    not_passing_count, status = aggregate_status(test.asserts)
    test.count = len(test.asserts)
    test.not_pass_count = not_passing_count
    test.status = status
