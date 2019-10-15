from guillotina.interfaces import IContainer
from typing import Awaitable
from zope.interface import Interface


class IEvolutionUtility(Interface):
    def register(self, version: int, evolver: Awaitable):
        pass

    async def evolve(self, container: IContainer):
        pass
