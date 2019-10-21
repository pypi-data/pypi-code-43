# Service_Application_Base_example.py
#
# Copyright 2017 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# for python 3
# for HRI Engine

"""Service_Application_Base_example
"""

import sys
import queue
import time
import threading

from . import RoIS_Service

import socketserver
import xmlrpc.server

class ThreadingXMLRPCServer(socketserver.ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    """ThreadingXMLRPCServer
    """
    pass

class Service_Application_Base(RoIS_Service.Service_Application_Base):
    """Service_Application_Base
    """
    def __init__(self):
        self.event_queue = queue.Queue()

    def poll_event(self):
        """poll_event
        """
        msg = self.event_queue.get()
        return msg

    def completed(self, command_id, status):
        msg = xmlrpc.client.dumps((command_id, status), 'completed')
        self.event_queue.put(msg)

    def notify_error(self, error_id, error_type):
        msg = xmlrpc.client.dumps((error_id, error_type), 'notify_error')
        self.event_queue.put(msg)

    def notify_event(self, event_id, event_type, subscribe_id, expire):
        msg = xmlrpc.client.dumps(
            (event_id, event_type, subscribe_id, expire), 'notify_event')
        self.event_queue.put(msg)


def event_dispatch(sa):
    """event_dispatch
    """
    sa.completed("0", RoIS_Service.Completed_Status.OK.value)
    time.sleep(0.1)
    sa.notify_error("1", RoIS_Service.ErrorType.ENGINE_INTERNAL_ERROR.value)
    time.sleep(0.1)
    sa.notify_event("2", "sensor", "0", "2100-01-01T00:00:01+09:00")


# def event_dispatch_long(sa):
#     sa.completed("0", RoIS_Service.Completed_Status.OK.value)
#     time.sleep(1)
#     sa.notify_error("0", RoIS_Service.ErrorType.ENGINE_INTERNAL_ERROR.value)
#     time.sleep(60)
#     sa.notify_event("0", "sensor", "0", "2100-01-01T00:00:01+09:00")

def example_sa(port):
    """example_sa
    """
    sa = Service_Application_Base()

    # start the timer to dispatch events
    t = threading.Timer(0.1, event_dispatch, args=(sa,))
    t.start()

    # start the XML-RPC server
    server = ThreadingXMLRPCServer(("0.0.0.0", port), logRequests=False)
    server.register_instance(sa)
    server.register_introspection_functions()
    server.register_multicall_functions()
    # print("server running")
    server.serve_forever()


if __name__ == '__main__':
    example_sa(8000)
