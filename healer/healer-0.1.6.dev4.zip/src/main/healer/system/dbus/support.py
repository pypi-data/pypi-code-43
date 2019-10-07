from __future__ import annotations

import functools
from typing import Any

import dbus
import dbus.mainloop.glib


class SupportDBUS:
    """
    Utility functions
    """

    @staticmethod
    def python_to_dbus(data:Any) -> Any:
        if isinstance(data, str):
            data = dbus.String(data)
        elif isinstance(data, bool):
            data = dbus.Boolean(data)
        elif isinstance(data, int):
            data = dbus.Int64(data)
        elif isinstance(data, float):
            data = dbus.Double(data)
        elif isinstance(data, list):
            data = dbus.Array([SupportDBUS.python_to_dbus(item) for item in data], signature='v')
        elif isinstance(data, dict):
            data = dbus.Dictionary(data, signature='sv')
            for key in data.keys():
                data[key] = SupportDBUS.python_to_dbus(data[key])
        return data

    @staticmethod
    def dbus_to_python(data:Any) -> Any:
        if isinstance(data, dbus.String):
            data = str(data)
        elif isinstance(data, dbus.Boolean):
            data = bool(data)
        elif isinstance(data, (
                dbus.Int16, dbus.Int32, dbus.Int64,
                dbus.UInt16, dbus.UInt32, dbus.UInt64,
            )):
            data = int(data)
        elif isinstance(data, dbus.Double):
            data = float(data)
        elif isinstance(data, dbus.Array):
            data = [SupportDBUS.dbus_to_python(item) for item in data]
        elif isinstance(data, dbus.Dictionary):
            new_data = dict()
            for key in data.keys():
                new_data[str(key)] = SupportDBUS.dbus_to_python(data[key])
            data = new_data
        elif isinstance(data, dbus.ObjectPath):
            data = str(data)
        return data

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def obtain_system_bus() -> dbus.SystemBus:
        nativeloop = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        system_bus = dbus.SystemBus(mainloop=nativeloop)
        return system_bus

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def obtain_sesion_bus() -> dbus.SessionBus:
        nativeloop = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus(mainloop=nativeloop)
        return session_bus

    @staticmethod
    def has_system_bus_name(bus_name:str) -> bool:
        "find if system bus contains named bus"
        for raw_name in SupportDBUS.obtain_system_bus().list_names():
            bus_text = str(raw_name)  # from dbus.String
            if bus_name == bus_text:
                return True
        return False
