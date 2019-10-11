import os
import logging
import logging.config
from six import StringIO

from . import get_tool_dir

_LOGGING_OUTPUT_DIR = os.path.join(get_tool_dir(), 'log')
_LOGGING_CONFIG_TEMPLATE = """\
[loggers]
keys=root

[handlers]
keys=console,logfile

[formatters]
keys=fmt

[logger_root]
level=NOTSET
handlers=console,logfile

[handler_console]
class=StreamHandler
level=INFO
args=(sys.stderr,)

[handler_logfile]
class=FileHandler
args=(r'%(logfile)s','a+')
level=%(level)s
formatter = fmt

[formatter_fmt]
format=%%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s
datefmt=%%Y-%%m-%%d %%H:%%M:%%S
"""


def _init_logging(log_name, output_dir=_LOGGING_OUTPUT_DIR, level='DEBUG'):
    """ Initializes logging. """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logfile = os.path.join(output_dir, log_name)
    conf = _LOGGING_CONFIG_TEMPLATE % {"logfile": logfile, "level": level}
    log = StringIO(conf)
    logging.config.fileConfig(log, None, False)

    return logfile


def init_bootstrap_log():
    return _init_logging('bootstrap.log')
