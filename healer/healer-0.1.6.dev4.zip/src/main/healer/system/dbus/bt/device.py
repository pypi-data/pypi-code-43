"""
Base types for dbus bluetooth devices
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt
"""

from __future__ import annotations

from typing import List

from .base import BluetoothObject
from .const import DevicePropertyBT
from .const import FaceBT


class BluetoothDevice(BluetoothObject):
    """
    Bluetooth device: dbus proxy object wrapper

    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt
    """

    object_face:str = FaceBT.DEVICE
    ignore_reply:bool = True

    @property
    def blocked(self) -> bool:
        return bool(self.prop_get(DevicePropertyBT.Blocked))

    @blocked.setter
    def blocked(self, value:bool) -> None:
        self.prop_set(DevicePropertyBT.Blocked, value)

    @property
    def trusted(self) -> bool:
        return bool(self.prop_get(DevicePropertyBT.Trusted))

    @trusted.setter
    def trusted(self, value:bool) -> None:
        self.prop_set(DevicePropertyBT.Trusted, value)

    @property
    def connected(self) -> bool:
        return bool(self.prop_get(DevicePropertyBT.Connected))

    @property
    def paired(self) -> bool:
        return bool(self.prop_get(DevicePropertyBT.Paired))

    @property
    def name(self) -> str:
        return str(self.prop_get(DevicePropertyBT.Name))

    @property
    def address(self) -> str:
        return str(self.prop_get(DevicePropertyBT.Address))

    @property
    def adapter(self) -> str:
        return str(self.prop_get(DevicePropertyBT.Adapter))

    @property
    def uuid_list(self) -> List[str]:
        return [str(uuid) for uuid in self.prop_get(DevicePropertyBT.UUIDs) ]

    @property
    def services_resolved(self) -> bool:
        return bool(self.prop_get(DevicePropertyBT.ServicesResolved))

    def do_connect(self, profile:str=None) -> bool:
        if not self.connected:
            if profile is None:
                self.object_entry.Connect(ignore_reply=self.ignore_reply)
            else:
                self.object_entry.ConnectProfile(profile, ignore_reply=self.ignore_reply)

    def do_disconnect(self) -> None:
        if self.connected:
            self.object_entry.Disconnect(ignore_reply=self.ignore_reply)

    def do_pair(self) -> None:
        if not self.paired:
            self.object_entry.Pair(ignore_reply=self.ignore_reply)

    def do_cancel_pairing(self) -> None:
        if self.paired:
            self.object_entry.CancelPairing(ignore_reply=self.ignore_reply)
