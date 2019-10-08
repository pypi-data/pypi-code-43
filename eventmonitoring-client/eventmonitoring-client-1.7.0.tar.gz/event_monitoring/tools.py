import os
import sys

from zappa.async import run as zappa_run


def run(function, **kwargs):
    """
    function must be a top level function, not class method, and not decorated function
    """
    if "kwargs" in kwargs:
        kwargs = kwargs["kwargs"]
    if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return function(**kwargs)
    zappa_run(function, kwargs=kwargs)
    return True
