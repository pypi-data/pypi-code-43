from zope.interface.common import mapping   
from zope.interface.exceptions import BrokenImplementation

def _verify_map(container):
    try:
        for name in mapping.IEnumerableMapping:
            getattr(container, name)
    except AttributeError:
        raise BrokenImplementation(mapping.IEnumerableMapping, name)
        
def verify_config_container(object_):
    """Verify object is a valid config container
    
    Valid config containers provide zope.interface.common.mapping.IEnumerableMapping
    or an iterable of zope.interface.common.mapping.IEnumerableMapping.
    
    verification is performed by checking required interfaces attributes 
    against those provided by object_
    
    Raises: zope.interface.exceptions.BrokenImplementation if object_ does not
            fully implement zope.interface.common.mapping.IEnumerableMapping
    """
    try:
        #check for a map
        _verify_map(object_)
    except BrokenImplementation as e:
        #check for a iterable of maps
        try:
            for m in object_:
                _verify_map(m)
        except BrokenImplementation:
            raise e