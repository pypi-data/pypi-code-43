import json
import logging
import traceback
from datetime import datetime


def json_serializer(log):
    """
    serialize log record
    :param log: log record
    :return: serialized log record
    """
    return json.dumps(log, ensure_ascii=False)


def sanitize_log_msg(record):
    """
    sanitize log message
    \n, \r, \t == replace ==> _
    :param record: log record
    :return: sanitized log message
    """
    return record.getMessage().replace('\n', '_').replace('\r', '_').replace('\t', '_')


class JSONLogFormatter(logging.Formatter):
    """
    custom json formatter
    """

    def get_exc_fields(self, record):
        """
        if an exception raised, this method formats the exception message and
        returns { formatted exception message and filename }
        :param record: log record
        :return: a dict => { formatted exception message, filename }
        """
        if record.exc_info:
            exc_info = self.format_exception(record.exc_info)
        else:
            exc_info = record.exc_text
        return {
            'exc_info': exc_info,
            'filename': record.filename,
        }

    @classmethod
    def format_exception(cls, exc_info):
        """
        format exception message
        :param exc_info: an exception that raised
        :return: formatted exception message
        """
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

    def format(self, record):
        """
        format log record to a json object
        :param record: log record
        :return: a json string that contains the log record
        """
        now = datetime.now()
        json_log_object = {
                           "date_time": str(now),
                           "level": record.levelname,
                           "message": sanitize_log_msg(record),
                           "line_number": record.lineno,
                           "module": record.module
                           }
        if hasattr(record, 'props'):
            json_log_object.update({'data': record.props})

        if record.exc_info or record.exc_text:
            json_log_object.update(self.get_exc_fields(record))

        return json_serializer(json_log_object)
