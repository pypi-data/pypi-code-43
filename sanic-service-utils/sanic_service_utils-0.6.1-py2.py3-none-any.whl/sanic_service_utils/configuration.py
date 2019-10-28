import contextvars
import sys
import time
import typing
import uuid

import dynaconf
import sanic
import sanic.worker
import sanic.server
import sanic.websocket
import structlog
import structlog.threadlocal

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.6.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    'build_logging_configuration', 'settings',
    'build_structlog_config'
]

LOG_TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


settings = dynaconf.LazySettings(  # pylint: disable=invalid-name
    ENVVAR_PREFIX_FOR_DYNACONF='SANIC',
    ROOT_PATH_FOR_DYNACONF="settings/",
    SILENT_ERRORS_FOR_DYNACONF=False,
    ENV_FOR_DYNACONF='default'
)


def wrap_dict(dict_class):
    Wrapped = type(
        "WrappedDict-" + str(uuid.uuid4()), (_ContextVarWrapper,), {}
    )
    Wrapped._tl = contextvars.ContextVar('t1')  # pylint: disable=protected-access
    Wrapped._dict_class = dict_class  # pylint: disable=protected-access
    return Wrapped


class _ContextVarWrapper(structlog.threadlocal._ThreadLocalDictWrapper):  # pylint: disable=protected-access,too-few-public-methods

    @property
    def _dict(self):
        """
        Return or create and return the current context.
        """
        try:
            return self.__class__._tl.get()  # pylint: disable=protected-access
        except LookupError:
            self.__class__._tl.set(self.__class__._dict_class())  # pylint: disable=protected-access
            return self.__class__._tl.get()  # pylint: disable=protected-access


def _fetch_data_from_extra(_1, _2, event_dict):
    reserved_attrs = (
        'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName', 'levelno', 'lineno',
        'module', 'server_time', 'msecs', 'message', 'msg', 'pathname', 'process', 'processName'
        'relativeCreated', 'stack_info', 'thread', 'threadName', 'request'
    )
    event_dict.update({
        k: v for k, v in event_dict['_record'].__dict__.items()
        if k not in reserved_attrs
    })
    return event_dict


def _add_logger_config(config: typing.Dict, package: str, log_level: str):
    if package in config['loggers']:
        config['loggers'][package]['level'] = log_level
    else:
        config['loggers'][package] = {
            "level": log_level,
            "handlers": [settings.get('BASE_HANDLER', 'console')],
            "propagate": True,
        }


def build_logging_configuration(app_name: str):
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _fetch_data_from_extra,
        structlog.processors.format_exc_info
    ]

    base_dict = dict(
        version=1,
        disable_existing_loggers=False,
        loggers={},
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console_structlog",
                "stream": sys.stdout,
            },
            'json_console': {
                "class": "logging.StreamHandler",
                "formatter": "structlog",
                "stream": sys.stdout,
            },
            'json_log': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'structlog',
                'when': 'D',
                'backupCount': 1,
                'filename': settings.get('LOGFILE_PATH', './sanic.log')
            }
        },
        formatters={
            "generic": {
                "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                "datefmt": f"[{settings.get('TIMESTAMP_FORMAT', LOG_TIMESTAMP_FORMAT)}]",
                "class": "logging.Formatter",
            },
            "access": {
                "format": "%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: %(request)s %(message)s %(status)d %(byte)d",
                "datefmt": f"[{settings.get('TIMESTAMP_FORMAT', LOG_TIMESTAMP_FORMAT)}]",
                "class": "logging.Formatter",
            },
            "structlog": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": pre_chain,
            },
            'console_structlog': {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
                "foreign_pre_chain": pre_chain,
            }
        },
    )

    for package in ['sanic.root', 'sanic.access', 'sanic.error', 'sanic_service_utils', app_name]:
        _add_logger_config(base_dict, package, 'INFO')

    for package, log_level in settings.get('LOG_LEVELS', {}).items():
        _add_logger_config(base_dict, package, log_level)

    return base_dict


def build_structlog_config(use_contextvar_dict=True):
    return dict(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=wrap_dict(dict) if use_contextvar_dict else dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class BetterHttpProtocol(sanic.server.HttpProtocol):

    def log_response(self, response):
        """
        Helper method provided to enable the logging of responses in case if
        the :attr:`HttpProtocol.access_log` is enabled.

        :param response: Response generated for the current request

        :type response: :class:`sanic.response.HTTPResponse` or
            :class:`sanic.response.StreamingHTTPResponse`

        :return: None
        """
        if self.access_log:
            extra = {"status": getattr(response, "status", 0)}

            if isinstance(response, sanic.response.HTTPResponse):
                extra["response_lenght"] = len(response.body)
            else:
                extra["response_lenght"] = -1

            extra["remote_address"] = "-"
            current_time = time.time()
            if self.request is not None:
                if self.request.ip:
                    extra["remote_address"] = self.request.ip

                extra["request_method"] = self.request.method
                extra['path'] = self.request.path
                extra['query'] = self.request.query_string
                extra['protocol'] = self.request.scheme
                extra['user_agent'] = self.request.headers.get('user-agent')
                extra['request_time'] = current_time - self.request.get('__START_TIME__', current_time)
            else:
                extra["request_method"] = '-'
                extra['url'] = '-'
                extra['path'] = '-'
                extra['query'] = '-'
                extra['protocol'] = '-'
                extra['user_agent'] = '-'
                extra['request_time'] = '-'

            sanic.log.access_logger.info("", extra=extra)


class BetterWebsocketProtocol(BetterHttpProtocol, sanic.websocket.WebSocketProtocol):

    pass


class BetterGunicornWorker(sanic.worker.GunicornWorker):

    websocket_protocol = BetterWebsocketProtocol
    http_protocol = BetterHttpProtocol
