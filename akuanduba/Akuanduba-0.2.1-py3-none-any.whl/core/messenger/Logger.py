__all__ = ['LoggingLevel', 'Logger']

import logging
from Akuanduba.core.utilities import retrieve_kw
from Akuanduba.core.gtypes import EnumStringification

class FatalError(RuntimeError):
  pass

class LoggingLevel ( EnumStringification ):
  #
  #   A wrapper for logging levels, which allows stringification of known log
  #   levels.
  #
  VERBOSE  = logging.DEBUG - 1
  DEBUG    = logging.DEBUG
  INFO     = logging.INFO
  WARNING  = logging.WARNING
  ERROR    = logging.ERROR
  FATAL    = logging.CRITICAL
  MUTE     = logging.CRITICAL # MUTE Still displays fatal messages.

  @classmethod
  def toC(cls, val):
    val = LoggingLevel.retrieve( val ) 
    if val == cls.VERBOSE:
      val = 0
    else:
      val = val/10
    return val + 1 # There is NIL at 0, DEBUG is 2 and so on.

logging.addLevelName(LoggingLevel.VERBOSE, "VERBOSE")
logging.addLevelName(LoggingLevel.FATAL,    "FATAL" )

def _getAnyException(args):
  exceptionType = [issubclass(arg,BaseException) if type(arg) is type else False for arg in args]
  Exc = None
  if any(exceptionType):
    # Check if any args message is the exception type that should be raised
    args = list(args)
    Exc = args.pop( exceptionType.index( True ) )
    args = tuple(args)
  return Exc, args

def verbose(self, message, *args, **kws):
  """
    Attempt to emit verbose message
  """
  if self.isEnabledFor(LoggingLevel.VERBOSE):
    self._log(LoggingLevel.VERBOSE, message, args, **kws) 

def debug(self, message, *args, **kws):
  """
    Attempt to emit debug message
  """
  if self.isEnabledFor(LoggingLevel.DEBUG):
    self._log(LoggingLevel.DEBUG, message, args, **kws) 

def info(self, message, *args, **kws):
  """
    Attempt to emit debug message
  """
  if self.isEnabledFor(LoggingLevel.INFO):
    self._log(LoggingLevel.INFO, message, args, **kws) 

def warning(self, message, *args, **kws):
  Exc, args = _getAnyException(args)
  if self.isEnabledFor(LoggingLevel.WARNING):
    self._log(LoggingLevel.WARNING, message, args, **kws) 
  if Exc is not None:
    if args:
      raise Exc(message % (args if len(args) > 1 else args[0]))
    else:
      raise Exc(message)

def error(self, message, *args, **kws):
  Exc, args = _getAnyException(args)
  if self.isEnabledFor(LoggingLevel.ERROR):
    self._log(LoggingLevel.ERROR, message, args, **kws) 
  if Exc is not None:
    if args:
      raise Exc(message % (args if len(args) > 1 else args[0]))
    else:
      raise Exc(message)

def fatal(self, message, *args, **kws):
  """
    Attempt to emit fatal message
  """
  Exc, args = _getAnyException(args)
  if Exc is None: Exc = FatalError
  if self.isEnabledFor(LoggingLevel.FATAL):
    self._log(LoggingLevel.FATAL, message, args, **kws) 
  if args:
    raise Exc(message % (args if len(args) > 1 else args[0]))
  else:
    raise Exc(message)

logging.Logger.verbose = verbose
logging.Logger.debug = debug
logging.Logger.info = info
logging.Logger.warning = warning
logging.Logger.error = error
logging.Logger.fatal = fatal

# The logger main object
class Logger(object):

  #
  # >>> Internal method to get the formatter custom obj.
  #
  def _getFormatter(self):

    class Formatter(logging.Formatter):

      # Normal
      gray = '0;30'
      red = '0;31'
      green = '0;32'
      yellow = '0;33'
      blue = '0;34'
      magenta = '0;35'
      cyan = '0;36'
      white = '0;37'
      
      # Bold
      bold_black = '1;30'
      bold_red = '1;31'
      bold_green = '1;32'
      bold_yellow = '1;33'
      bold_blue = '1;34'
      bold_magenta = '1;35'
      bold_cyan = '1;36'
      bold_white = '1;37'

      reset_seq = "\033[0m"
      color_seq = "\033[%(color)sm"
      colors = {
                 'VERBOSE':  gray,
                 'DEBUG':    cyan,
                 'INFO':     green,
                 'WARNING':  bold_yellow,
                 'ERROR':    red,
                 'FATAL':    bold_red,
               }
  
      # It's possible to overwrite the message color by doing:
      # logger.info('MSG IN MAGENTA', extra={'color' : Logger._formatter.bold_magenta})
  
      def __init__(self, msg):
        logging.Formatter.__init__(self, self.color_seq + msg + self.reset_seq )
  
      def format(self, record):
        if not(hasattr(record,'nl')):
          record.nl = True
        levelname = record.levelname
        if not 'color' in record.__dict__ and levelname in self.colors:
          record.color = self.colors[levelname]
        return logging.Formatter.format(self, record)
  
    formatter = Formatter("%(asctime)s | Py.%(name)-33.33s %(levelname)7.7s %(message)s")
    return formatter
  
  def __init__(self, **kw):
    self._level = retrieve_kw( kw, 'level', LoggingLevel.INFO)
    self._logger = logging.getLogger(self.__class__.__name__)
    ch = logging.StreamHandler()
    ch.setLevel(self._level)
    ch.setFormatter(self._getFormatter())
    self._logger.handlers = []
    self._logger.addHandler(ch)
    self._logger.setLevel(self._level)

  def setLevel(self, lvl):
    self._logger.setLevel(lvl)

  def getLevel(self):
    return self._level

  def getModuleLogger(self):
    return self._logger

