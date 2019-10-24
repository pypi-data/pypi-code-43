import logging
from functools import wraps
import datetime

log = logging.getLogger('facebook_api_log')  # pick up the log


def write_to_log(func):
    """Decorator function to write to log"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper to put details into log"""
        args_str = [x for x in args]
        kwargs_str = ', '.join([':'.join([str(j) for j in i]) for i in kwargs.items()])
        log.info(f'running function: {func.__name__}, module: {func.__module__} @ {datetime.datetime.now()}')
        log.debug(f'args: {args_str}')
        log.debug(f'kwargs: {kwargs_str}')
        return func(*args, **kwargs)
    return wrapper

