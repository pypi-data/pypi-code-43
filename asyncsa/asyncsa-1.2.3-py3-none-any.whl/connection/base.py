from abc import ABCMeta, abstractmethod


class BaseConnection(metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def connect(self,loop=None,**kwargs):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def get(self):
        pass

    @abstractmethod
    async def set(self):
        pass

    @abstractmethod
    async def bare_set(self):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass

    @abstractmethod
    async def get_transaction(self):
        pass

    @abstractmethod
    def format_sql_result(self):
        pass
