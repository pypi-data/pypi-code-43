# RoIS_Common.py
#
# Copyright 2017 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# For python3
# For HRI Component
"""
RoIS_Common
"""
import abc
import enum

class Component_Status(enum.Enum):
    """Component_Status
    """
    UNINITIALIZED = 0
    READY = 1
    BUSY = 2
    WARNING = 3
    ERROR = 4

class Command:
    """Command
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def start(self):
        """
        start () -> status: RoIS_HRI.ReturnCode_t
        """
        pass
    @abc.abstractmethod
    def stop(self):
        """
        stop () -> status: RoIS_HRI.ReturnCode_t
        """
        pass
    @abc.abstractmethod
    def suspend(self):
        """
        suspend () -> status: RoIS_HRI.ReturnCode_t
        """
        pass
    @abc.abstractmethod
    def resume(self):
        """
        resume () -> status: RoIS_HRI.ReturnCode_t
        """
        pass

class Query:
    """Quary
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def component_status(self):
        """
        component_status () -> (status: RoIS_HRI.ReturnCode_t, status: Component_Status)
        """
        pass

class Event:
    """Event
    """
    pass
