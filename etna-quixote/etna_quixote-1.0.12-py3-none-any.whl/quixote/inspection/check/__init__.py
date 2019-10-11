from typing import Type
from quixote.inspection import get_inspection_result, KOError


def fail(message: str, error_kind: Type = KOError):
    """
    Fail unconditionally

    :param message:             a contextual message providing information about the failure
    :param error_kind:          the type of exception to raise (must be of or inherit from KOError and InternalError)
    """

    raise error_kind(message)


def assert_true(condition: bool, message: str, error_kind: Type = KOError):
    """
    Assert that a given condition is True (or raise an exception)

    :param condition:           the condition expected to be True
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    if not condition:
        fail(message, error_kind=error_kind)


def assert_false(condition: bool, message: str, error_kind: Type = KOError):
    """
    Assert that a given condition is False (or raise an exception)

    :param condition:           the condition expected to be False
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    return assert_true(not condition, message, error_kind=error_kind)


def assert_equal(a, b, message: str, error_kind: Type = KOError):
    """
    Assert that ``a == b`` is True (or raise an exception)

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    return assert_true(a == b, message, error_kind=error_kind)


def assert_not_equal(a, b, message: str, error_kind: Type = KOError):
    """
    Assert that ``a != b`` is True (or raise an exception)

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    return assert_true(a != b, message, error_kind=error_kind)


def assert_greater_than(a, b, message: str, error_kind: Type = KOError):
    """
    Assert that ``a > b`` is True (or raise an exception)

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    return assert_true(a > b, message, error_kind=error_kind)


def assert_greater_or_equal(a, b, message: str, error_kind: Type = KOError):
    """
    Assert that ``a >= b`` is True (or raise an exception)

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    return assert_true(a >= b, message, error_kind=error_kind)


def assert_less_than(a, b, message: str, error_kind: Type = KOError):
    """
    Assert that ``a < b`` is True (or raise an exception)

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    return assert_true(a < b, message, error_kind=error_kind)


def assert_less_or_equal(a, b, message: str, error_kind: Type = KOError):
    """
    Assert that ``a <= b`` is True (or raise an exception)

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message providing information about how / why the assertion failed
    :param error_kind:          the type of exception to raise if the assertion fails (must be of or inherit from KOError and InternalError)
    """

    return assert_true(a <= b, message, error_kind=error_kind)


def expect_true(condition: bool, message: str, nb_points: int = 1) -> bool:
    """
    Expect that a given condition is True to grant a given number of points

    :param condition:           if not True the requirement is considered failed
    :param message:             a contextual message describing the requirement and (optionally) providing feedback
    :param nb_points:           the number of points granted by the requirement if it passes
    """

    requirements = get_inspection_result()["requirements"]
    check = condition
    requirements.append((check, message, nb_points))
    return check


def expect_false(condition: bool, message: str, nb_points: int = 1) -> bool:
    """
    Expect that a given condition is False to grant a given number of points

    :param condition:           if not True the requirement is considered failed
    :param message:             a contextual message describing the expectation and (optionally) providing feedback
    :param nb_points:           the number of points granted by the expectation if it passes
    """

    return expect_true(not condition, message, nb_points=nb_points)


def expect_equal(a, b, message: str, nb_points: int = 1) -> bool:
    """
    Expect that ``a == b`` is True to grant a given number of points

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message describing the expectation and (optionally) providing feedback
    :param nb_points:           the number of points granted by the expectation if it passes
    """

    return expect_true(a == b, message, nb_points=nb_points)


def expect_not_equal(a, b, message: str, nb_points: int = 1) -> bool:
    """
    Expect that ``a != b`` is True to grant a given number of points

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message describing the expectation and (optionally) providing feedback
    :param nb_points:           the number of points granted by the expectation if it passes
    """

    return expect_true(a != b, message, nb_points=nb_points)


def expect_greater_than(a, b, message: str, nb_points: int = 1) -> bool:
    """
    Expect that ``a > b`` is True to grant a given number of points

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message describing the expectation and (optionally) providing feedback
    :param nb_points:           the number of points granted by the expectation if it passes
    """

    return expect_true(a > b, message, nb_points=nb_points)


def expect_greater_or_equal(a, b, message: str, nb_points: int = 1) -> bool:
    """
    Expect that ``a >= b`` is True to grant a given number of points

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message describing the expectation and (optionally) providing feedback
    :param nb_points:           the number of points granted by the expectation if it passes
    """

    return expect_true(a >= b, message, nb_points=nb_points)


def expect_less_than(a, b, message: str, nb_points: int = 1) -> bool:
    """
    Expect that ``a < b`` is True to grant a given number of points

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message describing the expectation and (optionally) providing feedback
    :param nb_points:           the number of points granted by the expectation if it passes
    """

    return expect_true(a < b, message, nb_points=nb_points)


def expect_less_or_equal(a, b, message: str, nb_points: int = 1) -> bool:
    """
    Expect that ``a <= b`` is True to grant a given number of points

    :param a:                   the first object to consider
    :param b:                   the second object to consider
    :param message:             a contextual message describing the requirement and (optionally) providing feedback
    :param nb_points:           the number of points granted by the requirement if it passes
    """

    return expect_true(a <= b, message, nb_points=nb_points)
