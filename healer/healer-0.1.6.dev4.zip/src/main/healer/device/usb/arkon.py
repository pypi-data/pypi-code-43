"""
Base type for USB device
"""

from __future__ import annotations

import enum
import logging
import threading
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Type

import pyudev
import usb.core

from healer.device.arkon import DeviceBase
from healer.device.arkon import DeviceSupport
from healer.device.arkon import IdentityBase
from healer.support.typing import override
from healer.system.udev.arkon import EventFilter
from healer.system.udev.arkon import ManagerUDEV

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddrBusDev():
    """
    USB usbbus/device address
    """

    bus_num:int
    dev_num:int

    @staticmethod
    def from_pyudev(pyudev_device:pyudev.Device) -> AddrBusDev:
        "resolve bus/num from udev device descriptor"
        bus_num = int(pyudev_device.properties['BUSNUM'])  # hardcoded pyudev
        dev_num = int(pyudev_device.properties['DEVNUM'])  # hardcoded pyudev
        return AddrBusDev(bus_num, dev_num)

    @staticmethod
    def from_pyusb(pyusb_device:usb.core.Device) -> AddrBusDev:
        "resolve bus/num from usb device proxy object"
        bus_num = int(pyusb_device.bus)
        dev_num = int(pyusb_device.address)
        return AddrBusDev(bus_num, dev_num)


@dataclass(frozen=True)
class IdentityUSB(IdentityBase):
    """
    USB device vendor/product group identity
    :vendor: vendor id as hex string, without the 0x prefix
    :product: product id as hex string, without the 0x prefix
    """

    vendor:str
    product:str

    def idVendor(self) -> int:
        return int(self.vendor, 16)

    def idProduct(self) -> int:
        return int(self.product, 16)

    @staticmethod
    def from_pyudev(pyudev_device:pyudev.Device) -> IdentityUSB:
        vendor = pyudev_device.properties['ID_VENDOR_ID']  # hardcoded pyudev
        product = pyudev_device.properties['ID_MODEL_ID']  # hardcoded pyudev
        return IdentityUSB(vendor, product)

    @staticmethod
    def from_pyusb(pyusb_device:usb.core.Device) -> IdentityUSB:
        vendor = SupportUSB.format_hex4(pyusb_device.idVendor)
        product = SupportUSB.format_hex4(pyusb_device.idProduct)
        return IdentityUSB(vendor, product)

    @staticmethod
    def from_token(identity_token:str) -> IdentityUSB:
        term_list = identity_token.lower().split('/')  # healer convention
        vendor = term_list[0]
        product = term_list[1]
        return IdentityUSB(vendor, product)


@dataclass
class DeviceUSB(DeviceBase):
    """
    Base type for USB device driver
    """

    config_entry:str = field(init=False, default='device/usb/any')

    # underlying pyusb device
    pyusb_device:usb.core.Device = field()

    device_lock:threading.Lock = field(default_factory=threading.RLock, repr=False)

    @classmethod
    def identity_bucket(cls) -> IdentityUSB:
        return IdentityUSB.from_token(cls.identity_token())

    def __enter__(self) -> None:
        logger.debug(f"with:enter")
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type:
            logger.error(f"with:exit: {exc_type} {exc_val} {exc_tb}")
            return False  # enable error propagation
        else:
            logger.debug(f"with:exit")
            self.stop()
            return True  # disable error propagation

    def start(self) -> None:
        self.perform_detach()
        self.perform_reset()
        self.device_run = True

    def stop(self) -> None:
        self.device_run = False
        try:
            self.perform_reset()
        except usb.core.USBError as error:
            logger.debug(f"error: {error}")
            if error.errno == 2:
                "[Errno 2] Entity not found"
                return
            if error.errno == 19:
                "[Errno 19] No such device (it may have been disconnected)"
                return
            raise error

    def select_face(self, face_num:enum.Enum) -> usb.core.Interface:
        config = self.pyusb_device.get_active_configuration()
        for face in config.interfaces():
            if face.bInterfaceNumber == face_num.value:
                return face
        raise RuntimeError(f"Missing face: {face_num}")

    def select_point(self, face:usb.core.Interface, point_addr:enum.Enum) -> usb.core.Endpoint:
        for point in face:
            if point.bEndpointAddress == point_addr.value:
                return point
        raise RuntimeError(f"Missing point: {point_addr}")

    def perform_attach(self) -> None:
        "restore kernel driver"
        for config in self.pyusb_device:
            for face in config:
                face_num = face.bInterfaceNumber
                if not self.pyusb_device.is_kernel_driver_active(face_num):
                    self.pyusb_device.attach_kernel_driver(face_num)

    def perform_detach(self) -> None:
        "release kernel driver"
        for conf in self.pyusb_device:
            for face in conf:
                face_num = face.bInterfaceNumber
                if self.pyusb_device.is_kernel_driver_active(face_num):
                    self.pyusb_device.detach_kernel_driver(face_num)

    def perform_reset(self):
        "ensure default configuration"
        self.pyusb_device.reset()
        self.pyusb_device.set_configuration()

    def device_address(self) -> AddrBusDev:
        return AddrBusDev.from_pyusb(self.pyusb_device)

    def device_string(self, config_index:int) -> str:
        return usb.util.get_string(self.pyusb_device, config_index)

    def device_serial_number(self) -> str:
        return self.device_string(self.pyusb_device.iSerialNumber)

    @override
    def device_identity(self) -> str:
        "device instance identity: default: vendor/product/serial"
        bucket = self.identity_bucket()
        vendor = bucket.vendor
        product = bucket.product
        serial_number = self.device_serial_number()
        return f"device/usb/{vendor}/{product}/{serial_number}"

    @override
    def device_description(self) -> str:
        "human readable description of the device class"
        return self.__class__.__name__


