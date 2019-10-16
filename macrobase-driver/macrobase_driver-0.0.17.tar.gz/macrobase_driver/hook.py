import inspect
from enum import IntEnum
from asyncio import AbstractEventLoop


class HookNames(IntEnum):
    before_server_start = 0
    # after_server_start = 1    #TODO
    # before_server_stop = 2    #TODO
    after_server_stop = 3


class HookHandler(object):

    def __init__(self, driver, handler):
        super().__init__()
        self._driver = driver
        self._handler = handler

    async def __call__(self, _, loop: AbstractEventLoop):
        if inspect.iscoroutinefunction(self._handler):
            await self._handler(self._driver, self._driver.context, loop)
        else:
            self._handler(self._driver, self._driver.context, loop)
