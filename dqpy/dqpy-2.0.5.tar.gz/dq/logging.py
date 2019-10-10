import os

PRODUCTION = os.getenv('DQENV', 'local') == 'production'


def error(logger, message, payload=None):
    """Log an error message.

    :param logger logger: The logger to use.
    :param string message: The error message.
    :param dict payload: The payload to attach to the log.
    """
    _log(logger.error, message, payload, exc_info=True)


def warning(logger, message, payload=None):
    """Log a warning message.

    :param logger logger: The logger to use.
    :param string message: The warning message.
    :param dict payload: The payload to attach to the log.
    """
    _log(logger.warning, message, payload)


def info(logger, message, payload=None):
    """Log an info message.

    :param logger logger: The logger to use.
    :param string message: The info message.
    :param dict payload: The payload to attach to the log.
    """
    _log(logger.info, message, payload)


def debug(logger, message, payload=None):
    """Log a debug message. This does nothing in production enviornment.

    :param logger logger: The logger to use.
    :param string message: The debug message.
    :param dict payload: The payload to attach to the log.
    """
    if PRODUCTION:
        return
    _log(logger.debug, message, payload)


def _log(logger, message, payload, exc_info=False):
    """Log a message.

    This does two things:

    1. The payload (if present) is converted to a string and appended to the
       log message. Format string is used so that Sentry can group messages
       together correctly.
    2. The payload is attached again as a data dict. This doesn't show up in
       terminal/file, but Sentry uses it for searching.

    :param func logger: The logger with level to use (e.g. logger.error).
    :param string message: The log message.
    :param dict payload: The payload to attach to the log.
    :param boolean exc_info: Whether to log the stack trace if the log is for
        an exception.
    """
    if payload:
        message = message + '\n%s'
        pstr = _format(payload)
        logger(message, pstr, extra={'data': payload}, exc_info=exc_info)
    else:
        logger(message, exc_info=exc_info)


def _format(payload):
    """Format the payload (variables) as a string.

    When logging to the terminal or a file, only the string message is logged.
    This converts the payload into a string, which can then be appended to the
    log message itself.

    :param dict payload: The variable payload.
    :returns string: The formatted payload message.
    """
    message = ''
    for key in payload.keys():
        message += '\n`{}`: {}'.format(key, payload[key])
    return message
