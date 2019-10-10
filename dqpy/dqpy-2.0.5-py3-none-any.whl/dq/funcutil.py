import logging
from functools import wraps

from dq.logging import error

logger = logging.getLogger(__name__)


def safe_invoke(noreturn=False):
    """Invoke a function safely.

    :param boolean noreturn: Whether the function being called has no return
        value itself. Default to False. If True and the function returns
        successfully, True will be returned. None will be returned upon failure
        no matter whether the function has return value.
    :returns func: The decorator function that provides safe invocation.
    """
    def safe_invoke_deco(func):
        """Decorator that captures an underlying error."""
        @wraps(func)
        def decorated_func(*args, **kwargs):
            try:
                retval = func(*args, **kwargs)
                return True if noreturn else retval
            except Exception as e:
                error(logger, 'Error invoking {}'.format(func.__qualname__), {
                    'function': func.__qualname__, 'module': func.__module__,
                    'args': args, 'kwargs': kwargs, 'error': e,
                })
                return None
        return decorated_func

    return safe_invoke_deco
