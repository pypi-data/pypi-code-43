from zope import interface
from zope.component.factory import Factory
from .interfaces import IConfigContainer
from .mapping import SparcConfigMapping
from .sequence import SparcConfigSequence
from .verify import verify_config_container

@interface.implementer(IConfigContainer)
class SparcConfigContainer(object):
    def __init__(self, container):
        verify_config_container(container if container else [])
        self._container = container
    def mapping(self):
        return SparcConfigMapping(self._container)
    def sequence(self, key):
        return SparcConfigSequence(self._container, key)
SparcConfigContainerFactory = Factory(SparcConfigContainer)