"""
Base type for dbus bluetooth object/service
"""

from __future__ import annotations

from typing import Any

import dbus
import dbus.service
from dbus.proxies import ProxyObject

from healer.system.dbus.arkon import SupportDBUS
from healer.system.dbus.const import FaceDBUS

from .const import FaceBT
from .event import AnyServiceContextBT


class BluetoothObject:
    """
    Bluetooth wrapper for proxy object with "entry interface" and "properties interface"

    https://dbus.freedesktop.org/doc/dbus-python/tutorial.html#proxy-objects
    """

    object_face:str = None  # class constant

    proxy_object:ProxyObject
    object_entry:dbus.Interface
    object_props:dbus.Interface

    def __init__(self, proxy_object:ProxyObject):
        super().__init__()
        self.proxy_object = proxy_object
        self.object_entry = dbus.Interface(proxy_object, self.object_face)
        self.object_props = dbus.Interface(proxy_object, FaceDBUS.PROPERTIES)

    def prop_get(self, key) -> Any:
        return self.object_props.Get(self.object_face, key)

    def prop_set(self, key, value) -> None:
        self.object_props.Set(self.object_face, key, value)


class BluetoothService(dbus.service.Object):
    """
    Bluetooth service base

    https://dbus.freedesktop.org/doc/dbus-python/tutorial.html#exporting-objects
    """

    service_context:AnyServiceContextBT

    def __init__(self, service_context:AnyServiceContextBT):
        "aquire bus resources after service register"
        self.service_context = service_context
        sys_bus = SupportDBUS.obtain_system_bus()
        bus_name = FaceBT.ROOT
        service_path = self.service_context.service_path
        dbus.service.Object.__init__(self,
            conn=sys_bus,
            object_path=service_path,
            bus_name=bus_name,
        )

    def terminate(self) -> None:
        "release bus resources after service unregister"
        sys_bus = SupportDBUS.obtain_system_bus()
        service_path = self.service_context.service_path
        self.remove_from_connection(
            connection=sys_bus,
            path=service_path,
        )
