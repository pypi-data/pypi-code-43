# RoIS_HRI.py
#
# Copyright 2017 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# for python 3

"""RoIS_HRI
"""
import abc
import enum

class ReturnCode_t(enum.Enum):
    """ReturnCode_t
    """
    OK = 1
    ERROR = 2
    BAD_PARAMETER = 3
    UNSUPPORTED = 4
    OUT_OF_RESOURCES = 5
    TIMEOUT = 6

class SystemIF:
    """
    class SystemIF(object)
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def connect(self):
        """
        connect() -> ReturnCode_t: status
        """
        pass
    @abc.abstractmethod
    def disconnect(self):
        """
        disconnect() -> ReturnCode_t: status
        """
        pass
    @abc.abstractmethod
    def get_profile(self, condition):
        """
        get_profile(condition) -> (status, profile)
        """
        pass
    @abc.abstractmethod
    def get_error_detail(self, error_id, condition):
        """
        get_error_detail(error_id,condition) -> (status,results)
        """
        pass

class CommandIF:
    """
    class CommandIF(object):
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def search(self, condition):
        """
        search(condition) -> (status, component_ref_list)
        """
        pass
    @abc.abstractmethod
    def bind(self, component_ref):
        """
        bind(component_ref) -> status
        """
        pass
    @abc.abstractmethod
    def bind_any(self, condition):
        """
        bind_any(condition) -> (status,component_ref_list)
        """
        pass
    @abc.abstractmethod
    def release(self, component_ref):
        """
        release(component_ref) -> status
        """
        pass
    @abc.abstractmethod
    def get_parameter(self, component_ref):
        """
        get_parameter(self,component_ref) -> (status,parameter_list)
        """
        pass
    @abc.abstractmethod
    def set_parameter(self, component_ref, parameters):
        """
        set_parameter(self, component_ref, parameters) -> (status,command_id)
        """
        pass
    @abc.abstractmethod
    def execute(self, command_unit_list):
        """
        execute(command_unit_list) -> status
        """
        pass
    @abc.abstractmethod
    def get_command_result(self, command_id, condition):
        """
        get_command_result(self, command_id, condition) -> (status,results)
        """
        pass

class QueryIF:
    """
    class QueryIF(object):
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def query(self, query_type, condition):
        """
        query(self, query_type, condition) -> (status,results)
        """
        pass

class EventIF:
    """
    class EventIF(object):
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def subscribe(self, event_type, condition):
        """
        subscribe(self, event_type, condition) -> (status,subscribe_id)
        """
        pass
    @abc.abstractmethod
    def unsubscribe(self, subscribe_id):
        """
        unsubscribe(self,subscribe_id) -> status
        """
        pass
    @abc.abstractmethod
    def get_event_detail(self, event_id, condition):
        """
        get_event_detail(self,event_id,condition) -> (status,results)
        """
        pass
