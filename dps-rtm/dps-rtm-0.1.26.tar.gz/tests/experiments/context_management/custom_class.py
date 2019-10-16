from contextlib import contextmanager
from rtm.main.exceptions import UninitializedError

count = None


class Doubler:

    def __call__(self):
        return self.get_count() * 2

    @staticmethod
    def get_count():
        global count
        if count is None:
            raise UninitializedError(f"Context ({count.__name__}) not set")
        return count


@contextmanager
def set_count(count_):
    global count
    count = count_
    yield
    count = None
