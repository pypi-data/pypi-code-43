import abc

from macrobase_driver.context import Context
from macrobase_driver.config import BaseConfig


class Endpoint(object, metaclass=abc.ABCMeta):
    """
    Endpoint protocol for processing from macrobase and his drivers
    """

    def __init__(self, context: Context, config: BaseConfig, *args):
        self.context = context
        self.config = config
        self.__name__ = self.__class__.__name__

    async def __call__(self, *args, **kwargs):
        return await self.handle(*args, **kwargs)

    @abc.abstractmethod
    async def handle(self, *args, **kwargs):
        raise NotImplementedError
