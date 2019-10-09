__all__ = ["ServiceManager", "ToolManager", "DataframeManager"]

from Akuanduba.core.messenger import Logger
from Akuanduba.core.messenger.macros import *
from Akuanduba.core import AkuandubaTool, AkuandubaService, AkuandubaDataframe, NotSet, StatusCode
from Akuanduba.core.constants import *

class Manager ( Logger ):

  def __init__(self, name, mgrType = NotSet):
    Logger.__init__(self)
    import collections
    self._name = name
    if (mgrType not in ['Dataframe', 'Tool', 'Service']) or (mgrType == NotSet):
      MSG_ERROR(self, "Couldn't create Manager with type {}".format(mgrType))
    self._mgrType = mgrType
    self._collection = collections.OrderedDict()
    MSG_INFO( self, "Creating {} as a {} manager...".format(name, mgrType))

  def name(self):
    return self._name

  def get(self, name):
    return self._collection[name]

  def put(self, tool):
    self._collection[ tool.name() ] =  tool

  def __iter__(self):
    for _, tool in self._collection.items():
      yield tool

  def disable(self):
    for name, tool in self._collection.items():
      MSG_DEBUG(self, "Disable {} {}".format(name, self._mgrType))
      tool.disable()

  def enable(self):
    for name, tool in self._collection.items():
      MSG_DEBUG(self, "Enable {} {}".format(name, self._mgrType))
      tool.enable()

  def push_back(self, tool):

    if self._mgrType == 'Dataframe':
      if not issubclass(type(tool), AkuandubaDataframe):
        MSG_FATAL (self, "{} must have inheritance from AkuandubaDataframe. Is it a {}?".format(self._name, self._mgrType))

    elif self._mgrType == 'Tool':
      if not issubclass(type(tool), AkuandubaTool):
        MSG_FATAL (self, "{} must have inheritance from AkuandubaTool. Is it a {}?".format(self._name, self._mgrType))

    elif self._mgrType == 'Service':
      if not issubclass(type(tool), AkuandubaService):
        MSG_FATAL (self, "{} must have inheritance from AkuandubaService. Is it a {}?".format(self._name, self._mgrType))

    else:
      MSG_FATAL (self, "{} shouldn't be here. What is this?".format(self._name))

    if not tool.name() in self._collection.keys():
      self._collection[tool.name()] = tool
    else:
      MSG_FATAL(self, "{} {} already exists in this manager's collection. Please include this with another name...".format(self._mgrType, tool.name()))

  def __add__(self, tool):
    self.push_back( tool )
    return self

  def clear(self):
    self._collection.clear()

  def resume(self):
    MSG_INFO( self, "{}: {}".format(self._mgrType, self.name()))
    for _, tool in self._collection.items():
      MSG_INFO( self, " * {} as {}".format(tool.name(), self._mgrType))

  def getTools(self):
    return [ tool for _, tool in self._collection.items() ]

  def retrieve( self, key ):
    if key in self._collection.keys():
      return self._collection[key]
    else:
      MSG_ERROR( self, "{} with name {} not found in this manager".format(self._mgrType, key))


# Use this to attach all services
ServiceManager = Manager("ServiceManager", "Service")

# Use this to attach all tools
ToolManager = Manager("ToolManager", "Tool")

# Use this to attach all dataframes
DataframeManager = Manager("DataframeManager", "Dataframe")