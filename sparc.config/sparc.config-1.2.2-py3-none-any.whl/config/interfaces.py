from zope import interface
from zope.interface.common import mapping

class IConfigContainer(interface.Interface):
    def mapping():
        """Return a IHierarchyMapping provider"""
    def sequence(key):
        """Return a zope.interface.common.sequence.IReadSequence provider"""

class IHierarchyMapping(mapping.IEnumerableMapping):
    """A config mapping"""
    def get_value(*args, **kwargs):
        """Return value of key hierarchy
        
        Args:
            One or more mapping keys.  Keys must be listed in order from mapping
            root where first entry lives in root, second entry lives
            under first, so on.
        Kwargs:
            default: value to return if specified key hierarchy is not valid
        Raises:
            KeyError if specified key hierarchy does not exist and default 
            return value is not specified
        
        Returns: Value of specified key hierarchy
        """
    def query_value(*args):
        """Return value of key hierarchy
        
        Same as get_value(), except None is returned for invalid key 
        hierarchies.
        
        Returns: Value of specified key hierarchy, or None if key hierarchy is
                 not valid
        """
