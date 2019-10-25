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
"""Contains class definitions for Policies and related objects."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Text, Union

import attr
import pytz
from pybatfish.util import get_uuid  # type: ignore

STATUS_ERROR = u"Error"
STATUS_FAIL = u"Fail"
STATUS_NOT_FINISHED = u"Not Finished"
STATUS_PASS = u"Pass"


class Policy(object):
    """Class containing results from running a network policy."""

    def __init__(self, name, id_=None, ci_props=None, tests=None, timestamp=None):
        # type: (Text, Optional[Text], Optional[CiProperties], Optional[List[Test]], Optional[Text]) -> None
        """
        Create a new policy run.

        If tests are specified, then their statuses are used to update this run's status.

        :param name: name of the policy
        :type name: Text
        :param id_: unique identifier for this run of the policy
        :type id_: Text
        :param ci_props: Object that contains CI properties
        :type ci_props_: CiProperties
        :param tests: list of tests associated with this policy run, if more than one test of a given name is supplied, only the last is saved to this policy
        :type tests: List[Test]
        :param timestamp: RFC3339 timestamp corresponding to when this policy run started
        :type timestamp: Text
        """
        self.name = name
        self.status = STATUS_NOT_FINISHED
        self.count = 0
        self.not_pass_count = 0
        if id_:
            self.id = id_
        else:
            self.id = get_uuid()
        self.ci_props = ci_props if ci_props is not None else CiProperties()
        if tests is not None:
            self.tests = {t.name: t for t in tests}
        else:
            self.tests = {}
        self.timestamp = (
            datetime.now(tz=pytz.UTC).isoformat("T") if timestamp is None else timestamp
        )

    def get_summary(self):
        # type: () -> Dict[Text, Any]
        """Get the summary dictionary for this policy."""
        return {
            "name": self.name,
            "id": self.id,
            "ci_props": self.ci_props.to_dict(),
            "status": self.status,
            "testMetrics": {"count": self.count, "notPassed": self.not_pass_count},
            "timestamp": self.timestamp,
        }


class Test(object):
    """Class containing network policy test results."""

    def __init__(self, name, asserts=None, questions=None):
        # type: (Text, Optional[List[Assert]], Optional[List[Question]]) -> None
        """
        Create a new test.

        :param name: name of the test
        :type name: Text
        :param asserts: list of asserts associated with this test
        :type asserts: List[Assert]
        :param asserts: list of questions associated with this test
        :type asserts: List[Question]
        """
        self.name = name
        self.status = STATUS_NOT_FINISHED
        self.count = 0
        self.not_pass_count = 0

        assertions = [] if asserts is None else asserts  # type: List[Assert]
        self.asserts = assertions

        qs = [] if questions is None else questions  # type: List[Question]
        self.questions = qs

    def get_status(self):
        # type: () -> Text
        """Get the status for this test."""
        return self.status

    def add_assert(self, assert_):
        # type: (Assert) -> None
        """Add a new Assert to this test."""
        self.asserts.append(assert_)

    def add_question(self, question):
        # type: (Question) -> None
        """Associate a new question with this test."""
        self.questions.append(question)

    def get_summary(self):
        # type: () -> Dict[Text, Union[Text, Dict[Text, int]]]
        """Get the summary dictionary for this test."""
        return {
            "name": self.name,
            "status": self.status,
            "assertMetrics": {"count": self.count, "notPassed": self.not_pass_count},
        }


class Assert(object):
    """Class containing network policy assert results."""

    def __init__(
        self,
        name,
        status,
        message,
        expected=None,
        actual=None,
        key_present=None,
        questions=None,
    ):
        # type: (Text, Text, Text, Optional[Any], Optional[Any], Optional[bool], Optional[List[Question]]) -> None
        """
        Create a new assert.

        :param name: name of the assert
        :type name: Text
        :param status: status of the assert
        :type status: Text
        :param message: message describing the assertion result
        :type message: Text
        :param expected: value expected by the assertion
        :type expected: Any
        :param actual: actual value evaluated by the assertion
        :type actual: Any
        :param key_present: `False` indicates the actual value did not exist (e.g. an expected fact did not exist on the inspected node)
        :type key_present: bool
        :param questions: questions associated with this assertion
        :type questions: List[Question]
        """
        self._name = name
        self._status = status
        self._message = message
        self._expected = expected
        self._actual = actual
        self._key_present = key_present
        qs = [] if questions is None else questions  # type: List[Question]
        self._questions = qs

    def add_question(self, question):
        # type: (Question) -> None
        """Associate a new question with this assert."""
        self._questions.append(question)

    def get_name(self):
        # type: () -> Text
        """Get the name of this assert."""
        return self._name

    def get_status(self):
        # type: () -> Text
        """Get the status of this assert."""
        return self._status

    def get_summary(self):
        # type: () -> Dict[Text, Any]
        """Get the summary dictionary for this assert."""
        return {
            "name": self._name,
            "status": self._status,
            "message": self._message,
            "expected": self._expected,
            "actual": self._actual,
            "key_present": self._key_present,
            "questions": [q.get_summary() for q in self._questions],
        }

    def get_questions(self):
        # type: () -> List[Question]
        """Get the list of questions associated with this assertion."""
        return self._questions


class Question(object):
    """Class containing information about a question, relevant to a policy."""

    def __init__(self, name):
        """
        Create a new question.

        :param name: name of the question
        :type name: Text
        """
        self._name = name

    def get_name(self):
        # type: () -> Text
        """Get the name of this question."""
        return self._name

    def get_summary(self):
        # type: () -> Dict[Text, Any]
        """Get the summary dictionary for this question."""
        return {"name": self._name}


@attr.s(frozen=True)
class CiProperties(object):
    """
    Holding class for CI properties.

    :param url: URL that points to the CI dashboard of the policy run (optional)
    :type name: Text
    """

    url = attr.ib(type=Optional[Text], default=None)

    @classmethod
    def from_dict(cls, json_dict):
        # type: (Dict) -> CiProperties
        """Create the object from the provided dictionary."""
        return CiProperties(url=json_dict.get("url", None))

    def to_dict(self):
        # type: () -> Dict[str, Any]
        """Return the dictionary version of the object."""
        return attr.asdict(self)
