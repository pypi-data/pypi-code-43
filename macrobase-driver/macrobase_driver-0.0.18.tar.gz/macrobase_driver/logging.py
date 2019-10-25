import rapidjson
import logging

from macrobase.config import AppConfig
from macrobase_driver.config import LogFormat

import structlog


class ExtraLogsRenderer(object):
    """
    Add application information with key `service`.
    """

    def __init__(self, config: AppConfig):
        self.version = config.VERSION

    def __call__(self, logger, name, event_dict):
        if isinstance(event_dict, dict):
            event_dict['service'] = {
                'version': self.version
            }

            return event_dict


def add_log_location_data(logger, method_name, event_dict):
    record = event_dict.get("_record")
    if record is not None:
        event_dict['filepath'] = record.pathname
        event_dict['module'] = record.module
        event_dict['function'] = record.funcName
        event_dict['lineno'] = record.lineno
    elif logger is not None:
        from structlog._frames import _find_first_app_frame_and_name

        frame, _ = _find_first_app_frame_and_name(['logging', __name__])
        event_dict['filepath'] = frame.f_code.co_filename
        event_dict['module'] = frame.f_globals['__name__']
        event_dict['function'] = frame.f_code.co_name
        event_dict['lineno'] = frame.f_lineno
    return event_dict


def add_request_data(logger, method_name, event_dict):
    record = event_dict.get("_record")

    if record is not None:
        byte = getattr(record, 'byte', None)
        host = getattr(record, 'host', None)
        status = getattr(record, 'status', None)
        request = getattr(record, 'request', None)

        if byte is not None:
            event_dict['byte'] = byte
        if host is not None:
            event_dict['host'] = host
        if status is not None:
            event_dict['status'] = status
        if request is not None:
            event_dict['request'] = request

        if not event_dict['event']:
            event_dict['event'] = f'({host}): {request} {status} {byte}'

    return event_dict


timestamper = structlog.processors.TimeStamper(fmt="iso")


# structlog.configure(
#     processors=[
#         structlog.stdlib.add_log_level,
#         structlog.stdlib.add_logger_name,
#         add_log_location_data,
#         add_request_data,
#         structlog.stdlib.PositionalArgumentsFormatter(),
#         timestamper,
#         structlog.processors.StackInfoRenderer(),
#         structlog.processors.format_exc_info,
#         structlog.stdlib.ProcessorFormatter.wrap_for_formatter
#     ],
#     context_class=dict,
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.stdlib.BoundLogger,
#     cache_logger_on_first_use=True,
# )


def get_logging_config(config: AppConfig) -> dict:
    logging_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_log_location_data,
        timestamper,
        ExtraLogsRenderer(config),
        structlog.processors.format_exc_info,
    ]
    all_processors = logging_processors + [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ]

    structlog.configure(
        processors=all_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    level = logging.getLevelName(config.LOG_LEVEL.raw.upper())
    if config.DEBUG:
        level = logging.DEBUG

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            LogFormat.plain: {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
                "foreign_pre_chain": logging_processors,
            },
            LogFormat.json: {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(serializer=rapidjson.dumps),
                "foreign_pre_chain": logging_processors,
            }
        },
        "handlers": {
            "default": {
                "level": level,
                "class": "logging.StreamHandler",
                "formatter": config.LOG_FORMAT,
            },
        },
        "loggers": {
            "": {
                "handlers": ["default", ],
                "level": level,
                "propagate": True,
            },
        }
    }