class SupportUSB:
    """
    Utility name space
    """

    logger = logging.getLogger(__name__)

    @staticmethod
    def format_hex4(value:int) -> str:
        return '{:04x}'.format(value)

    @staticmethod
    def event_filter_list() -> List[EventFilter]:
        "select udev root device events"
        return [
            EventFilter('usb', 'usb_device'),
        ]

    @staticmethod
    def find_pyusb_device(device_address:AddrBusDev) -> usb.core.Device:
        "resolve pyusb device from usb bus device address"
        return usb.core.find(bus=device_address.bus_num, address=device_address.dev_num)

    @staticmethod
    def find_class_type(pyusb_device:usb.core.Device) -> Type[DeviceUSB]:
        "resolve usb wrapper device type from backend pyusb device"
        identity = IdentityUSB.from_pyusb(pyusb_device)
        return DeviceSupport.find_class_type(identity)


@dataclass(init=False)
class ManagerUSB(ManagerUDEV):
    """
    USB orchestration system
    """

    device_list:List[DeviceUSB]

    def __init__(self, **kwargs):
        super().__init__(
            event_filter_list=SupportUSB.event_filter_list(),
            **kwargs,
        )
        self.device_list = []

    @override
    def react_event(self, action:str, pyudev_device:pyudev.Device) -> None:
        "react to hot-plug udev envents"
        super().react_event(action, pyudev_device)
        if action in ('bind', 'unbind'):
            device_address = AddrBusDev.from_pyudev(pyudev_device)
            device = self.find_device(device_address)
            if action == 'bind':
                if device:
                    logger.warning(f"duplicate bind for: {pyudev_device}")
                    return
                pyusb_device = SupportUSB.find_pyusb_device(device_address)
                if not pyusb_device:
                    logger.warning(f"missing pyusb_device: {pyudev_device}")
                    return
                class_type = SupportUSB.find_class_type(pyusb_device)
                if class_type:
                    device = class_type(pyusb_device)
                    self.device_register(device)
                else:
                    logger.debug(f"ignore foreing device: {pyudev_device}")
            elif action == 'unbind':
                if device:
                    self.device_unregister(device)
                else:
                    logger.debug(f"ignore foreing device: {pyudev_device}")

    def find_device(self, device_address:AddrBusDev) -> DeviceUSB:
        for device in self.device_list:
            if device.device_address() == device_address:
                return device
        return None

    def device_register(self, device:DeviceUSB) -> None:
        from healer.device.actor.arkon import DeviceActorSupport
        if not device in self.device_list:
            logger.info(f"device: {device}")
            self.device_list.append(device)
            DeviceActorSupport.produce_actor(device)

    def device_unregister(self, device:DeviceUSB) -> None:
        from healer.device.actor.arkon import DeviceActorSupport
        if device in self.device_list:
            logger.info(f"device: {device}")
            self.device_list.remove(device)
            DeviceActorSupport.terminate_actor(device)
