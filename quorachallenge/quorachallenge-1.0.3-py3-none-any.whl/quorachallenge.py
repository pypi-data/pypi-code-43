#!/usr/bin/env python3
# coding=utf-8
"""
# quorachallenge : Quora Challenge Framework

Summary :
    The framework for the Quora development challenges - supporting project description and testing.

Use Case :
    As a entrant in the challenge I want to be able to consistently test the code I enter

Testable Statements :
    ...
"""
from . import _core
from typing import Any, Collection, Sequence, Union
import math
import cmath

import sys

if sys.version_info[0] != 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    raise ImportError('Quora Challenge Framework is only supported on Python 3.6 and later.')

def testdata(challenge_name: str, test_id: str = None, _directory: str = None):
    """Display the test data for the given challenge

    :param str challenge_name: The lower case name for the challenge.
    :param str test_id: The test test_id. If left as the default value this function will display the data for
                all of the test cases.
                If it is not None, then this function will display the data for the test case with that test_id.
    :param str _directory: The base local directory to search for this challenge in. Implemented to allow testing
                of challenges before publication. For Contributor use only.

    *In normal use the test data is downloaded from a remote site, so this function requires an active public internet
    connection.*
    """
    c = _core.Challenge(challenge_name, _directory)
    print(c.testdata(test_id))


def describe(challenge_name: str, webpage: bool = True, _directory: str = None):
    """Display the Description of this challenge

    :param str challenge_name: The lower case name for the challenge.
    :param bool webpage: When True the description is displayed in a tab in the browser. When False the text is
            returned in a raw form - rst formatted.
    :param str _directory: The base local directory to search for this challenge in. Implemented to allow testing of
            challenges before publication. For Contributor use only.

    *In normal use the test data is downloaded from a remote site, so this function requires an active public internet
    connection.*
    """
    c = _core.Challenge(challenge_name, _directory)
    return c.describe(webpage=webpage)


