import logging.config
import structlog

from spacemakerlog3.utils import merge_two_dicts

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    },
    'handlers': {
        'json': {
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'loggers': {
        '': {
            'handlers': ['json'],
            'level': logging.INFO
        }
    }
})


def _dict_to_log(d):
    """
    Recursively create log in key=value pairs (text format)
    output for nested dictionaries.
    """
    arr = []
    for k, v in d.items():
        val = v
        if isinstance(v, dict):
            val = '[{}]'.format(_dict_to_log(v))
        arr.append('{}={}'.format(k, val))
    return ' '.join(arr)


def _add_exc_info(logger, method_name, event_dict):
    if 'exception' in event_dict:
        event_dict['exc_info'] = True
    return event_dict


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        _add_exc_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.render_to_log_kwargs,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

_log = structlog.getLogger()

_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
}

_global_kwargs = {}


def set_format(fmt):
    """
    Set the log format

    :param string fmt: "json" or "text"
    """
    # NB: Only "json" is supported


def set_level(lvl):
    """
    Set the log level

    :param string lvl: "debug", "info", "warn" or "error"
    """
    _log.setLevel(_levels[lvl])


def set_level_external(lvl):
    """
    Set the log level for "external" loggers

    :params string lvl: "debug", "info", "warn" or "error"
    """
    for logger_name in logging.getLogger().manager.loggerDict.keys():
        logging.getLogger(logger_name).setLevel(_levels[lvl])

def set_global_args(**kwargs):
    for key, value in kwargs.items():
        if value is None:
            del _global_kwargs[key]
        else:
            _global_kwargs[key] = value

def debug(msg, *args, **kwargs):
    """
    Log a message with level 'debug'
    """

    kwargs_with_global = merge_kwargs_with_global_kwargs(kwargs)

    try:
        _log.debug(msg, *args, **kwargs_with_global)
    except Exception as e:
        _log.debug(msg, log_error=e)


def info(msg, *args, **kwargs):
    """
    Log a message with level 'info'
    """

    kwargs_with_global = merge_kwargs_with_global_kwargs(kwargs)

    try:
        _log.info(msg, *args, **kwargs_with_global)
    except Exception as e:
        _log.info(msg, log_error=e)


def warn(msg, *args, **kwargs):
    """
    Log a message with level 'warn'
    """

    kwargs_with_global = merge_kwargs_with_global_kwargs(kwargs)

    try:
        _log.warn(msg, *args, **kwargs_with_global)
    except Exception as e:
        _log.warn(msg, log_error=e)


def error(msg, *args, **kwargs):
    """
    Log a message with level 'error'
    """

    kwargs_with_global = merge_kwargs_with_global_kwargs(kwargs)

    try:
        _log.error(msg, *args, **kwargs_with_global)
    except Exception as e:
        _log.error(msg, log_error=e)


def merge_kwargs_with_global_kwargs(kwargs):
    if len(_global_kwargs) > 0:
        kwargs_with_global = merge_two_dicts(_global_kwargs, kwargs)
    else:
        kwargs_with_global = kwargs
    return kwargs_with_global
