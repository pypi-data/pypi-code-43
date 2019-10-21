# Service_Application_IF.py
#
# Copyright 2017 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# for python 3
# for Service Application

"""Service_Application_IF
"""

import xmlrpc.client
import logging
import logging.handlers

from . import RoIS_Service


class Service_Application_IF(RoIS_Service.Service_Application_Base):
    """Service_Application_IF
    """
    def __init__(self, uri, logger=None):
        self._uri = uri
        self._proxy = xmlrpc.client.ServerProxy(self._uri,verbose=False)
        if logger is not None:
            self.logger = logger
        while True:
            self.poll_event()

    def poll_event(self):
        """poll_event
        """
        try:
            msg = self._proxy.poll_event()
        except:
            print('xmlrpc error')
        (params, methodname) = xmlrpc.client.loads(msg)
        if methodname == 'completed':
            self.completed(params[0], params[1])
        elif methodname == 'notify_error':
            self.notify_error(params[0], params[1])
        elif methodname == 'notify_event':
            self.notify_event(params[0], params[1], params[2], params[3])

    def completed(self, command_id, status):
        self.logger.debug('received completed event'
                          + command_id
                          + RoIS_Service.Completed_Status(status).name)

    def notify_error(self, error_id, error_type):
        self.logger.debug('received error event'
                          + error_id
                          + RoIS_Service.ErrorType(error_type).name)

    def notify_event(self, event_id, event_type, subscribe_id, expire):
        self.logger.debug('received event'
                          + event_id
                          + event_type
                          + subscribe_id
                          + expire)


def example_sa_IF(url, q):
    try:
        logger = logging.getLogger('Service_Application_IF')
        logger.setLevel(logging.DEBUG)
        ch = logging.handlers.QueueHandler(q)
        # ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        a = Service_Application_IF(url, logger=logger)
    except KeyboardInterrupt:
        print("Interrupted")


if __name__ == '__main__':
    pass
