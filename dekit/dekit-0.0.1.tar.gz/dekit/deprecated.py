import functools
import warnings


def deprecated(func):
    """The decorated function is marked deprecated and a deprecation warning
    will be shown if the function is called.

    :param func: the function to be deprecated
    :return: the decorated function
    """

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        warn_msg = 'This method has been deprecated'
        warnings.warn(message=warn_msg, category=DeprecationWarning,
                      stacklevel=2)
        return func(*args, **kwargs)

    return func_wrapper
