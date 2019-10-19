# todo: change to fanout, create consumer that formats
from ..queues.logq import Logq
from pythonjsonlogger import jsonlogger
import logging


def json():
    """ formatter called by logging.yaml. format the log record columns in json format
    not needed if logging configured in .py file
    """
    return jsonlogger.JsonFormatter(reserved_attrs=[])


class RabbitHandler(logging.Handler):
    """ logging handler that outputs to rabbit queue
    """
    def __init__(self):
        # note fails if use super()
        logging.Handler.__init__(self)
        self.q = Logq(heartbeat=0)

    def emit(self, record):
        """ log the record """
        msg = self.format(record)
        self.q.put(msg)