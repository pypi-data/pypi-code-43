# HRI_Engine_client.py
#
# Copyright 2017 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# For python 3
# For Service Application

"""HRI_Engine_client
"""
import xmlrpc.client

from . import RoIS_HRI


class SystemIF(RoIS_HRI.SystemIF):
    """SystemIF
    """
    def __init__(self, proxy_obj):
        self._proxy = proxy_obj

    def connect(self):
        status = RoIS_HRI.ReturnCode_t(self._proxy.connect())
        return status

    def disconnect(self):
        status = RoIS_HRI.ReturnCode_t(self._proxy.disconnect())
        return status

    def get_profile(self, condition):
        (s, profile) = self._proxy.get_profile(condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, profile)

    def get_error_detail(self, error_id, condition):
        (s, results) = self._proxy.get_error_detail(error_id, condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, results)


class CommandIF(RoIS_HRI.CommandIF):
    """CommandIF
    """
    def __init__(self, proxy_obj):
        self._proxy = proxy_obj

    def search(self, condition):
        (s, component_ref_list) = self._proxy.search(condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, component_ref_list)

    def bind(self, component_ref):
        status = RoIS_HRI.ReturnCode_t(self._proxy.bind(component_ref))
        return status

    def bind_any(self, condition):
        (s, component_ref_list) = self._proxy.search(condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, component_ref_list)

    def release(self, component_ref):
        status = RoIS_HRI.ReturnCode_t(self._proxy.release(component_ref))
        return status

    def get_parameter(self, component_ref):
        (s, parameter_list) = self._proxy.get_parameter(component_ref)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, parameter_list)

    def set_parameter(self, component_ref, parameters):
        (s, command_id) = self._proxy.set_parameter(component_ref, parameters)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, command_id)

    def execute(self, command_unit_list):
        s = self._proxy.execute(command_unit_list)
        status = RoIS_HRI.ReturnCode_t(s)
        return status

    def get_command_result(self, command_id, condition):
        (s, results) = self._proxy.get_command_result(command_id, condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, results)


class QueryIF(RoIS_HRI.QueryIF):
    """QueryIF
    """
    def __init__(self, proxy_obj):
        self._proxy = proxy_obj

    def query(self, query_type, condition):
        (s, results) = self._proxy.query(query_type, condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, results)


class EventIF(RoIS_HRI.EventIF):
    """EventIF
    """
    def __init__(self, proxy_obj):
        self._proxy = proxy_obj

    def subscribe(self, event_type, condition):
        (s, subscribe_id) = self._proxy.subscribe(event_type, condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, subscribe_id)

    def unsubscribe(self, subscribe_id):
        s = self._proxy.unsubscribe(subscribe_id)
        status = RoIS_HRI.ReturnCode_t(s)
        return status

    def get_event_detail(self, event_id, condition):
        (s, results) = self._proxy.get_event_detail(event_id, condition)
        status = RoIS_HRI.ReturnCode_t(s)
        return (status, results)


class IF(SystemIF, CommandIF, QueryIF, EventIF):
    """IF
    """
    def __init__(self, uri):
        self._uri = uri
        self._proxy = xmlrpc.client.ServerProxy(self._uri)

if __name__ == "__main__":
    pass
