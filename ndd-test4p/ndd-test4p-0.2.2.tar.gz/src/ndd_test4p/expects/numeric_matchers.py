"""
Numeric matchers for the `expects <https://expects.readthedocs.io/en/stable/>`_ library.
"""

import re
from typing import Union

from expects.matchers import Matcher


class approximate(Matcher):  # pylint: disable=invalid-name
    """
    Check that a number is within an acceptable range defined as a percentage.
    The percentage can be expressed either as a float or a string, e.g. ``0.051`` or ``5.1%``.

    :Examples:

    >>> from expects import *
    >>> from ndd_test4p.expects.numeric_matchers import approximate

    >>> expect(2.1).to(approximate(2.0).by('5.1%'))

    >>> expect(2.1).to(approximate(2.0).by(0.051))

    >>> expect(2.1).to(approximate(2.0).by('0.1%'))
    Traceback (most recent call last):
        ...
    AssertionError:
    expected: 2.1 to approximate 2.0
         but: values ​​differ by more than 0.1%

    >>> expect(2.1).to(approximate(2.0).by(0.001))
    Traceback (most recent call last):
        ...
    AssertionError:
    expected: 2.1 to approximate 2.0
         but: values ​​differ by more than 0.1%
    """

    #: The regular expression used to convert a string representing a percentage to a float.
    _PERCENTAGE_REGEX = re.compile(r'(\d+(?:\.\d+)?)%')

    def __init__(self, expected_value: Union[float, int], error_margin: Union[float, int, str] = 0):
        """
        Args:
            expected_value (typing.Union[float, int]): The expected number to compare.
            error_margin (typing.Union[float, int, str]): The percentage of acceptable difference (1 is 100%).
        """
        self._expected = expected_value
        self._expected_value = expected_value
        self._error_margin = error_margin

    def by(self, error_margin: Union[float, int, str]) -> 'approximate':  # pylint: disable=invalid-name
        """
        Args:
            error_margin (typing.Union[float, int, str]): The percentage of acceptable difference (1 is 100%).

        Returns:
            ndd_test4j.expects.numeric_matchers.approximate: The matcher itself.
        """
        if isinstance(error_margin, str):
            self._error_margin = self._percent_to_float(error_margin)
        else:
            self._error_margin = error_margin
        return self

    def _match(self, subject):
        """
        Args:
            subject (typing.Union[float, int]): The actual number to compare.

        Returns:
            (bool, [str]): The result of the comparison and its associated message.
        """
        expected_value_min = self._expected_value * (1 - self._error_margin)
        expected_value_max = self._expected_value * (1 + self._error_margin)
        if subject > expected_value_max or subject < expected_value_min:
            return False, [f'values ​​differ by more than {self._error_margin * 100}%']
        return True, ["values are similar"]

    @staticmethod
    def _percent_to_float(error_margin: str) -> float:
        """
        Convert a string representing a percentage to the corresponding float.

        Args:
            error_margin (str): The percentage of acceptable difference.

        Returns:
            float: The percentage as a float.

        Raises:
            ValueError: if ``error_margin`` ìs not a valid convertible string.
        """
        match = approximate._PERCENTAGE_REGEX.match(error_margin)
        if match is None:
            raise ValueError(f"Percentage must be a string matching '{approximate._PERCENTAGE_REGEX.pattern}'")
        return float(match.group(1)) / 100
