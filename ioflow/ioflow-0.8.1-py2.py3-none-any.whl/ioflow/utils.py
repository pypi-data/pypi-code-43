import logging
import functools

logger = logging.getLogger(__name__)


def log_call(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        # logger.info("[] >> {}()".format())
        print(">> {}(*{}, **{})".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)

    return decorator


if __name__ == "__main__":
    @log_call
    def say_hello(msg):
        print("hello, {}".format(msg))

    say_hello("world")

    class World:
        @log_call
        def say_hello(self, msg):
            print("hello, {}".format(msg))

    World().say_hello("world")


