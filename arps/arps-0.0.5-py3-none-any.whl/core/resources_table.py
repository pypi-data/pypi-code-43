from typing import Dict, Callable, Any
from collections import defaultdict
import warnings

from arps.core.abstract_resource import AbstractResource
from arps.core.resource_category import ResourceCategory


class ResourcesTableError(Exception):
    '''
    Error raised when there is something wrong while manipulating the resources in the table
    '''


class ResourcesCategories:
    '''
    This class organizes the resources by their categories.
    '''

    def __init__(self):
        self.categories = defaultdict(dict)

    def _add_resource_instance(self, resource_instance: AbstractResource):
        if self._resource_exists(resource_instance.identifier):
            raise ResourcesTableError('Resource Identifier already in the current category')
        self.categories[resource_instance.category][resource_instance.identifier] = resource_instance

    def resources_by_category(self, category: ResourceCategory) -> Dict:
        '''
        Return all instances from a category as a dict of Resource identifier as key and Resource
        instance as value
        '''
        if category in self.categories:
            return self.categories[category]

        raise ResourcesTableError('Category does not exist')

    def resource_by_identifier(self, identifier) -> AbstractResource:
        '''
        Return resource by its global unique identifier

        If resource not found, raise ResourcesTableError
        '''
        for category in self.categories.values():
            try:
                return category[identifier]
            except KeyError:
                pass

        raise ResourcesTableError('Resource Identifier does not exists in any category')

    def _resource_exists(self, identifier) -> bool:
        '''
        Check for the existence of the resource in any of the categories
        '''
        for resources_instance in self.categories.values():
            if identifier in resources_instance.keys():
                return True

        return False


class ResourcesTable:
    '''
    Resources table organizes resources hierarchically:
    - Agent Manager Identifier (which environment the resource is part)
    -- Resources organized by their categories (which category the resource is classified)
    '''

    def __init__(self):
        self.environments = defaultdict(ResourcesCategories)

    def add_resource(self, resource_instance: AbstractResource):
        '''
        Add resource into the resources table. Resources are grouped by environment and category

        Args:
        - resource_instance: instance of class AbstractResource
        '''
        assert isinstance(resource_instance, AbstractResource)
        self.environments[resource_instance.environment_identifier]._add_resource_instance(resource_instance)

    def categories(self, *, environment):
        '''
        Return all categories from a specific environment

        Args:
        - environment: environment identifier
        '''
        return self.environments[environment]

    def add_resources_listener(self, logger: Callable[[Any], bool]):
        '''
        Invoke logger when a resource is modified

        Args:
        - logger: a function expecting a Resouce.Event as parameter to be logged
        '''
        try:
            for resource in self.resources():
                resource.add_listener(logger)
        except AttributeError:
            warnings.warn('This isn\'t supposed to be invoked in real resources')

    def remove_resources_listener(self, logger: Callable[[Any], bool]):
        '''
        Remove logger attached to each resource

        Args:
        - logger: a function expecting a Resouce.Event as parameter to be logged
        '''
        try:
            for resource in self.resources():
                resource.remove_listener(logger)
        except AttributeError:
            warnings.warn('This isn\'t supposed to be invoked in real resources')


    def reset(self):
        '''
        Reset resource state when resource is a fake resource, otherwise do nothing
        '''
        try:
            for resource in self.resources():
                resource.reset()
        except AttributeError:
            warnings.warn('This isn\'t supposed to be invoked in real resources')
            return

    def resources(self):
        '''
        Generator of all resources
        '''
        for environment in self.environments.values():
            for resources_by_categories in environment.categories.values():
                for resource in resources_by_categories.values():
                    yield resource
