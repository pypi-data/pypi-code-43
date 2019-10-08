"""Various ready-to-use logging formatters"""

import datetime
import logging


class DetailedFlatFormatter(logging.Formatter):
    """A concrete formatter with lots of details

    If provides the timestamp, level name, PID, class.function and
    file _AT_ line, separated by a tabulation.

    The message is shown on the next line, every line of the message is
    prefixed by a tablulation.
    """

    def __init__(self):
        """Constructor

        It inherits of logging.Formatter, but is called without argument:
        the arguments of the Formatter are defined in the implementation
        """
        logging.Formatter.__init__(self, self.fmt, None)

    @property
    def fmt(self):
        """The format of the event

        See the class' documentation.
        """
        return '\t'.join([
            '%(asctime)s',
            '%(levelname)s',
            '%(process)s',
            '%s.%s' % ('%(name)s', '%(funcName)s'),
            '%s@%s' % ('%(pathname)s', '%(lineno)d')
        ]) + '%(message)s'

    def formatTime(self, record, datefmt=None):
        """Format the date and time, going up to the microsecond"""
        if datefmt is not None:
            raise TypeError("Cannot provide datefmt: hardcoded")
        dt = datetime.datetime.fromtimestamp(record.created)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")

    def formatMessage(self, record):
        """Formats the event

        It calls logging.Formatter.formatMessage after having transformed the
        record's message by prefixing it by a new line and indenting the result
        with a tabulation (see the class' documentation).
        """
        sep = '\n\t'
        record.message = sep + sep.join(record.message.split('\n'))
        return logging.Formatter.formatMessage(self, record)
