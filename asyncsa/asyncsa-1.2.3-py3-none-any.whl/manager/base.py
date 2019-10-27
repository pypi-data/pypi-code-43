from abc import ABCMeta, abstractmethod


class BaseManager(metaclass=ABCMeta):
    @abstractmethod
    async def connect(self,loop=None,**kwargs):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def get_by_param(self):
        pass

    @abstractmethod
    async def get(self):
        pass

    @abstractmethod
    async def set(self):
        pass

    @abstractmethod
    async def format_query(self):
        pass

    @abstractmethod
    async def set_multi(self):
        pass

    @abstractmethod
    async def all(self):
        pass

    @abstractmethod
    async def instance(self):
        pass

    @abstractmethod
    async def execute(self):
        pass
