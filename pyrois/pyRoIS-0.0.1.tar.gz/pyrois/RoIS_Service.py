# RoIS_Service.py
#
# Copyright 2017 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# for python 3
# for Service Application

"""RoIS_Service
"""

import abc
import enum

class Completed_Status(enum.Enum):
    """Completed_Status
    """
    OK = 1
    ERROR = 2
    ABORT = 3
    OUT_OF_RESOURCES = 4
    TIMEOUT = 5

class ErrorType(enum.Enum):
    """ErrorType
    """
    ENGINE_INTERNAL_ERROR = 1
    COMPONENT_INTERNEL_ERROR = 2
    COMPONENT_NOT_RESPONDING = 3
    USER_DEFINE_ERROR = 4

class Service_Application_Base:
    """
    class ServiceApplicationBase(object)
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def completed(self, command_id, status):
        """
        connect(command_id, status) : void
        """
        pass
    @abc.abstractmethod
    def notify_error(self, error_id, error_type):
        """
        notify_error(error_id, error_type) : void
        """
        pass
    @abc.abstractmethod
    def notify_event(self, event_id, event_type, subscribe_id, expire):
        """
        notify_event(self, event_id, event_type, subscribe_id, expire) : void
        """
        pass
