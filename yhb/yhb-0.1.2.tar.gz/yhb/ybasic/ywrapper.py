import functools
import traceback


class MaxRetryExceeds(Exception):
    pass


def retry_wrapper(n):
    def _retry_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            max_try = n
            while max_try:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    max_try -= 1
                    if max_try <= 0:
                        raise MaxRetryExceeds
                    traceback.print_exc()
                    print(e)

        return wrapper

    return _retry_wrapper
