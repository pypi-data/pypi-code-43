__all__ = ["Context"]

from Akuanduba.core import Logger, NotSet
from Akuanduba.core.messenger.macros import *
from Akuanduba.core import StatusCode
from Akuanduba.core.CoreClasses import AkuandubaDataframe

class Context(Logger):

  def __init__(self, t):
    Logger.__init__(self) 
    import collections
    self._containers = collections.OrderedDict()
    self._lockedContainers = []
    self._decoration = dict()

  def setHandler(self, key, obj):
    if key in self._containers.keys():
      MSG_ERROR( self, "Key %s exist into the event context. Attach is not possible...",key)
    else:
      self._containers[key]=obj

  def getHandler(self,key):
    if not key in self._containers.keys():
      MSG_ERROR (self, "Tried to access key {} but it's not yet set.".format(key))
      return NotSet
    else:
      handler = self._containers[key]
      if issubclass(type(handler), AkuandubaDataframe):
        MSG_DEBUG(self, "Acquiring lock from {} dataframe".format(handler.name()))
        handler.acquire()
        self._lockedContainers.append (handler.name())
        return handler
      else:
        return handler

  def releaseContainer (self, key):
    if not key in self._lockedContainers:
      MSG_ERROR (self, "Tried to release container {} but it's not on the locked list".format(key))
      return NotSet
    else:
      container = self._containers[key]
      MSG_DEBUG(self, "Releasing lock from {} dataframe".format(container.name()))
      container.release()
      self._lockedContainers.remove(key)

  def releaseAllContainers (self):
    for key in self._lockedContainers:
      self.releaseContainer(key)
    
    if (len(self._lockedContainers) != 0):
      self.releaseAllContainers()

  def execute(self):
    for key, edm in self._containers.items():
      if edm.execute().isFailure():
        MSG_WARNING( self,  'Can not execute the dataframe %s', key )
    return StatusCode.SUCCESS

  def initialize(self):
    return StatusCode.SUCCESS

  def finalize(self):
    return StatusCode.SUCCESS

  def setDecor(self, key, v):
    self._decoration[key] = v

  def getDecor(self,key):
    try:
      return self._decoration[key]
    except KeyError:
      MSG_WARNING( self, 'Decoration %s not found',key)

  def clearDecorations(self):
    self._decoration = dict()

  def decorations(self):
    return self._decoration.keys()