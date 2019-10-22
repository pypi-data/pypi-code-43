import traceback
from datetime import datetime
from typing import Optional, List, Mapping
import logging
import json


class JSONFormatter(logging.Formatter):
    BUILTIN_ATTRS = {
        'args',
        'asctime',
        'created',
        'exc_info',
        'exc_text',
        'filename',
        'funcName',
        'levelname',
        'levelno',
        'lineno',
        'module',
        'msecs',
        'message',
        'msg',
        'name',
        'pathname',
        'process',
        'processName',
        'relativeCreated',
        'stack_info',
        'thread',
        'threadName',
    }

    def __init__(self, tags: Optional[List[str]] = None, extra: Optional[Mapping] = None):
        super(JSONFormatter, self).__init__()
        self._tags = tags if tags is not None else []
        self._extra = extra if extra is not None else {}

    def format(self, record: logging.LogRecord):
        message = {
            '@timestamp': self._format_timestamp(record.created),
            'message': record.getMessage(),
            'level': record.levelname,
            'pid': record.process,
            'context': record.name,
            'tags': self._tags,
        }

        message.update({'extra': self._get_extra_fields(record=record)})

        return json.dumps(message)

    @staticmethod
    def _format_timestamp(time_):
        timestamp = datetime.utcfromtimestamp(time_)
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (timestamp.microsecond / 1000) + "Z"

    def _get_extra_fields(self, record: logging.LogRecord):
        extra_fields = {
            'func_name': record.funcName,
            'line': record.lineno,
            'path': record.pathname,
            'process_name': record.processName,
            'thread_name': record.threadName,
        }

        if self._extra:
            extra_fields.update(self._extra)

        if record.exc_info:
            extra_fields['stack_trace'] = self._format_exception(record.exc_info)

        for attr in record.__dict__:
            if attr in self.BUILTIN_ATTRS:
                continue
            extra_fields[attr] = record.__dict__[attr]

        return extra_fields

    @staticmethod
    def _format_exception(exc_info):
        if isinstance(exc_info, tuple):
            stack_trace = ''.join(traceback.format_exception(*exc_info))
        elif exc_info:
            stack_trace = ''.join(traceback.format_stack())
        else:
            stack_trace = ''

        return stack_trace
