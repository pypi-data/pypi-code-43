from abc import abstractmethod

from arps.core.resource_category import ResourceCategory


class AbstractResource:

    def __init__(self, environment_identifier, identifier,
                 category: ResourceCategory) -> None:
        '''
        Args:
        - environment_identifier: environment identifier where the resource is available
        - identifier: resource unique identifier within the environment
        - category: what type of resource it is
        '''
        self.environment_identifier = environment_identifier
        self.identifier = identifier
        self.category = category

    @property
    @abstractmethod
    def value(self):
        '''Retrieve the internal state of the resource

        '''

    @value.setter
    def value(self, value):
        raise NotImplementedError(f'Does it make sense to modify the internal state of this resource? {self.__class__.__name__}')
