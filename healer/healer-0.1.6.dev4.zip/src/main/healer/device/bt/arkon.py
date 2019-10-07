"""
Base type for bluetooth device
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from dataclasses import field
from types import FunctionType
from typing import Any
from typing import List
from typing import Mapping
from typing import Type

import dbus

from healer.config import CONFIG
from healer.device.arkon import DeviceBase
from healer.device.arkon import DeviceSupport
from healer.device.arkon import IdentityBase
from healer.support.typing import override
from healer.system.dbus.bt.adapter import BluetoothAdapter
from healer.system.dbus.bt.const import GuidBT
from healer.system.dbus.bt.const import ProfileOptionBT
from healer.system.dbus.bt.device import BluetoothDevice
from healer.system.dbus.bt.error import BluetoothRejectedError
from healer.system.dbus.bt.event import AgentAnyEventBT
from healer.system.dbus.bt.event import AgentAuthorizeEntryEventBT
from healer.system.dbus.bt.event import AgentContextBT
from healer.system.dbus.bt.event import AgentPasswordRequestEventBT
from healer.system.dbus.bt.event import ProfileAnyEventBT
from healer.system.dbus.bt.event import ProfileContextBT
from healer.system.dbus.bt.event import PropertyChangeEventBT
from healer.system.dbus.bt.manager import BluetoothManager
from healer.system.dbus.support import SupportDBUS

logger = logging.getLogger(__name__)


@dataclass
class ReactorBT:
    """
    Forwarder of bluetooth device events to the device actor
    """

    actor_ref:ProperRef = field()

    def react_change(self,
            entry_face:str,
            changed:dbus.Dictionary,
            invalidated:dbus.Array,
            entry_path:str
        ) -> None:
        event = PropertyChangeEventBT(
            entry_face=str(entry_face),
            entry_path=str(entry_path),
            changed_dict=SupportDBUS.dbus_to_python(changed),
            invalid_list=SupportDBUS.dbus_to_python(invalidated),
        )
        logger.debug(f"event: {event}")
        self.actor_ref.tell(event)

    def react_profile(self, event:ProfileAnyEventBT) -> None:
        self.actor_ref.tell(event)


@dataclass(frozen=True)
class IdentityBT(IdentityBase):
    """
    BlueTooth device group identity
    OUI: Organizational Unique Identifier, the first 24 bits of a MAC address
    """

    vendor:str

    @staticmethod
    def from_token(identity_token:str) -> IdentityBT:
        "from OUI string AA:BB:CC"
        vendor = identity_token
        return IdentityBT(vendor)

    @staticmethod
    def from_address(address:str) -> IdentityBT:
        "from MAC string AA:BB:CC:DD:EE:FF"
        assert len(address) == 17
        vendor = address[0:8]  # AA:BB:CC
        return IdentityBT(vendor)

    @staticmethod
    def from_pydbus(pydbus_device:BluetoothDevice) -> IdentityBT:
        return IdentityBT.from_address(pydbus_device.address)


@dataclass
class AdapterBT():
    "base type for bluetooth adapter driver"

    # underlying dbus proxy object
    pydbus_adapter:BluetoothAdapter = field(repr=False)


@dataclass
class DeviceBT(DeviceBase):
    "base type for bluetooth device driver"

    # device configuation section
    config_entry:str = field(init=False, default='device/bt/any')

    # underlying dbus proxy object
    pydbus_device:BluetoothDevice = field(repr=False)

    @classmethod
    def identity_bucket(cls) -> IdentityBT:
        "device group identity"
        return IdentityBT.from_token(cls.identity_token())

    @classmethod
    def bluetooth_passcode(cls) -> str:
        "access is defined by device group identity"
        return CONFIG[cls.config_entry]['bluetooth_passcode']

    def issue_pair(self) -> bool:  # TODO
        return self.pydbus_device.do_pair()

    def issue_connect(self) -> bool:
        return self.pydbus_device.do_connect()

    def issue_disconnect(self) -> bool:
        return self.pydbus_device.do_disconnect()

    def device_address(self) -> str:
        return self.pydbus_device.address

    @override
    def device_identity(self) -> str:
        "individual identity of the device instance"
        device_host = ""  # TODO
        device_address = self.device_address()
        return f"device/bt/{device_address}"

    @override
    def device_description(self) -> str:
        "human readable description of the device class"
        return self.__class__.__name__


class SupportBT:
    """
    Utility functiions
    """

    @staticmethod
    def find_class_type(pydbus_device:BluetoothDevice) -> Type[DeviceBT]:
        "resolve bt wrapper device type from underlying bt dbus device"
        identity = IdentityBT.from_pydbus(pydbus_device)
        return DeviceSupport.find_class_type(identity)

    # auto login bluetooth agent descriptor
    master_agent = AgentContextBT(
        request_default=True,
    )

    # serial link bluetooth profile descriptor
    serial_profile = ProfileContextBT(
        service_uuid=GuidBT.SerialPort,
        option_dict={
            ProfileOptionBT.AutoConnect : True,
        }
    )


class ManagerBT(BluetoothManager):
    """
    Bluetooth orchestration system:
    * ensure single bt adapter
    * maintain bt agent/profile services
    * activate/deactivate bt device actors
    """

    adapter_path:str  # selected adapter identity or none
    adapter_map:Mapping[str, AdapterBT]  # track all adapters
    device_map:Mapping[str, DeviceBT]  # track supported devices
    reactor_registry:Mapping[str, ReactorBT]  # store event forwarders

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device_map = dict()
        self.adapter_map = dict()
        self.adapter_path = None
        self.reactor_registry = dict()

    def service_register(self):
        "configure services for bus_name='org.bluez' upon bus activation"
        self.agent_register(SupportBT.master_agent)
        self.profile_register(SupportBT.serial_profile)

    def service_unregister(self):
        "unconfigure services for bus_name='org.bluez' upon bus deactivation"
        self.agent_unregister(SupportBT.master_agent)
        self.profile_unregister(SupportBT.serial_profile)

    def adapter_start(self, entry_path:str) -> None:
        adapter = self.managed_adapter(entry_path)
        adapter.powered = True
        adapter.do_start_discovery()

    def adapter_stop(self, entry_path:str) -> None:
        adapter = self.managed_adapter(entry_path)
        adapter.do_stop_discovery()
        adapter.powered = False

    def device_remove(self, entry_path:str) -> None:
        device = self.managed_device(entry_path)
        adapter = self.managed_adapter(device.adapter)
        adapter.do_remove_device(entry_path)

    def managed_adapter(self, entry_path:str) -> BluetoothAdapter:
        return BluetoothAdapter(self.proxy_object(entry_path))

    def managed_device(self, entry_path:str) -> BluetoothDevice:
        return BluetoothDevice(self.proxy_object(entry_path))

    @override
    def react_adapter_added(self, entry_path:str) -> None:
        super().react_adapter_added(entry_path)
        pydbus_adapter = self.managed_adapter(entry_path)
        adapter = AdapterBT(pydbus_adapter)
        self.adapter_map[entry_path] = adapter
        self.ensure_single_adapter()

    @override
    def react_adapter_removed(self, entry_path:str) -> None:
        super().react_adapter_removed(entry_path)
        self.adapter_map.pop(entry_path, None)
        self.ensure_single_adapter()

    def ensure_single_adapter(self) -> None:
        "adapter lifecycle: select single active adapter"
        has_path = self.adapter_path is not None
        has_in_map = self.adapter_path in self.adapter_map
        has_any_map = len(self.adapter_map) > 0
        if has_path and not has_in_map:  # active adapter removed
            logger.debug(f"adapter disable: {self.adapter_path}")
            self.adapter_path = None
            self.service_unregister()
            self.ensure_single_adapter()  # select again, if possible
            return
        if not has_path and has_any_map:  # provide active adapter
            self.adapter_path = list(self.adapter_map.keys())[0]  # first found
            logger.debug(f"adapter enable:  {self.adapter_path}")
            self.adapter_start(self.adapter_path)
            self.service_register()
            return

    def ensure_device_paired(self, pydbus_device:BluetoothDevice) -> None:
        if not pydbus_device.paired:

            def ensure_paired():
                pydbus_device.do_pair()
                while not pydbus_device.paired:
                    time.sleep(1)
                pydbus_device.blocked = False
                pydbus_device.trusted = True

            self.with_agent_scope(SupportBT.master_agent, ensure_paired)

    @override
    def react_device_added(self, entry_path:str) -> None:
        super().react_device_added(entry_path)
        pydbus_device = self.managed_device(entry_path)
        if self.adapter_path == pydbus_device.adapter:
            device_class = SupportBT.find_class_type(pydbus_device)
            if device_class:
                pydbus_device.trusted = True
                pydbus_device.blocked = False
                device = device_class(pydbus_device)
                self.device_map[entry_path] = device
                self.device_register(entry_path, device)

    @override
    def react_device_removed(self, entry_path:str) -> None:
        super().react_device_removed(entry_path)
        if entry_path in self.device_map:
            device = self.device_map.pop(entry_path, None)
            self.device_unregister(entry_path, device)

    def device_register(self, entry_path:str, device:DeviceBT) -> None:
        "produce device actor for the bt device"
        from healer.device.actor.arkon import DeviceActorSupport
        logger.info(f"device: {device}")
        actor_ref = DeviceActorSupport.produce_actor(device)
        reactor = ReactorBT(actor_ref)
        self.reactor_registry[entry_path] = reactor
        self.reactor_register(entry_path, reactor.react_change)

    def device_unregister(self, entry_path:str, device:DeviceBT) -> None:
        "release device actor for the bt device"
        from healer.device.actor.arkon import DeviceActorSupport
        logger.info(f"device: {device}")
        reactor = self.reactor_registry.pop(entry_path, None)
        self.reactor_unregister(entry_path, reactor.react_change)
        DeviceActorSupport.terminate_actor(device)

    @override
    def react_agent_event(self, event:AgentAnyEventBT) -> str:
        "user agent reactor: provide device pairing: pincode or passkey"
        super().react_agent_event(event)
        device = self.device_map.get(event.entry_path, None)
        if not device:
            logger.warning(f"wrong device: {event}")
            raise BluetoothRejectedError()  # exception means deny access
        if isinstance(event, AgentAuthorizeEntryEventBT):
            logger.info(f"device allow: {device}")
            return ""  # no exception means grant access
        if isinstance(event, AgentPasswordRequestEventBT):
            logger.info(f"device login: {device}")
            return device.bluetooth_passcode()  # pass code is checked by device

    @override
    def react_profile_event(self, event:ProfileAnyEventBT) -> None:
        "device profile reactor: process connect/disconnect events"
        super().react_profile_event(event)
        entry_path = event.entry_path
        reactor = self.reactor_registry[entry_path]
        reactor.react_profile(event)  # propagate event to device actor
