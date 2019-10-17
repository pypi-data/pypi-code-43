from zope import interface
from zope.component.factory import Factory
from zope.interface.common.mapping import IEnumerableMapping
from .interfaces import IHierarchyMapping

@interface.implementer(IHierarchyMapping)
class SparcConfigMapping(dict):
    
    def __init__(self, container):
        """Init a IHierarchyMapping provider from a container
        
        Container must either be an iterable mapping, or a container of iterable 
        mappings.
        
        This solves the issue of getting a IHierarchyMapping provider from a 
        container, where you might not know if the container is a mapping or 
        an iterable of mappings.
        
        Raises: KeyError if container is not an iterable mapping, or a container 
        of iterable mappings.
        
        Returns: IHierarchyMapping provider based on container
        """
        try:
            for name in IEnumerableMapping:
                getattr(container, name)
        except AttributeError:
            container = list(container)[::-1] #convert to reverse ordered sequence
            new = {}
            for mapping in container:
                for key in mapping:
                    new[key] = mapping[key]
            container = new
        super(SparcConfigMapping, self).__init__(container)
    
    #IHierarchyMappingValue
    def get_value(self, *args, **kwargs):
        try:
            value = self
            for key in args:
                value = value[key]
            return value
        except KeyError as e:
            if 'default' in kwargs:
                return kwargs['default']
            else:
                raise e
        
    def query_value(self, *args):
        try:
            return self.get_value(*args)
        except KeyError:
            return None
SparcConfigMappingFactory = Factory(SparcConfigMapping)