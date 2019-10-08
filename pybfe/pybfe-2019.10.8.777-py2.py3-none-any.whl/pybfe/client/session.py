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
"""Contains class definitions for Enterprise Pybatfish Sessions."""
import operator
import os
from typing import Any, Dict, Optional, Text, Tuple

from pybatfish.client import restv2helper
from pybatfish.client._facts import (
    get_facts, load_facts, validate_facts
)
from pybatfish.client.asserts import (
    _format_df,
    _get_question_object,
    _raise_common,
    assert_filter_denies,
    assert_filter_has_no_unreachable_lines,
    assert_filter_permits,
    assert_no_forwarding_loops,
    assert_no_incompatible_bgp_sessions,
    assert_no_undefined_references,
    assert_no_unestablished_bgp_sessions,
)
from pybatfish.client.restv2helper import get_component_versions
from pybatfish.client.session import (
    Asserts as BaseAsserts, Session as BaseSession,
)
from pybatfish.datamodel import HeaderConstraints, PathConstraints
from pybatfish.datamodel.answer.base import Answer
from pybatfish.exception import BatfishAssertException
from pybatfish.util import get_uuid

from pybfe.client.policy._policy import (
    get_or_create_test, load_policy, write_policy,
)
from pybfe.datamodel.policy import (
    Assert, CiProperties, Policy, Question, STATUS_ERROR, STATUS_FAIL,
    STATUS_PASS, Test
)


