from abc import ABC, abstractmethod


class ComponentsABC(ABC):

    @property
    @abstractmethod
    def output(self):
        return NotImplementedError('Not implemented')
