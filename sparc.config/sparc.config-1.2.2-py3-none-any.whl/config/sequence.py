from zope import interface
from zope.component.factory import Factory
from zope.interface.common import mapping, sequence

@interface.implementer(sequence.IReadSequence)
class SparcConfigSequence(list):
    
    def __init__(self, container, key):
        """Init a IReadSequence provider from a container
        
        Init's to the sequence of container values matching key.  If container
        is a mapping, then it returns a single-lenth sequence for the key's
        container value.  If container is a sequence of mappings, then it is
        inited to a sequence of length X where X matches to number container
        mappings that have key.
        
        Args:
            container: Container must either be an iterable mapping, or a 
                       container of iterable mappings.
            key: Container mapping key to build sequence from
        
        Raises: KeyError if container is not an iterable mapping, or a container 
        of iterable mappings.
        
        Returns: IReadSequence provider based on container values for key
        """
        try:
            for name in mapping.IEnumerableMapping:
                getattr(container, name)
            #container is a map
            container = [container[key]] if key in container else []
        except AttributeError:
            #container is a sequence of maps
            new = []
            for map_ in container:
                if key in map_:
                    new.append(map_[key])
            container = new
        super(SparcConfigSequence, self).__init__(container)
SparcConfigSequenceFactory = Factory(SparcConfigSequence)