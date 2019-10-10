__all__ = ['Akuanduba']

from Akuanduba.core import Logger, NotSet, LoggingLevel
from Akuanduba.core.messenger.macros import *
from Akuanduba.core import StatusCode
from Akuanduba.core.Watchdog import Watchdog
# Time import (debug purposes)
from time import time

# The main framework base class.
# This class is responsible to build all managers for all classes.
class Akuanduba( Logger ):


  def __init__(self, name, level = LoggingLevel.INFO, use_linux_watchdog = False):
    Logger.__init__(self, level = level)
    import collections
    self._containers = {}
    self._context = NotSet
    self._name = name
    self._useLinuxWatchdog = use_linux_watchdog


  def initialize( self ):

    MSG_INFO( self, 'Initializing Akuanduba...')

    # create the event context. This will be used to hold all dataframes (EDMs)
    # produced during the execution loop. Its possible to attach the thread pointers
    from Akuanduba.core import Context
    self._context = Context("Context")

    # Sets watchdog's context
    Watchdog.setContext(self.getContext())
    if (self._useLinuxWatchdog):
      Watchdog.enableLinuxWatchdog()

    # Create here all dataframes the core needs
    from Akuanduba.core import EventStatus
    self._containers = {
        "EventStatus"     : EventStatus("EventStatus"),
    }
    for key, edm in self._containers.items():
      edm.setContext(self.getContext())
      self.getContext().setHandler(key, edm)

    # Getting all dataframes from user
    from Akuanduba import DataframeManager
    DataframeManager.resume()

    # Loop over dataframes
    for dataframe in DataframeManager.getTools():
      MSG_INFO( self, 'Initializing DATAFRAME with name %s', dataframe.name())
      dataframe.setContext(self.getContext())
      self.getContext().setHandler( dataframe.name(), dataframe )
      dataframe.level = self._level

    # Getting all services (threads)
    from Akuanduba import ServiceManager
    ServiceManager.resume()

    # Loop over services (Threading mode)
    for tool in ServiceManager.getTools():
      if tool.isInitialized(): continue
      MSG_INFO( self, 'Initializing SERVICE with name %s', tool.name())
      self.getContext().setHandler( tool.name() , tool )
      tool.setContext( self.getContext() )
      tool.level = self._level
      if tool.initialize().isFailure():
        MSG_FATAL(self, "Couldn't initialize SERVICE %s.", key)

    # Getting all tools
    from Akuanduba import ToolManager
    ToolManager.resume()

    # Loop over tools list.
    for tool in ToolManager.getTools():
      if tool.isInitialized():continue
      MSG_INFO( self, 'Initializing TOOL with name %s', tool.name())
      self.getContext().setHandler( tool.name() , tool )
      tool.setContext( self.getContext() )
      tool.level = self._level
      if tool.initialize().isFailure():
        MSG_FATAL(self, "Couldn't initialize TOOL %s.", tool.name())

    # Checks for error in the context
    if self.getContext().initialize().isFailure():
      MSG_FATAL(self, "Can not initialize Event Context.")

    # Initialization complete
    MSG_INFO( self, "Event manager initialization completed.")
    return StatusCode.SUCCESS


  def execute(self):

    MSG_INFO( self, 'Running...')
    context = self.getContext()
    status = self.getContext().getHandler("EventStatus")

    from Akuanduba import ToolManager, ServiceManager

    # For any moment, any tool can call terminate to interrupt
    # the while loop and finalize the execute method
    while not status.terminate():
      initTime = time()

      # Services
      MSG_DEBUG( self, "Starting new loop")
      for tool in ServiceManager.getTools():

        MSG_DEBUG( self, "Execute SERVICE %s...",tool.name())
        if( tool.execute( self.getContext() ).isFailure() ):
          MSG_WARNING( self, "Impossible to execute SERVICE %s.", tool.name())

        # Releasing dataframes
        context.releaseAllContainers()

        # Feeding WDTs
        Watchdog.feed(tool.name(), 'execute')

        # Use interrupt to stop the tool stack execution
        if status.stop():
          MSG_DEBUG( self, "Stop stack execution.")
          # stop tool loop and reset the stop flag inside of event
          status.resetStop()
          break

      # Tools
      for tool in ToolManager.getTools():
        MSG_DEBUG( self, "Execute TOOL %s...",tool.name())
        if( tool.execute( self.getContext() ).isFailure() ):
          MSG_WARNING( self, "Impossible to execute TOOL %s.", tool.name())

        # Releasing dataframes
        context.releaseAllContainers()

        # Use interrupt to stop the tool stack execution
        if status.stop():
          MSG_DEBUG( self, "Stop stack execution.")
          # stop tool loop and reset the stop flag inside of event
          status.resetStop()
          break

      MSG_DEBUG( self, "=== Loop time (seconds): %f ===", time() - initTime)

    MSG_INFO( self, 'Stop execute...')

    return StatusCode.SUCCESS


  def finalize(self):

    from Akuanduba import ServiceManager, ToolManager

    # Services
    for tool in ServiceManager.getTools():
      if( tool.finalize().isFailure() ):
        MSG_WARNING( self, "Impossible to execute SERVICE %s.", tool.name())
        return StatusCode.FAILURE

    # Tools
    for tool in ToolManager.getTools():
      if( tool.finalize().isFailure() ):
        MSG_WARNING( self, "Impossible to execute TOOL %s.", tool.name())
        return StatusCode.FAILURE

    return StatusCode.SUCCESS

  def getContext(self):
    return self._context

  def setContext(self, context):
    self._context = context