"""
Base types for dbus bluetooth adapters
"""

from __future__ import annotations

from typing import Any
from typing import List
from typing import Mapping

import dbus

from .base import BluetoothObject
from .const import AdapterFilterBT
from .const import AdapterPropertyBT
from .const import FaceBT


class BluetoothAdapter(BluetoothObject):
    """
    Bluetooth adapter: dbus proxy object wrapper

    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/adapter-api.txt
    """

    object_face:str = FaceBT.ADAPTER

    @property
    def discoverable(self) -> bool:
        return bool(self.prop_get(AdapterPropertyBT.Discoverable))

    @discoverable.setter
    def discoverable(self, value:bool) -> None:
        self.prop_set(AdapterPropertyBT.Discoverable, value)

    @property
    def pairable(self) -> bool:
        return bool(self.prop_get(AdapterPropertyBT.Pairable))

    @pairable.setter
    def pairable(self, value:bool) -> None:
        self.prop_set(AdapterPropertyBT.Pairable, value)

    @property
    def powered(self) -> bool:
        return bool(self.prop_get(AdapterPropertyBT.Powered))

    @powered.setter
    def powered(self, value:bool) -> None:
        self.prop_set(AdapterPropertyBT.Powered, value)

    @property
    def discovering(self) -> bool:
        return bool(self.prop_get(AdapterPropertyBT.Discovering))

    @property
    def address(self) -> str:
        return str(self.prop_get(AdapterPropertyBT.Address))

    @property
    def uuid_list(self) -> List[str]:
        return [str(uuid) for uuid in self.prop_get(AdapterPropertyBT.UUIDs) ]

    def do_remove_device(self, device_path:str) -> None:
        self.object_entry.RemoveDevice(device_path)

    def do_get_discovery_filters(self) -> List[str]:
        return [ str(entry) for entry in self.object_entry.GetDiscoveryFilters()]

    def do_set_discovery_filter(self, filter_dict:Mapping[str, Any]) -> None:
        filter_result = BluetoothAdapterSupport.convert_filter(filter_dict)
        self.object_entry.SetDiscoveryFilter(filter_result)

    def do_start_discovery(self):
        if not self.discovering:
            self.object_entry.StartDiscovery()

    def do_stop_discovery(self):
        if self.discovering:
            self.object_entry.StopDiscovery()


class BluetoothAdapterSupport:
    """
    """

    @staticmethod
    def convert_filter(self, filter_dict:Mapping[str, Any]) -> dbus.Dictionary:
        "map from python to dbus types"
        filter_result = dbus.Dictionary()
        for key, value in filter_dict:
            if key == AdapterFilterBT.RSSI:
                filter_result.update(key, dbus.Int16(int(value)))
            elif key == AdapterFilterBT.Pathloss:
                filter_result.update(key, dbus.UInt16(int(value)))
            elif key == AdapterFilterBT.Transport:
                filter_result.update(key, dbus.String(str(value)))
            elif key == AdapterFilterBT.UUIDs:
                assert isinstance(value, list)
                filter_result.update(key, dbus.Array(value))
            else:
                raise RuntimeError(f"Invalid filter key: {key}")
        return filter_result
