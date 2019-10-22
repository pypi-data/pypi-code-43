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
"""Common Policy helper code."""

from typing import Sequence, Text, Tuple, Union

from pybfe.datamodel.policy import (
    Assert,
    STATUS_ERROR,
    STATUS_FAIL,
    STATUS_NOT_FINISHED,
    STATUS_PASS,
    Test,
)


def aggregate_status(list_):
    # type: (Sequence[Union[Assert, Test]]) -> Tuple[int, Text]
    """
    Aggregate statuses for the Tests or Assertions in the supplied list.

    Returns a tuple containing the count of non-passing statuses, and summary status for the supplied objects (e.g. `Fail` if one or more of the items failed).
    """
    fail = False
    not_finished = False
    not_passing_count = 0

    if list_:
        for i in list_:
            status = i.get_status()
            assert status
            if status == STATUS_FAIL or status == STATUS_ERROR:
                not_passing_count += 1
                fail = True
            elif status == STATUS_NOT_FINISHED:
                not_passing_count += 1
                not_finished = True

    status = STATUS_PASS
    if not_finished:
        status = STATUS_NOT_FINISHED
    if fail:
        status = STATUS_FAIL
    return not_passing_count, status
