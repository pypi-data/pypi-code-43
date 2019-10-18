from enum import IntEnum


class HookNames(IntEnum):
    before_start = 0
    after_stop = 3


class HookHandler(object):

    def __init__(self, handler):
        super().__init__()
        self._handler = handler

    def __call__(self, *args, **kwargs):
        self._handler(self._driver, self._driver.context)
