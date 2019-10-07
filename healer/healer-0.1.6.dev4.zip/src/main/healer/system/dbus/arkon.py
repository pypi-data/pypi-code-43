"""
Base types for dbus operations
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from types import FunctionType
from typing import Any
from typing import List
from typing import Mapping

import dbus
import dbus.mainloop.glib
from dbus.proxies import ProxyObject
from gi.repository import GObject

from healer.device.arkon import ManagerBase
from healer.support.typing import cached_method
from healer.support.typing import override
from healer.system.dbus.const import FaceDBUS
from healer.system.dbus.const import SignalDBUS
from healer.system.dbus.support import SupportDBUS

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EventDBUS:
    """
    Base for dbus events
    :entry_path: underlying device/adapter path on the bus
    """
    entry_path:str


class ObserverDBUS(threading.Thread):
    """
    Map python thread to dbus main loop to emit dbus signal events
    """

    main_loop:GObject.MainLoop

    def __init__(self):
        super().__init__()
        self.setDaemon(True)
        self.main_loop = GObject.MainLoop()

    @override
    def run(self) -> None:
        self.main_loop.run()

    @override
    def start(self) -> None:
        super().start()

    def stop(self) -> None:
        self.main_loop.quit()


class ManagerDBUS(ManagerBase):
    """
    DBUS manager base
    """

    # dbus event reactor
    observer:ObserverDBUS = None

    # underlying system bus
    sys_bus:dbus.SystemBus = None

    # sub-bus on system bus that is managed here
    bus_name:str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sys_bus = SupportDBUS.obtain_system_bus()
        self.observer = ObserverDBUS()

    def has_bus_name(self) -> bool:
        "verify if managed bus is available"
        "i.e.: bus_name='org.bluez' is not availble when 'bluetooth.service' is stopped"
        return SupportDBUS.has_system_bus_name(self.bus_name)

    def proxy_object(self, object_path:str) -> ProxyObject:
        "obtain dbus proxy object by full object path"
        "i.e.: bus_name='org.bluez' object_path='/org/bluez'"
        return self.sys_bus.get_object(bus_name=self.bus_name, object_path=object_path)

    @override
    @cached_method
    def observer_start(self) -> None:
        self.observer.start()

    @override
    @cached_method
    def observer_stop(self) -> None:
        self.observer.stop()


class ObjectManagerDBUS(ManagerDBUS):
    """
    DBUS manager base with "object manager" interface and signals
    """

    object_manager_path:str = None

    @cached_method
    def observer_start(self) -> None:
        "attach default event listeners"
        self.sys_bus.add_signal_receiver(self.react_name_added,
            signal_name=SignalDBUS.NameAcquired,
        )
        self.sys_bus.add_signal_receiver(self.react_faces_added,
            bus_name=self.bus_name,
            dbus_interface=FaceDBUS.MANAGER,
            signal_name=SignalDBUS.InterfacesAdded,
        )
        self.sys_bus.add_signal_receiver(self.react_faces_removed,
            bus_name=self.bus_name,
            dbus_interface=FaceDBUS.MANAGER,
            signal_name=SignalDBUS.InterfacesRemoved,
        )
        super().observer_start()

    @cached_method
    def observer_stop(self) -> None:
        "detach default event listeners"
        self.sys_bus.remove_signal_receiver(self.react_faces_removed)
        self.sys_bus.remove_signal_receiver(self.react_faces_added)
        self.sys_bus.remove_signal_receiver(self.react_name_removed)
        super().observer_stop()

    def react_name_added(self, bus_name:str) -> None:
        logger.debug(f"bus_name={bus_name}")

    def react_name_removed(self, bus_name:str) -> None:
        logger.debug(f"bus_name={bus_name}")

    def react_faces_added(self, entry_path:str, face_dict:dbus.Dictionary) -> None:
        logger.debug(f"entry_path={entry_path} face_dict={face_dict}")

    def react_faces_removed(self, entry_path:str, face_list:dbus.Array) -> None:
        logger.debug(f"entry_path={entry_path} face_list={face_list}")

    def object_manager(self) -> dbus.Interface:
        root_obj = self.proxy_object(self.object_manager_path)
        return dbus.Interface(root_obj, FaceDBUS.MANAGER)

    def managed_objects(self) -> Mapping[str, Any]:
        "report registered object descriptors"
        return self.object_manager().GetManagedObjects()

    def reactor_register(self, entry_path:str, reactor:FunctionType) -> None:
        "attach filtered property change event listener"
        self.sys_bus.add_signal_receiver(reactor,
            bus_name=self.bus_name,
            dbus_interface=FaceDBUS.PROPERTIES,
            signal_name=SignalDBUS.PropertiesChanged,
            path=entry_path,
            path_keyword="entry_path",  # keep name
        )

    def reactor_unregister(self, entry_path:str, reactor:FunctionType) -> None:
        "detach filtered property change event listener"
        self.sys_bus.remove_signal_receiver(reactor,
            bus_name=self.bus_name,
            dbus_interface=FaceDBUS.PROPERTIES,
            signal_name=SignalDBUS.PropertiesChanged,
            path=entry_path,
        )
