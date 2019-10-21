import logging
from logging.config import dictConfig

DATEFMT = '%Y-%m-%d %H:%M:%S'
FORMAT = "%(asctime)s %(levelname)-8s:%(name)s:%(message)s"
FORMAT_NO_TIME = "%(levelname)-8s:%(name)s:%(message)s"


COLORS = {
    'DEBUG': '\033[1m\033[34m', # bold + blue
    'INFO': '\033[1m', # bold
    'WARNING': '\033[1m\033[33m', # yellow + bold
    'WARN': '\033[1m\033[33m', # yellow + bold
    'ERROR': '\033[31m',  # red
    'EXCEPTION': '\033[31m',  # red
    'CRITICAL': '\033[4m\033[1m\033[31m' ,  # red + underline + bold
    'FATAL': '\033[4m\033[1m\033[31m' ,  # red + underline + bold
    'RESET': "\033[0m" # reset colors
}


def configure_logging(console=True, level='DEBUG', modules=None, other_modules_level='WARNING', filepath=None,
                      max_bytes=10485760, backup_count=5, console_format=None, file_format=None,
                      console_datefmt=None, file_datefmt=None, console_print_time=False,
                      console_colored=True, console_level=None, file_level=None, file_mode='a', other_level_rules=None):
    handlers = {}
    formatters = {}
    loggers = {}
    # Console handler
    if console:
        console_handler = {'class': 'logging.StreamHandler', 'level': level, 'formatter': 'console_formatter'}
        if console_level is not None:
            console_handler['level'] = console_level
        handlers['console_handler'] = console_handler

        # console_formatter
        console_formatter = {}
        if console_colored:
            console_formatter['()'] =  ColoredFormatter
        if console_format is None:
            if console_print_time:
                console_formatter['format'] = FORMAT
            else:
                console_formatter['format'] = FORMAT_NO_TIME
        else:
            console_formatter['format'] = console_format
        console_formatter['datefmt'] = console_datefmt if console_datefmt is not None else DATEFMT
        formatters['console_formatter'] = console_formatter

    # File handler
    if filepath is not None:
        file_handler = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': level,
            'formatter': 'file_formatter',
            'filename': filepath,
            'mode': file_mode,
            'maxBytes': max_bytes,
            'backupCount': backup_count,
        }
        if file_level is not None:
            file_handler['level'] = file_level
        handlers['file_handler'] = file_handler

        # file formatter
        file_formatter = {}
        file_formatter['format'] = file_format if file_format is not None else FORMAT
        file_formatter['datefmt'] = file_datefmt if file_datefmt is not None else DATEFMT
        formatters['file_formatter'] = file_formatter

    # root logger
    loggers[''] = {'level':other_modules_level, 'handlers':handlers.keys()}

    # main logger
    loggers['__main__'] = {'level':level}

    # modules loggers
    if modules is None:
        modules = list()
    for m in modules:
        loggers[m] = {'level':level}

    # other modules rules:
    if other_level_rules is not None:
        for k,v in other_level_rules.items():
            loggers[k] = v

    # logging dict config
    config = {
        'version': 1,
        'handlers': handlers,
        'formatters': formatters,
        'loggers': loggers
    }

    dictConfig(config)


def _wrap_level_color(txt, level):
    return COLORS[level] + txt + COLORS['RESET']


class ColoredFormatter(logging.Formatter):
    def __init__(self, format=FORMAT, datefmt=DATEFMT):
        super(ColoredFormatter, self).__init__(format, datefmt=datefmt)

    def format(self, record):
        msg, levelname = record.msg, record.levelname
        if record.levelname in COLORS:
            record.msg = _wrap_level_color(msg, levelname)
            record.levelname = _wrap_level_color(levelname, levelname)
        s = logging.Formatter.format(self, record)
        record.msg, record.levelname = msg, levelname
        return s


def test_logging(loggername=''):
    logger = logging.getLogger(loggername)
    logger.debug('Jackdaws love my big sphinx of quartz.')
    logger.info('Jackdaws love my big sphinx of quartz.')
    logger.warning('Jackdaws love my big sphinx of quartz.')
    logger.error('Jackdaws love my big sphinx of quartz.')
    logger.critical('Jackdaws love my big sphinx of quartz.')
