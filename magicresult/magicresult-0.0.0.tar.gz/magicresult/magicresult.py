"""
This module provides a Result type modeled after Results in Rust and Swift. The idea behind this is to force callers
of a function/method to explicitly handle the possibility of an error (via calling `Result.is_ok()`) rather than
having unhandled exceptions that callers do not need to be aware of.
"""

from typing import Generic, Optional, TypeVar, Union, cast

T = TypeVar("T")  # pylint: disable=invalid-name


class EmptyVal:
    """
    Represents an Empty Value to be used as the default argument for the Result class
    """


class ResultMisuseException(Exception):
    """
    An Exception that may be thrown by Result if used in an innapropriate way
    """


class Result(Generic[T]):
    """
    Result is a class made to force explicit error handling modeled after Results in Rust and Swift. A result
    is either a value (of type T) or an error (with an associated error message). Callers must
    call `Result.is_ok()` prior to calling `Result.value()` or `Result.error()` in order to determine which function
    to call.
    """

    _val: Union[T, EmptyVal]
    _error_msg: Union[str, EmptyVal]

    def __init__(
        self,
        val: Union[T, EmptyVal] = EmptyVal(),
        error_msg: Union[str, EmptyVal] = EmptyVal(),
    ) -> None:
        if not isinstance(val, EmptyVal) and not isinstance(error_msg, EmptyVal):
            raise ResultMisuseException(
                "Cannot make a Result with a null value and a null error!"
            )
        if isinstance(val, EmptyVal) and isinstance(error_msg, EmptyVal):
            raise ResultMisuseException(
                "Cannot make a Result with a value and an error!"
            )

        self._val = val
        self._error_msg = error_msg

    def is_ok(self) -> bool:
        """
        :return: True iff this Result contains a value. False otherwise.
        """
        return not isinstance(self._val, EmptyVal)

    def is_error(self) -> bool:
        """
        :return:  True iff this result contains an error. False otherwise.
        """
        return not self.is_ok()

    def value(self) -> T:
        """
        The value associated with a Result. Must call is_ok() and verify that this Result contains a value prior to
        calling this method.

        :return:  The value associated with a Result. Must call is_ok() and verify that this Result contains a value
        """
        if not self.is_ok():
            raise ResultMisuseException(
                "Called Result.value() on a Result containing an error! Error=%s"
                % self._error_msg
            )
        return cast(T, self._val)

    def error(self) -> str:
        """
        The error associated with a Result. Must call is_ok() and verify that this Result contains an error prior to
        calling this method.

        :return:  The error associated with a Result. Must call is_ok() and verify that this Result contains an error
        """
        if self.is_ok():
            raise ResultMisuseException(
                "Called Result.error() on a Result containing a value! Value=%s"
                % self._val
            )
        return cast(str, self._error_msg)

    def __str__(self) -> str:
        if self.is_ok():
            return "Result(val=%s)" % repr(self.value())
        else:
            return "Result(error=%s)" % repr(self.error())

    def __repr__(self) -> str:
        return self.__str__()


def ok(val: T) -> Result[T]:  # pylint: disable=invalid-name
    """
    Create a Result that contains the given value
    :param val:     The value to place in the result
    :return:        A Result containing the given value
    """
    return Result(val=val)


def error(msg: str) -> Result[T]:
    """
    Create a Result representing an error with the given message
    :param msg:     The error message to place in the result
    :return:        A Result representing an error with the given message
    """
    return Result(error_msg=msg)


"""

Example of using the Result type:

import requests
def get_url(url: str) -> Result[str]:
    try:
        rq = requests.get(url)
        if rq.status_code == 200:
            return ok(rq.content.decode('utf-8'))
        else:
            return error("bad status code while getting %s: %s" % (url, rq.status_code))
    except requests.Exception:
        return error("failed to get url %s: %s" % (url, e))
"""

def attempt(val: Result[T]) -> T:
    raise ValueError("This function is never actually called due to macro instantiation! It is the equivalent of returning val.value()")
