import logging
import threading
from functools import wraps

logger = logging.getLogger(__name__)


def synchronized(func):
    func.__thread_locker_synchronized = threading.Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        with func.__thread_locker_synchronized:
            result = func(*args, **kwargs)
        return result

    return wrapper


def onecase(func):
    func.__thread_locker_onecase = threading.Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        if func.__thread_locker_onecase.locked():
            return
        with func.__thread_locker_onecase:
            return func(*args, **kwargs)

    return wrapper
