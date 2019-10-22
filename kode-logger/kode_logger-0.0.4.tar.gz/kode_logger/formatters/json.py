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

    def format(self, record: logging.LogRecord):
        extra = {
            attr: record.__dict__[attr]
            for attr in record.__dict__
            if attr not in self.BUILTIN_ATTRS
        }
        json_record = {
            'message': record.getMessage(),
            'context': record.name,
            'extra': extra,
        }

        return json.dumps(json_record)
