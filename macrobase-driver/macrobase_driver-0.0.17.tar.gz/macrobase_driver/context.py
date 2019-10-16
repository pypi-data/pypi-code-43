__all__ = ['Context']

from collections import UserDict

from .exceptions import ContextLockedException


class Context(UserDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_lock = False

    def set(self, key, value):
        if self.is_lock:
            raise ContextLockedException(key)

        self[key] = value

    # def __getitem__(self, key):
    #     return self[key]

    # def __iter__(self):
    #     return super.__iter__()

    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(item)

        return self[item]

    def lock(self):
        self.is_lock = True

    def unlock(self):
        self.is_lock = False
