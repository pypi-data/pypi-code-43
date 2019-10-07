"""
Base type for bluetooth profile
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/test-hfp
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/test-profile
"""

from __future__ import annotations

import abc

import dbus
import dbus.types

from healer.system.dbus.arkon import SupportDBUS
from healer.system.dbus.bt.const import FaceBT

from .base import BluetoothService
from .event import ProfileAnyEventBT
from .event import ProfileConnectEventBT
from .event import ProfileContextBT
from .event import ProfileDisconnectEventBT


class WithProfileReactor(abc.ABC):
    """
    Trait: react to bluez profile connect/disconnect events
    """

    @abc.abstractmethod
    def react_profile_event(self, event:ProfileAnyEventBT) -> None:
        "react to bluez profile connect/disconnect events"


class BluetoothProfile(BluetoothService):
    """
    Bluetooth profile: dbus connection profile service provider
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt
    propagate profile connect/disconnect events to the event reactor
    """

    service_context:ProfileContextBT
    service_reactor:WithProfileReactor

    def __init__(self,
            service_context:ProfileContextBT,
            service_reactor:WithProfileReactor,
        ):
        super().__init__(service_context)
        self.service_reactor = service_reactor

    @dbus.service.method(FaceBT.PROFILE, in_signature='oha{sv}', out_signature='')
    def NewConnection(self,
            entry_path:dbus.String, file_desc:dbus.types.UnixFd, properties:dbus.Dictionary
        ) -> None:
        event = ProfileConnectEventBT(
            service_context=self.service_context,
            entry_path=str(entry_path),
            file_desc=file_desc.take(),  # assume care of the fd
            property_dict=SupportDBUS.dbus_to_python(properties),
        )
        self.service_reactor.react_profile_event(event)

    @dbus.service.method(FaceBT.PROFILE, in_signature='o', out_signature='')
    def RequestDisconnection(self,
            entry_path:dbus.String
        ) -> None:
        event = ProfileDisconnectEventBT(
            service_context=self.service_context,
            entry_path=str(entry_path),
        )
        self.service_reactor.react_profile_event(event)

    @dbus.service.method(FaceBT.PROFILE, in_signature='', out_signature='')
    def Release(self) -> None:
        "not used"
