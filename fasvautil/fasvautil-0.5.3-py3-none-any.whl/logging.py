import functools
import logging


def error_log(function):
    @functools.wraps(function)
    def _wrap(*args, **kwargs):
        try:
            return function(*args, ** kwargs)
        except BaseException as err:
            if not isinstance(err, KeyboardInterrupt):
                logging.warning('The following error occured: %s', err, exc_info=1)

                raise err

    return _wrap
