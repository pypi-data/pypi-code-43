"""
Base type for udev
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

import pyudev

from healer.device.arkon import ManagerBase
from healer.support.typing import cached_method
from healer.support.typing import override
from healer.support.typing import unused

logger = logging.getLogger(__name__)


@dataclass
class EventFilter():
    """
    Udev event selector
    """
    subsystem:str = None  # exact string match
    device_type:str = None  # exact string match


@dataclass(init=False)
class ManagerUDEV(ManagerBase):
    """
    Base type for udev device monitor
    """

    context:pyudev.Context
    monitor:pyudev.Monitor
    observer:pyudev.MonitorObserver

    def __init__(self, event_filter_list:List[EventFilter]=[], **kwargs):
        super().__init__(**kwargs)
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.observer = pyudev.MonitorObserver(self.monitor, self.react_event)
        for event_filter in event_filter_list:
            self.monitor.filter_by(event_filter.subsystem, event_filter.device_type)

    @override
    @cached_method
    def observer_start(self) -> None:
        self.observer.start()

    @override
    @cached_method
    def observer_stop(self) -> None:
        self.observer.stop()

    def react_event(self, action:str, pyudev_device:pyudev.Device) -> None:
        "react to hot-plug udev envents"
        unused(action)
        event_props = dict(pyudev_device.properties.items())
        logger.debug(f"udev event: {event_props}")
