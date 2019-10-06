import logging
import os
import re
import sys

from .config import Configurable

try:
    from PyQt5   import QtCore
    _has_pyqt = True
except ModuleNotFoundError:
    _has_pyqt = False

logging.VERBOSE  = VERBOSE  = logging.INFO  - 1 # Verbose information messages
logging.VERBOSE2 = VERBOSE2 = logging.INFO  - 2 # (very) Verbose information messages
logging.VERBOSE3 = VERBOSE3 = logging.INFO  - 3 # (very very) Verbose information messages
logging.DEBUG2   = DEBUG2   = logging.DEBUG - 1 # Verbose debug messages
logging.DEBUG3   = DEBUG3   = logging.DEBUG - 2 # (very) Verbose debug messages

if _has_pyqt:
    # Log handler which can be connected to QtSignals
    class QLogSignalHandler(QtCore.QObject, logging.Handler):
        sigLogMessage = QtCore.pyqtSignal(str)

        def __init__(self, parent):
            QtCore.QObject.__init__(self, parent)
            Hlogging.andler.__init__(self)

        def emit(self, record):
            self.sigLogMessage.emit(self.format(record))

_ANSI_ESCAPE_SEQ = re.compile(r"\x1b\[[\d;]+m")

def _remove_ansi_escape_sequences(text):
    return _ANSI_ESCAPE_SEQ.sub("", text)

class PercentStyleMultiline(logging.PercentStyle):
    """
    Log multiline messages with each new line indented to the message start.
    """

    @staticmethod
    def _update_message(record_dict, message):
        tmp = record_dict.copy()
        tmp["message"] = message
        return tmp

    def format(self, record):
        if "\n" in record.message:
            lines = record.message.splitlines()
            formatted = self._fmt % self._update_message(record.__dict__, lines[0])
            indentation = _remove_ansi_escape_sequences(formatted).find(lines[0])
            lines[0] = formatted
            return ("\n" + " " * indentation).join(lines)
        else:
            return self._fmt % record.__dict__

class MultilineFormatter(logging.Formatter):
    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self._style = PercentStyleMultiline(self._style._fmt)


# Because we define custom logging functions in this file
# ... the frame detected by the logging module will be wrong for custom log level functions
# ... so override the current frame function and force it to ignore this file
def currentframe_custom():
    thisfile = os.path.normcase(currentframe_custom.__code__.co_filename)
    frame    = sys._getframe()
    while hasattr(frame, 'f_code'):
        # Note that 'findCaller()' which uses this function ignores the first frame always!
        # ... thus we need to always look at the parent frame for what to ignore
        if frame.f_back is not None:
            co       = frame.f_back.f_code
            filename = os.path.normcase(co.co_filename)

            if filename in (thisfile, _srcfile):
                frame = frame.f_back
                continue
            break
    return frame

currentframe = currentframe_custom

# Custom logging class which defines additional logging levels
# ... for fine tuning what information is logged
class _CustomLogger(logging.getLoggerClass()):

    def verbose1 ( self, *arg, **kw): return super().log(VERBOSE , *arg, **kw)
    def verbose2 ( self, *arg, **kw): return super().log(VERBOSE2, *arg, **kw)
    def verbose3 ( self, *arg, **kw): return super().log(VERBOSE3, *arg, **kw)
    def debug2   ( self, *arg, **kw): return super().log(DEBUG2  , *arg, **kw)
    def debug3   ( self, *arg, **kw): return super().log(DEBUG3  , *arg, **kw)

# Setup system-wide logging configuration
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(MultilineFormatter("%(asctime)s | %(levelname)-8s | %(name)-15s @ %(lineno)4d | %(message)s"))
logging.basicConfig(
    level  = logging.INFO,
    handlers = (_stream_handler,),
)
logging.addLevelName(VERBOSE,  "VERBOSE")
logging.addLevelName(VERBOSE2, "VERBOSE2")
logging.addLevelName(VERBOSE3, "VERBOSE3")
logging.addLevelName(DEBUG2,   "DEBUG2")
logging.addLevelName(DEBUG3,   "DEBUG3")
logging.setLoggerClass(_CustomLogger)

class LogConfig(Configurable):
    @staticmethod
    def _setDebugCL(level):
        logging.getLogger(__package__.split('.')[0]).setLevel(level)
        logging.debug(f"Command-Line: Log Level: {level}")
        return level

    @classmethod
    def create_config(cls, parser):
        parser.add_argument('--log-level',
                action  = 'store',
                type    = cls._setDebugCL,
                choices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO','VERBOSE', 'VERBOSE2', 'VERBOSE3','DEBUG','DEBUG2','DEBUG3'],
                default = 'INFO',
                help    = 'Set Log Message Level')

_logconfig = LogConfig()
