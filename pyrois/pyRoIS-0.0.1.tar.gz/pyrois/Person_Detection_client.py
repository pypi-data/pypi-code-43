# Person_Detection_Client.py
#
# Copyright 2018 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# For python3
# For HRI Engine

"""Person_Detection_Client
"""

import threading
# import logging
import xmlrpc.client

from pyrois import RoIS_Common, RoIS_HRI


class Command(RoIS_Common.Command):
    """Command
    """
    def __init__(self, uri):
        self._uri = uri
        self._proxy = xmlrpc.client.ServerProxy(self._uri)

    def start(self):
        status = RoIS_HRI.ReturnCode_t(self._proxy.start())
        return status

    def stop(self):
        status = RoIS_HRI.ReturnCode_t(self._proxy.stop())
        return status

    def suspend(self):
        status = RoIS_HRI.ReturnCode_t(self._proxy.suspend())
        return status

    def resume(self):
        status = RoIS_HRI.ReturnCode_t(self._proxy.resume())
        return status


class Query(RoIS_Common.Query):
    """Query
    """
    def __init__(self, uri):
        self._uri = uri
        self._proxy = xmlrpc.client.ServerProxy(self._uri)

    def component_status(self):
        (status, c_status) = self._proxy.component_status()
        return (RoIS_HRI.ReturnCode_t(status), RoIS_Common.Component_Status(c_status))


class Event(RoIS_Common.Event):
    """Event
    """
    def __init__(self, uri):
        self._uri = uri
        self._e_proxy = xmlrpc.client.ServerProxy(self._uri)

    def start_th(self):
        self.th = threading.Thread(target=self.event_loop,)
        self.th.daemon = True
        self.th.start()

    def event_loop(self):
        """event_loop
        """
        while self.allow_loop:
            try:
                self.poll_event()
            except ConnectionRefusedError:
                break

    def poll_event(self):
        """poll_event
        """
        msg = self._e_proxy.poll_event()
        (params, methodname) = xmlrpc.client.loads(msg)
        if methodname == 'person_detected':
            self.person_detected(params[0], params[1])

    def person_detected(self, timestamp, number):
        self.events.append((timestamp,number))
        # print("person_detected",timestamp,number)
        # self.logger.debug('received completed event'
        #                 + command_id
        #                 + RoIS_Service.Completed_Status(status).name)


class Person_Detection_Client(Command, Query, Event):
    """Person_Detection_Client
    """
    def __init__(self, uri):
        self._uri = uri
        self._proxy = xmlrpc.client.ServerProxy(self._uri)
        self._e_proxy = xmlrpc.client.ServerProxy(self._uri)
        self.events = []
        self.allow_loop = True
        self.start_th()

    def __del__(self):
        self.allow_loop = False