# noinspection PyPep8Naming
class autotest:
    """A callable class/decorator, which will automatically test the function against the challenge requirements.
        By default will immediately report any errors and unexpected exceptions that are raised by the function that
        is decorated.

        :param str challenge_name: The case insensitive name for the challenge.
        :param str test_id: A specific test_id to execute.
        :param bool defer_results: When False the decorator will immediately report test errors and unexpected
                                   exceptions upon completion of the automatic testing.
                                   When True the function will be automatically tested but test failures and exceptions
                                   are recorded but not automatically reported.
        :param str _directory: The base local directory to search for this challenge in. Implemented to allow testing
                of challenges before publication. For Contributor use only.

        When defer_results is True, the test failures and exceptions are accessed via the :ref:`errors<property_errors>`
        and :ref:`exceptions<property_exceptions>` properties. and the :ref:`passed property<property_passed>` provides
        a simple True/False report on whether the requested tests completed without errors or unexpected exceptions.

        *In normal use the test data for the challenge is downloaded from a remote site, so using this function requires
        an active public internet connection.*

        Examples :

        As a decorator:
            .. code-block:: python

                @quorachallenge.solves('dummy_challenge')
                def dummy( a, b):
                    return a +b

        Using an explicit instance of the class
            .. code-block:: python

                def dummy( a, b):
                    return a +b

                solver=quorachallenge.solves('dummy_challenge', defer_results=True)
                passed = solver(dummy)

                if not passed:
                    print(solver.errors)
                    print(solver.exceptions)
    """

    def __init__(self, challenge_name, test_id: str = None, defer_results: bool = None, _directory: str = None):
        self._challenge = _core.Challenge(challenge_name=challenge_name, _directory=_directory)
        resp = self._challenge.fetch('testdata.json')
        self._data = resp.json()
        self._errors = {}
        self._exceptions = {}
        self._successful = set()
        self._defer_results = defer_results
        self._test_id = test_id
        self._testsrun = False
        self._cases_completed = 0

    def __call__(self, test_function: callable) -> bool:
        """Invoking the decorator will automatically test the function"""
        self._errors.clear()
        self._exceptions.clear()
        test_count = 0

        for index, item in enumerate(self._data):
            test_id = item.get('test_id', str(index))
            if self._test_id is not None and test_id != self._test_id:
                continue
            item['test_id'] = test_id
            self._compare(index, item, test_function)
            test_count +=1

        self._cases_completed = test_count

        if not self._defer_results:
            print(f'{self._cases_completed} test cases executed.')
            print('Unexpected exceptions raised:')
            if self._exceptions:
                print('\n'.join(x for x in self._exceptions.values()))
            else:
                print('None')
            print('\nReturn value errors:')
            if self._errors:
                print('\n'.join(x for x in self._errors.values()))
            else:
                print('None')
        self._testsrun = True
        return self.passed

    def _compare(self, row_index: 0, test_row: dict, test_function: callable) -> None:
        """Execute a comparison for this item in the test data"""
        try:
            test_id = test_row['test_id']
            arguments = test_row['arguments']
            expected_return = test_row['return']

            can_raise_name = test_row.get('raises', '')

            # Convert test names from the json into actual exception types
            try:
                can_raise = __builtins__.get(can_raise_name, tuple)
            except AttributeError:
                can_raise = tuple()
            else:
                if not issubclass(can_raise, BaseException):
                    can_raise = tuple()

            expected_return = eval(expected_return)
        except (KeyError, TypeError) as e:
            if 'test_id' not in test_row:
                local_test_id = f'Entry {row_index}'
            else:
                local_test_id = f'Id {test_row["test_id"]}'
            raise ValueError(f"Invalid test data for challenge '{self._challenge.name}' : "
                             f"{local_test_id}: {e}") from None

        try:
            received_return_value = eval(f'test_function({arguments})')
        except SyntaxError as e:
            raise ValueError(f"Invalid data for challenge '{self._challenge.name}' : Id {test_id}: {e!s}") from None

        except can_raise:
            # This is an expected exception for this test case
            return
        except Exception as err:
            err_string = str(err)
            if not err_string:
                err_string = type(err).__name__
            self._exceptions[
                test_id] = f'Unexpected exception raised on Test case test_id {test_id} - ' \
                           f'call {test_function.__name__}({arguments}) - Return value {expected_return!r} expected ' \
                           f'but an Exception raised - {err_string}'
            return

        # compare values
        message = self._compare_values(expected_return, received_return_value)

        if message:
            self._errors[test_id] = f'Test {test_id} - Incorrect result : {message}'
        else:
            self._successful.add(test_id)

    def _compare_values(self, expected: Any, received: Any):
        """"Intelligent value comparison - with context sensitive messaging"""

        if isinstance(expected, list):
            return self._compare_lists(expected, received)

        if isinstance(expected, dict):
            return self._compare_dicts(expected, received)

        if isinstance(expected, str):
            return self._compare_str(expected, received)

        if isinstance(expected, tuple):
            return self._compare_tuples(expected, received)

        if isinstance(expected, float):
            if not math.isclose(expected, received, abs_tol=1e-09):
                return f'Expected ({expected}) !~ Returned ({received})'

        if isinstance(expected, complex):
            if not cmath.isclose(expected, received, abs_tol=1e-09):
                return f'Expected ({expected}) !~ Returned ({received})'

        if expected != received:
            return f'Expected ({expected}) != Returned ({received})'

    def _compare_tuples(self, expected: tuple, received: tuple) -> str:
        """Compare two tuples"""
        return self._compare_iterables(expected, received, tuple)

    def _compare_lists(self, expected: list, received: list) -> str:
        """Compare two lists"""
        return self._compare_iterables(expected, received, list)

    def _compare_str(self, expected: str, received: str) -> str:
        """Compare two strings"""
        return self._compare_iterables(expected, received, str)

    def _compare_iterables(self, expected: Union[Collection, Sequence], received: Union[Collection, Sequence], _type):
        """Intelligent comparison of iterable - tuple, list or str"""
        _type_label = 'list' if _type is list else ('str' if _type is str else 'tuple')

        if not isinstance(received, _type):
            return f'Expected return should be a {_type_label} - got a {type(received)} entries'

        if len(expected) > len(received):
            return f'return is too short - expecting {_type_label} of length {len(expected)}, received {_type_label} ' \
                   f'of length {len(received)}'

        if len(expected) < len(received):
            return f'return is too long - expecting {_type_label} of length {len(expected)}, received {_type_label} ' \
                   f'of length {len(received)}'

        if _type is str:
            if expected != received:
                return f'Expected ({expected}) != received ({received})'
        else:
            for i, (ei, oi) in enumerate(zip(expected, received)):
                res = self._compare_values(ei, oi)
                if res:
                    return f'{_type_label} index {i} : {res}'
            return ''

    @staticmethod
    def _compare_dicts(expected: dict, received: dict):
        """Intelligent comparison of dictionaries"""

        if not isinstance(received, dict):
            return f'Expected return should be a list - got a {type(received)} entries'

        e_keys, o_keys = set(expected.keys()), set(received.keys())

        if e_keys != o_keys:
            missing = e_keys - o_keys
            extra = o_keys - e_keys
            if missing:
                return f'return is missing these expected keys : {",".join(repr(x) for x in missing)}'
            if extra:
                return f'return has these extra keys : {",".join(repr(x) for x in extra)}'

        for key in expected:
            if expected[key] != received[key]:
                return f'Value for key {key} is incorrect - expected {expected[key]} but received {received[key]}'

        return ''

    def results(self, test_id):
        """Return the results for this test test_id if executed

        :param str test_id: The test test_id to be queried

        This methods returns a text string which indicates whether the given test test_id passed successfully, resulted
        in an return value error, or an unexpected exception.

        Returns an empty string if this test test_id has not been executed.
        """
        if test_id in self._successful:
            return 'Test passed'

        if test_id in self._errors:
            return self._errors[test_id]

        if test_id in self._exceptions:
            return self._exceptions[test_id]

        return ''

    @property
    def errors(self) -> list:
        """The list of errors identified during the automated testing your function"""
        return list(self._errors.values())

    @property
    def exceptions(self) -> list:
        """The list of unexpected exceptions identified during the automated testing your function"""
        return list(self._exceptions.values())

    @property
    def passed(self) -> bool:
        """True only if all of the requested tests passed successfully"""
        return self._testsrun and not self.errors and not self.exceptions

    @property
    def executed(self) -> int:
        """The number of test cases executed under this instance on the last run"""
        return self._cases_completed
