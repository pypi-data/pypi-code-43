# HRI_Engine_example.py
#
# Copyright 2017 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# For python 3
# For HRI Engine

"""HRI_Engine_example
"""

from __future__ import print_function

import os
import sys

from . import RoIS_HRI

import socketserver
import xmlrpc.server

class ThreadingXMLRPCServer(socketserver.ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    """ThreadingXMLRPCServer
    """
    pass


class SystemIF(RoIS_HRI.SystemIF):
    """SystemIF
    """
    def __init__(self, Engine):
        self._engine = Engine

    def connect(self):
        # print("connect")
        if self._engine.state is False:
            self._engine.state = True
            status = RoIS_HRI.ReturnCode_t.OK.value
        else:
            status = RoIS_HRI.ReturnCode_t.ERROR.value
        # time.sleep(30)
        return status

    def disconnect(self):
        if self._engine.state is True:
            self._engine.state = False
            status = RoIS_HRI.ReturnCode_t.OK.value
        else:
            status = RoIS_HRI.ReturnCode_t.ERROR.value
        #status = RoIS_HRI.ReturnCode_t.OK.value
        return status

    def get_profile(self, condition):
        status = RoIS_HRI.ReturnCode_t.OK.value
        # RoIS_HRI_Profile
        profile = "Unsupported"
        return (status, profile)

    def get_error_detail(self, error_id, condition):
        status = RoIS_HRI.ReturnCode_t.OK.value
        # ResultLists
        results = "None"
        return (status, results)


class CommandIF(RoIS_HRI.CommandIF):
    """CommandIF
    """
    def __init__(self, Engine):
        self._engine = Engine

    def search(self, condition):
        status = RoIS_HRI.ReturnCode_t.OK.value
        # List< RoIS_Identifier>
        component_ref_list = ["None"]
        return (status, component_ref_list)

    def bind(self, component_ref):
        # print("state:", self._engine.state)
        status = RoIS_HRI.ReturnCode_t.OK.value
        return status

    def bind_any(self, condition):
        status = RoIS_HRI.ReturnCode_t.OK.value
        component_ref_list = ["None"]
        return (status, component_ref_list)

    def release(self, component_ref):
        status = RoIS_HRI.ReturnCode_t.OK.value
        return status

    def get_parameter(self, component_ref):
        status = RoIS_HRI.ReturnCode_t.OK.value
        parameter_list = ["None"]
        return (status, parameter_list)

    def set_parameter(self, component_ref, parameters):
        status = RoIS_HRI.ReturnCode_t.OK.value
        command_id = "0"
        return (status, command_id)

    def execute(self, command_unit_list):
        status = RoIS_HRI.ReturnCode_t.OK.value
        return status

    def get_command_result(self, command_id, condition):
        status = RoIS_HRI.ReturnCode_t.OK.value
        results = ["None"]
        return (status, results)


class QueryIF(RoIS_HRI.QueryIF):
    """
    class QueryIF(object):
    """

    def __init__(self, Engine):
        self._engine = Engine

    def query(self, query_type, condition):
        status = RoIS_HRI.ReturnCode_t.OK.value
        results = ["None"]
        return (status, results)


class EventIF(RoIS_HRI.EventIF):
    """
    class QueryIF(object):
    """

    def __init__(self, Engine):
        self._engine = Engine

    def subscribe(self, event_type, condition):
        """
        subscribe(self, event_type, condition) -> (status,subscribe_id)
        """
        status = RoIS_HRI.ReturnCode_t.OK.value
        subscribe_id = "0"
        return (status, subscribe_id)

    def unsubscribe(self, subscribe_id):
        """
        unsubscribe(self,subscribe_id) -> status
        """
        status = RoIS_HRI.ReturnCode_t.OK.value
        return status

    def get_event_detail(self, event_id, condition):
        """
        get_event_detail(self,event_id,condition) -> (status,results)
        """
        status = RoIS_HRI.ReturnCode_t.OK.value
        results = ["None"]
        return (status, results)


class IF(SystemIF, CommandIF, QueryIF, EventIF):
    """IF
    """
    pass


class IF_server:
    """IF_Server
    """
    def __init__(self, port):
        self._addr = os.getenv("HRIENGINE")
        self._server = ThreadingXMLRPCServer(
            ("0.0.0.0", port), logRequests=False)

    def run(self, _IF):
        """IF_Server
        """
        self._server.register_instance(_IF)
        self._server.register_introspection_functions()
        # print("server running")
        self._server.serve_forever()


class MyHRIE:
    """IF_Server
    """
    def __init__(self):
        self.state = False


def test_engine(port):
    """test_engine
    """
    IF_server(port).run(IF(MyHRIE()))


if __name__ == "__main__":
    pass