class Asserts(BaseAsserts):
    """Contains assertions for a Session."""

    FILTER_DENIES_NAME = "Assert filter denies"
    FILTER_HAS_NO_UNREACHABLE_LINES_NAME = "Assert filter has no unreachable lines"
    FILTER_PERMITS_NAME = "Assert filter permits"
    FLOWS_FAIL_NAME = "Assert flows fail"
    FLOWS_SUCCEED_NAME = "Assert flows succeed"
    NO_FORWARDING_LOOPS_NAME = "Assert no forwarding loops"
    NO_INCOMPATIBLE_BGP_SESSIONS_NAME = "Assert no incompatible BGP sessions"
    NO_INCOMPATIBLE_OSPF_SESSIONS_NAME = "Assert no incompatible OSPF sessions"
    NO_UNESTABLISHED_BGP_SESSIONS_NAME = "Assert no unestablished BGP sessions"
    NO_UNDEFINED_REFERENCES_NAME = "Assert no undefined references"
    VTEP_REACHABILITY_NAME = "Assert all VXLAN VTEPs are reachable from source VTEPs"

    # Name used for asserts when no name is specified or inferred
    DEFAULT_ASSERT_NAME = "No assertion name set"

    def __init__(self, session):
        super(Asserts, self).__init__(session)
        self.current_assertion = None
        # Mapping to hold assertion<->questions association, before the assertion has been performed/created
        self.question_mapping = {}

    def assert_filter_denies(self, filters, headers, startLocation=None,
                             soft=False, snapshot=None, df_format="table"):
        # type: (str, HeaderConstraints, Optional[str], bool, Optional[str], str) -> bool
        """
        Check if a filter (e.g., ACL) denies a specified set of flows.

        :param filters: the specification for the filter (filterSpec) to check
        :param headers: :py:class:`~pybatfish.datamodel.flow.HeaderConstraints`
        :param startLocation: LocationSpec indicating where a flow starts
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param snapshot: the snapshot on which to check the assertion
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        :return: True if the assertion passes
        """
        self._set_assert_name(self.FILTER_DENIES_NAME)
        try:
            val = assert_filter_denies(filters, headers, startLocation, soft,
                                       snapshot, self.session, df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_filter_has_no_unreachable_lines(self, filters, soft=False,
                                               snapshot=None,
                                               df_format="table"):
        # type: (str, bool, Optional[str], str) -> bool
        """
        Check that a filter (e.g. an ACL) has no unreachable lines.

        A filter line is considered unreachable if it will never match a packet,
        e.g., because its match condition is empty or covered completely by those of
        prior lines."

        :param filters: the specification for the filter (filterSpec) to check
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param snapshot: the snapshot on which to check the assertion
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        :return: True if the assertion passes
        """
        self._set_assert_name(self.FILTER_HAS_NO_UNREACHABLE_LINES_NAME)
        try:
            val = assert_filter_has_no_unreachable_lines(filters, soft,
                                                         snapshot,
                                                         self.session,
                                                         df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_filter_permits(self, filters, headers, startLocation=None,
                              soft=False, snapshot=None, df_format="table"):
        # type: (str, HeaderConstraints, Optional[str], bool, Optional[str], str) -> bool
        """
        Check if a filter (e.g., ACL) permits a specified set of flows.

        :param filters: the specification for the filter (filterSpec) to check
        :param headers: :py:class:`~pybatfish.datamodel.flow.HeaderConstraints`
        :param startLocation: LocationSpec indicating where a flow starts
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param snapshot: the snapshot on which to check the assertion
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        :return: True if the assertion passes
        """
        self._set_assert_name(self.FILTER_PERMITS_NAME)
        try:
            val = assert_filter_permits(filters, headers, startLocation, soft,
                                        snapshot, self.session, df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_flows_fail(self, startLocation, headers, soft=False,
                          snapshot=None, df_format="table"):
        # type: (str, HeaderConstraints, bool, Optional[str], str) -> bool
        """
        Check if the specified set of flows, denoted by starting locations and headers, fail.

        :param startLocation: LocationSpec indicating where the flow starts
        :param headers: :py:class:`~pybatfish.datamodel.flow.HeaderConstraints`
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param snapshot: the snapshot on which to check the assertion
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        :return: True if the assertion passes
        """
        self._set_assert_name(self.FLOWS_FAIL_NAME)
        try:
            val = self._assert_flows_fail(startLocation, headers, soft,
                                          snapshot)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def _assert_flows_fail(self, startLocation, headers, soft=False,
                           snapshot=None):
        # type: (str, HeaderConstraints, bool, Optional[str]) -> bool
        __tracebackhide__ = operator.methodcaller("errisinstance",
                                                  BatfishAssertException)

        kwargs = dict(
            pathConstraints=PathConstraints(startLocation=startLocation),
            headers=headers,
            actions="success")

        df = _get_question_object(self.session, 'reachability').reachability(
            **kwargs).answer(snapshot).frame()  # type: ignore
        if len(df) > 0:
            message = "Found a flow that succeed, when expected to fail"
            flow = df.iloc[0]['Flow']
            traces = df.iloc[0]['Traces']
            trace = traces[0]
            extra = ""
            if len(traces) > 1:
                extra = "\nand {} more trace(s) not shown".format(
                    len(traces) - 1)

            return _raise_common("{}\nFlow:\n{}\n\nTrace #1:\n{}{}".format(
                message, flow, trace, extra), soft)
        return True

    def assert_flows_succeed(self, startLocation, headers, soft=False,
                             snapshot=None, df_format="table"):
        # type: (str, HeaderConstraints, bool, Optional[str], str) -> bool
        """
        Check if the specified set of flows, denoted by starting locations and headers, succeed.

        :param startLocation: LocationSpec indicating where the flow starts
        :param headers: :py:class:`~pybatfish.datamodel.flow.HeaderConstraints`
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param snapshot: the snapshot on which to check the assertion
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        :return: True if the assertion passes
        """
        self._set_assert_name(self.FLOWS_SUCCEED_NAME)
        try:
            val = self._assert_flows_succeed(startLocation, headers, soft,
                                             snapshot)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def _assert_flows_succeed(self, startLocation, headers, soft=False,
                              snapshot=None):
        # type: (str, HeaderConstraints, bool, Optional[str]) -> bool
        __tracebackhide__ = operator.methodcaller("errisinstance",
                                                  BatfishAssertException)

        kwargs = dict(
            pathConstraints=PathConstraints(startLocation=startLocation),
            headers=headers,
            actions="failure")

        df = _get_question_object(self.session, 'reachability').reachability(
            **kwargs).answer(snapshot).frame()  # type: ignore
        if len(df) > 0:
            message = "Found a flow that failed, when expected to succeed"
            flow = df.iloc[0]['Flow']
            traces = df.iloc[0]['Traces']
            trace = traces[0]
            extra = ""
            if len(traces) > 1:
                extra = "\nand {} more trace(s) not shown".format(
                    len(traces) - 1)

            return _raise_common("{}\nFlow:\n{}\n\nTrace #1:\n{}{}".format(
                message, flow, trace, extra), soft)
        return True

    def assert_no_forwarding_loops(self, snapshot=None, soft=False,
                                   df_format="table"):
        # type: (Optional[str], bool, str) -> bool
        """Assert that there are no forwarding loops in the snapshot.

        :param snapshot: the snapshot on which to check the assertion
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        """
        self._set_assert_name(self.NO_FORWARDING_LOOPS_NAME)
        try:
            val = assert_no_forwarding_loops(snapshot, soft, self.session,
                                             df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_no_incompatible_bgp_sessions(self, nodes=None, remote_nodes=None,
                                            status=None,
                                            snapshot=None,
                                            soft=False,
                                            df_format="table"):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str], bool, str) -> bool
        """Assert that there are no incompatible BGP sessions present in the snapshot.

        :param nodes: search sessions with specified nodes on one side of the sessions.
        :param remote_nodes: search sessions with specified remote_nodes on other side of the sessions.
        :param status: select sessions matching the specified `BGP session status specifier <https://github.com/batfish/batfish/blob/master/questions/Parameters.md#bgp-session-compat-status-specifier>`_, if none is specified then all statuses other than `UNIQUE_MATCH`, `DYNAMIC_MATCH`, and `UNKNOWN_REMOTE` are selected.
        :param snapshot: the snapshot on which to check the assertion
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        """
        self._set_assert_name(self.NO_INCOMPATIBLE_BGP_SESSIONS_NAME)
        try:
            val = assert_no_incompatible_bgp_sessions(nodes, remote_nodes,
                                                      status,
                                                      snapshot,
                                                      soft, self.session,
                                                      df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_no_incompatible_ospf_sessions(self, nodes=None,
                                             remote_nodes=None,
                                             snapshot=None,
                                             soft=False,
                                             df_format="table"):
        # type: (Optional[str], Optional[str], Optional[str], bool, str) -> bool
        """Assert that there are no incompatible or unestablished OSPF sessions present in the snapshot.

        :param nodes: search sessions with specified nodes on one side of the sessions.
        :param remote_nodes: search sessions with specified remote_nodes on other side of the sessions.
        :param snapshot: the snapshot on which to check the assertion
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        """
        self._set_assert_name(self.NO_INCOMPATIBLE_OSPF_SESSIONS_NAME)
        try:

            from pybatfish.client.asserts import (
                assert_no_incompatible_ospf_sessions
            )
            val = assert_no_incompatible_ospf_sessions(nodes, remote_nodes,
                                                       snapshot,
                                                       soft, self.session,
                                                       df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_no_unestablished_bgp_sessions(self, nodes=None,
                                             remote_nodes=None,
                                             snapshot=None, soft=False,
                                             df_format="table"):
        # type: (Optional[str], Optional[str], Optional[str], bool, str) -> bool
        """Assert that there are no BGP sessions that are compatible but not established.

        :param nodes: search sessions with specified nodes on one side of the sessions.
        :param remote_nodes: search sessions with specified remote_nodes on other side of the sessions.
        :param snapshot: the snapshot on which to check the assertion
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        """
        self._set_assert_name(self.NO_UNESTABLISHED_BGP_SESSIONS_NAME)
        try:
            val = assert_no_unestablished_bgp_sessions(nodes, remote_nodes,
                                                       snapshot, soft,
                                                       self.session, df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_no_undefined_references(self, snapshot=None, soft=False,
                                       df_format="table"):
        # type: (Optional[str], bool, str) -> bool
        """Assert that there are no undefined references present in the snapshot.

        :param snapshot: the snapshot on which to check the assertion
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        """
        self._set_assert_name(self.NO_UNDEFINED_REFERENCES_NAME)
        try:
            val = assert_no_undefined_references(snapshot, soft, self.session,
                                                 df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def assert_vtep_reachability(self, snapshot=None, soft=False,
                                 df_format="table"):
        # type: (Optional[str], bool, str) -> bool
        """Assert that all VXLAN VTEPs are reachable from source VTEPs.

        :param snapshot: the snapshot on which to check the assertion
        :param soft: whether this assertion is soft (i.e., generates a warning but
            not a failure)
        :param df_format: How to format the Dataframe content in the output message.
            Valid options are 'table' and 'records' (each row is a key-value pairs).
        """
        self._set_assert_name(self.VTEP_REACHABILITY_NAME)
        try:
            val = self._assert_vtep_reachability_helper(snapshot, soft,
                                                        df_format)
            return self._common_return(val, snapshot)
        except Exception as e:
            self._record_error(e, snapshot)
            raise e

    def _assert_vtep_reachability_helper(self, snapshot, soft, df_format):
        # type: (Optional[str], bool, str) -> bool
        __tracebackhide__ = operator.methodcaller("errisinstance",
                                                  BatfishAssertException)

        df = _get_question_object(self.session,
                                  'vxlanReachabilityAnalyzer').vxlanReachabilityAnalyzer().answer(
            snapshot).frame()  # type: ignore
        if len(df) > 0:
            return _raise_common(
                "Found unreachable VTEPs, when none were expected\n{}".format(
                    _format_df(df, df_format)), soft)
        return True

    def _set_assert_name(self, name):
        """Set current assert name."""
        self.current_assertion = name

    def _common_return(self, result, snapshot):
        # type: (bool, Optional[str]) -> bool
        # Assert-result is True when the assert passes and False when it fails
        if result:
            return self._record_result(result=result, status=STATUS_PASS,
                                       message='Assertion passed!',
                                       snapshot=snapshot)
        return self._record_result(result=result, status=STATUS_FAIL,
                                   snapshot=snapshot)

    def _record_result(self, result, status, message=None, snapshot=None):
        """Record results for an assertion."""
        p_name = self.session._get_policy_name()
        p_id = self.session._get_policy_id()
        p_ci_props = self.session._get_policy_ci_props()
        t_name = self.session._get_test_name()
        a_name = self.session._get_assert_name()
        if p_name is not None and p_id is not None and t_name is not None:
            self.session._add_assertion(policy_name=p_name, policy_id=p_id,
                                        policy_ci_props=p_ci_props,
                                        test_name=t_name,
                                        assert_name=self.DEFAULT_ASSERT_NAME if a_name is None else a_name,
                                        status=status,
                                        message=message if message else result,
                                        snapshot=snapshot)
        # Clear current assertion name, since the assertion is now finished
        self.current_assertion = None
        return result

    def _record_error(self, e, snapshot):
        """Record results for an assertion which encountered an exception."""
        if isinstance(e, BatfishAssertException):
            return self._record_result(result=str(e), status=STATUS_FAIL,
                                       snapshot=snapshot)
        return self._record_result(result=str(e), status=STATUS_ERROR,
                                   snapshot=snapshot)


class Session(BaseSession):
    """Session for connecting to a Batfish Enterprise service."""

    def __init__(self, **kwargs):
        super(Session, self).__init__(**kwargs)
        self.policies = {}  # type: Dict[Text, Dict[Text, Policy]]
        self.asserts = Asserts(self)  # type: Asserts

        if not self._check_session_is_bfe():
            raise ValueError(
                'Can only establish a session with a Batfish Enterprise backend')

    @staticmethod
    def _get_policy_name():
        # type: () -> Optional[Text]
        """Get current policy name."""
        return os.environ.get('bf_policy_name')

    @staticmethod
    def _get_policy_id():
        # type: () -> Optional[Text]
        """Get current policy id."""
        return os.environ.get('bf_policy_id')

    @staticmethod
    def _get_policy_ci_props():
        # type: () -> CiProperties
        """Get the CI properties."""
        return CiProperties(url=os.environ.get('bf_policy_ci_url'))

    @staticmethod
    def _get_test_name():
        # type: () -> Optional[Text]
        """Get current test name."""
        return os.environ.get('bf_test_name')

    def _get_assert_name(self):
        # type: () -> Optional[Text]
        """
        Get current assert name.

        Name in environment var takes precedence over internal name.
        """
        env_name = os.environ.get('bf_assert_name')
        if env_name:
            return env_name
        return self.asserts.current_assertion

    def _get_question_map_key(self, snapshot=None):
        # type: (Optional[Text]) -> Tuple
        """
        Return the current question mapping key.

        The key returned is a tuple of snapshot, policy name, policy id, test name, and assertion name, based on current policy metadata and snapshot.
        """
        snap = snapshot if snapshot is not None else self.snapshot
        return (
            snap, self._get_policy_name(), self._get_policy_id(),
            self._get_test_name(), self._get_assert_name()
        )

    def _check_session_is_bfe(self):
        # type: (Session) -> bool
        """Check if the session points to a BfE backend."""
        return self._get_bfe_version() is not None

    def _get_bfe_version(self):
        # type: () -> Optional[Text]
        """Get the BfE backend version."""
        return get_component_versions(self).get('Batfish-Extension-Pack')

    def _check_policy_exists_locally(self, policy_name, policy_id, snapshot):
        # type: (Text, Text, Text) -> bool
        """Check if the specified policy exists locally."""
        if snapshot in self.policies:
            if policy_name in self.policies[snapshot]:
                p = self.policies[snapshot][policy_name]
                if p.id == policy_id:
                    return True
        return False

    def _check_policy_exists_remotely(self, policy_name, policy_id, snapshot):
        # type: (Text, Text, Text) -> bool
        """
        Check if the specified policy exists on the remote service.

        If the policy exists remotely, it is loaded and saved locally.
        """
        remote_policy = load_policy(self, policy_name, policy_id, snapshot)
        if remote_policy is not None:
            if snapshot not in self.policies:
                self.policies[snapshot] = {}
            self.policies[snapshot][policy_name] = remote_policy
            return True
        return False

    def _check_policy_exists(self, policy_name, policy_id, snapshot):
        # type: (Text, Text, Text) -> bool
        """Check if the specified policy exists."""
        return (
            self._check_policy_exists_locally(policy_name, policy_id, snapshot)
            or self._check_policy_exists_remotely(policy_name, policy_id,
                                                  snapshot)
        )

    def _get_policy_by_name(self, policy_name, policy_id, snapshot=None):
        # type: (Text, Text, Optional[Text]) -> Policy
        """Get policy object from the specified policy name and ID."""
        snap = self.get_snapshot(snapshot)
        # Check locally first
        if self._check_policy_exists_locally(policy_name, policy_id, snap):
            return self.policies[snap][policy_name]

        # Check backend
        if self._check_policy_exists_remotely(policy_name, policy_id, snap):
            policy = load_policy(self, policy_name, policy_id, snap)
            if policy is not None:
                self.policies.get(snap, {})[policy_name] = policy
                return policy

        raise ValueError(
            'Specified policy does not exist (name:{}, id:{}, snapshot:{}).'.format(
                policy_name,
                policy_id,
                snap))

    def _create_policy(self, policy_name, policy_id, policy_ci_props, snapshot):
        # type: (Text, Text, CiProperties, Text) -> Policy
        """Create a new policy with the specified name and ID.

        This policy is created locally and not written to the remote service.
        """
        p = Policy(policy_name, policy_id, policy_ci_props)
        if snapshot not in self.policies:
            self.policies[snapshot] = {}
        self.policies[snapshot][policy_name] = p
        return p

    def _get_or_create_policy_and_test(self, policy_name, policy_id,
                                       policy_ci_props, test_name,
                                       snap):
        # type: (Text, Text, CiProperties, Text, Text) -> Tuple[Policy, Test]
        """
        Get the specified policy and test from the provided names.

        Creates the policy and test if they don't exist already.
        """
        if self._check_policy_exists(policy_name, policy_id, snap):
            p = self._get_policy_by_name(policy_name, policy_id, snap)
        else:
            p = self._create_policy(policy_name, policy_id, policy_ci_props,
                                    snap)
        t = get_or_create_test(p, test_name)
        return p, t

    def _add_assertion(self, policy_name, policy_id, policy_ci_props, test_name,
                       assert_name,
                       status, message, expected=None, actual=None,
                       key_present=None, write=True, snapshot=None):
        # type: (Text, Text, CiProperties, Text, Text, Text, Text, Optional[Any], Optional[Any], Optional[bool], bool, Optional[Text]) -> None
        """Add a new assertion to the specified test in the specified policy.

        Creates the policy and test if they don't exist already.  The assertion is only written to the remote service if `write=True`
        """
        snap = self.get_snapshot(snapshot)
        p, t = self._get_or_create_policy_and_test(policy_name, policy_id,
                                                   policy_ci_props,
                                                   test_name, snap)
        questions = self.asserts.question_mapping.pop(
            self._get_question_map_key(snapshot), None)
        t.add_assert(Assert(name=assert_name, status=status, message=message,
                            expected=expected, actual=actual,
                            key_present=key_present, questions=questions))
        if write is True:
            # Update the service
            write_policy(p, session=self, snapshot=snap)

    def validate_facts(self, expected_facts, snapshot=None):
        # type: (Text, Optional[Text]) -> Dict[Text, Any]
        """
        Return a dictionary of mismatched facts between the loaded expected facts and the actual facts.

        :param expected_facts: path to directory to read expected fact YAML files from
        :type expected_facts: Text
        :param snapshot: name of the snapshot to validate facts for, defaults to the current snapshot
        :type snapshot: Text
        :return: mismatched facts between expected and actual facts
        :rtype: dict
        """
        kwargs = dict()  # type: Dict[Text, Text]
        if snapshot is not None:
            kwargs.update(snapshot=snapshot)
        actual_facts = get_facts(self, **kwargs)
        expected_facts_ = load_facts(expected_facts)
        return self._validate_facts(expected_facts_, actual_facts)

    def _validate_facts(self, expected_facts, actual_facts):
        # type: (Dict[Text, Any], Dict[Text, Any]) -> Dict[Text, Any]
        """
        Return a dictionary of mismatched facts between the provided expected and actual facts.

        :param expected_facts: expected fact dictionary
        :type expected_facts: dict
        :param actual_facts: actual fact dictionary
        :type actual_facts: dict
        :return: mismatched facts between provided fact dictionaries
        :rtype: dict
        """
        policy_name = self._get_policy_name()
        policy_id_org = self._get_policy_id()
        policy_ci_props = self._get_policy_ci_props()
        policy_id = get_uuid() if policy_id_org is None else policy_id_org

        all_fact_val_results = validate_facts(expected_facts, actual_facts,
                                              verbose=True)
        failing_fact_results = {}  # type: Dict[Text, Any]

        # Update a separate test per node
        for node in all_fact_val_results:
            test_name = self._get_fact_test_name(node)
            vals = all_fact_val_results[node]
            for val in vals:
                # Update a separate assert per property checked
                res = vals[val]
                expected = res.get('expected')
                actual = res.get('actual')
                status = (
                    STATUS_FAIL if res.get(
                        'key_present') is False or expected != actual else STATUS_PASS
                )
                match_msg = 'matched' if status == STATUS_PASS else 'did not match'
                msg = 'Actual {key} ({act}) {match_msg} expected {key} ({exp})'.format(
                    key=val,
                    match_msg=match_msg,
                    exp=expected,
                    act=actual,
                )
                if policy_name is not None:
                    self._add_assertion(policy_name, policy_id, policy_ci_props,
                                        test_name,
                                        val, status, msg, expected, actual,
                                        res.get('key_present'), write=False)

                # Keep track of which facts are failing so those can be returned to user
                if status == STATUS_FAIL:
                    if node not in failing_fact_results:
                        failing_fact_results[node] = {}
                    failing_fact_results[node][val] = vals[val]
        if policy_name is not None:
            # Update the backend only after we've finished processing all asserts
            write_policy(
                self._get_policy_by_name(policy_name, policy_id),
                session=self)

        # Only return mismatched facts
        return failing_fact_results

    def _get_fact_test_name(self, node):
        # type: (Text) -> Text
        """Get fact validation test name for a given node name."""
        return 'Validate facts for node {}'.format(node)

    def get_answer(self, question, snapshot, reference_snapshot=None):
        # type: (str, str, Optional[str]) -> Answer
        """
        Get the answer for a previously asked question.

        :param question: the unique identifier of the previously asked question
        :type question: str
        :param snapshot: name of the snapshot the question was run on
        :type snapshot: str
        :param reference_snapshot: if present, gets the answer for a differential question asked against the specified reference snapshot
        :type reference_snapshot: str
        :return: answer to the specified question
        :rtype: :py:class:`Answer`
        """
        ans = super(Session, self).get_answer(question, snapshot,
                                              reference_snapshot=reference_snapshot)
        p_name = self._get_policy_name()
        p_id = self._get_policy_id()
        p_ci_props = self._get_policy_ci_props()
        t_name = self._get_test_name()
        a_name = self._get_assert_name()
        if p_name is not None and p_id is not None and t_name is not None:
            # We're in a test, so we should associate this question with a test or assertion

            q = Question(question)
            if a_name is not None:
                # Attach the question to current assertion, if one exists
                # Note: at this point, the assertion has not been created,
                # so we cannot directly add the question to it
                q_map_key = self._get_question_map_key(snapshot)
                qs = self.asserts.question_mapping.get(q_map_key, [])
                qs.append(q)
                self.asserts.question_mapping[q_map_key] = qs
                # Assume the assertion will handle writing the updated policy once it completes
            else:
                # Otherwise, just attach the question to the test
                p, t = self._get_or_create_policy_and_test(p_name, p_id,
                                                           p_ci_props, t_name,
                                                           snapshot)
                t.add_question(q)
                write_policy(p, session=self, snapshot=snapshot)
        return ans

    def delete_network_object(self, key):
        # type: (Text) -> None
        """
        Delete the network object with specified key.

        :param key: key identifying the resource to delete
        :type key: Text
        """
        return restv2helper.delete_network_object(self, key)

    def get_network_object_stream(self, key):
        # type: (Text) -> Any
        """
        Return a binary stream of the content of the network object with specified key.

        :param key: key identifying the resource to get
        :type key: Text
        """
        return restv2helper.get_network_object(self, key)

    def get_network_object_text(self, key, encoding='utf-8'):
        # type: (Text, Text) -> Text
        """
        Return the text content of the network object with specified key.

        :param key: key identifying the resource to get
        :type key: Text
        :param encoding: encoding type of the specified object
        :type encoding: Text
        """
        with self.get_network_object_stream(key) as stream:
            text = stream.read().decode(encoding)
        return str(text)

    def get_snapshot_object_stream(self, key, snapshot=None):
        # type: (Text, Optional[Text]) -> Any
        """Return a binary stream of the content of the snapshot object with specified key.

        :param key: key identifying the resource to get
        :type key: Text
        :param snapshot: name of the snapshot under which the resource is stored, uses current snapshot by default
        :type snapshot: Text
        :return: stream containing the resource
        :rtype: Stream
        """
        return restv2helper.get_snapshot_object(self, key, snapshot)

    def get_snapshot_object_text(self, key, encoding='utf-8', snapshot=None):
        # type: (Text, Text, Optional[Text]) -> Text
        """Return the text content of the snapshot object with specified key.

        :param key: key identifying the resource to get
        :type key: Text
        :param snapshot: name of the snapshot under which the resource is stored, uses current snapshot by default
        :type snapshot: Text
        :return: specified resource's text
        :rtype: Text
        """
        with self.get_snapshot_object_stream(key, snapshot) as stream:
            text = stream.read().decode(encoding)
        return str(text)

    def put_snapshot_object(self, key, data, snapshot=None):
        # type: (Text, Any, Optional[Text]) -> None
        """Put data as the snapshot object with specified key.

        :param key: key identifying the resource to upload
        :type key: Text
        :param snapshot: name of the snapshot under which the resource is stored, uses current snapshot by default
        :type snapshot: Text
        """
        restv2helper.put_snapshot_object(self, key, data, snapshot)

    def get_snapshot_input_object_stream(self, key, snapshot=None):
        # type: (Text, Optional[Text]) -> Any
        """Return a binary stream of the content of an input object (part of the original snapshot data) with specified key.

        :param key: key identifying the resource to get
        :type key: Text
        :param snapshot: name of the snapshot under which the resource is stored, uses current snapshot by default
        :type snapshot: Text
        :return: stream containing the resource
        :rtype: Stream
        """
        return restv2helper.get_snapshot_input_object(self, key, snapshot)

    def get_snapshot_input_object_text(self, key, encoding='utf-8',
                                       snapshot=None):
        # type: (Text, Text, Optional[Text]) -> Text
        """Return the text content of an input object (part of the original snapshot data) with specified key.

        :param key: key identifying the resource to get
        :type key: Text
        :param snapshot: name of the snapshot under which the resource is stored, uses current snapshot by default
        :type snapshot: Text
        :return: specified resource's text
        :rtype: Text
        """
        with self.get_snapshot_input_object_stream(key, snapshot) as stream:
            text = stream.read().decode(encoding)
        return str(text)

    def put_network_object(self, key, data):
        # type: (Text, Any) -> None
        """
        Put data as the network object with specified key.

        :param key: key identifying the resource to upload
        :type key: Text
        :param data: data to upload
        :type data: Any
        """
        restv2helper.put_network_object(self, key, data)
