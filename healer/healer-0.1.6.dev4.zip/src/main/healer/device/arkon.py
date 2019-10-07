"""
Base type for any device
"""

from __future__ import annotations

import abc
import logging
import os
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Type

from healer.config import CONFIG
from healer.resource.provider import resource_provider_path
from healer.support.typing import proper_class_name
from healer.wrapper.sudo import SUDO
from healer.wrapper.udevadm import UDEVADM

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IdentityBase():
    """
    Any device group identity parameters
    """


@dataclass
class DeviceBase(abc.ABC):
    """
    Base type for any hardware device driver
    :config_entry: configuration entry for the device
    """

    config_entry = 'device/any/any'  # must override

    device_run:bool = field(init=False, default=False, repr=False)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        "register available derived devices"
        super().__init_subclass__(**kwargs)
        DeviceSupport.register_device_class(cls)

    @classmethod
    def timeout(cls) -> int:  # milliseconds
        "generic read/write device operation timeout"
        seconds = float(CONFIG[cls.config_entry]['timeout'])
        milliseconds = int(1000 * seconds)
        return milliseconds

    @classmethod
    def udev_file(cls) -> str:
        "optional device udev rules file"
        return CONFIG[cls.config_entry]['udev_file']

    @classmethod
    def identity_token(cls) -> str:
        "device token, a string used for classification"
        return CONFIG[cls.config_entry]['identity_token']

    @classmethod
    def identity_bucket(cls) -> IdentityBase:
        "device group classification component"
        return IdentityBase()

    @abc.abstractmethod
    def device_identity(self) -> str:
        "individual identity of the device instance"

    @abc.abstractmethod
    def device_description(self) -> str:
        "human readable description of the device class"

    def has_run(self) -> bool:
        "device start/stop state"
        return self.device_run


class ManagerBase(abc.ABC):
    """
    Base type for any device manager
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abc.abstractmethod
    def observer_start(self) -> None:
        "initiate observer thread"

    @abc.abstractmethod
    def observer_stop(self) -> None:
        "terminate observer thread"


class DeviceSupport:
    """
    Utility functions
    """

    "track derived device types"
    device_class_list:List[Type[DeviceBase]] = list()

    @staticmethod
    def register_device_class(device_class:Type[DeviceBase]) -> None:
        assert not device_class in DeviceSupport.device_class_list, f"need unique: {device_class}"
        logger.debug(proper_class_name(device_class))
        DeviceSupport.device_class_list.append(device_class)

    @staticmethod
    def find_class_type(identity_bucket:IdentityBase) -> Type[DeviceBase]:
        for class_type in DeviceSupport.device_class_list:
            if identity_bucket == class_type.identity_bucket():
                return class_type
        return None

    @staticmethod
    def ensure_udev_rules() -> None:
        "provision /etc/udev.d rule files for the discoverd devices"
        logger.info(f"ensure udev rules")
        apply_count = 0
        for class_type in DeviceSupport.device_class_list:
            apply_done = DeviceSupport.ensure_udev_device_rules(class_type)
            if apply_done:
                apply_count += 1
        if apply_count > 0:
            logger.info(f"apply udev rules")
            UDEVADM.rules_reload()
            UDEVADM.events_trigger()

    @staticmethod
    def ensure_udev_device_rules(class_type:Type[DeviceBase]) -> bool:
        type_name = class_type.__name__
        udev_file = class_type.udev_file()
        if udev_file:
            if os.path.isfile(udev_file):
                logger.debug(f"present: {type_name}: {udev_file}")
                return False
            else:
                logger.debug(f"missing: {type_name}: {udev_file}")
                source = resource_provider_path(udev_file)
                target = udev_file
                SUDO.files_copy(source, target)
                logger.info(f"created: {type_name}: {udev_file}")
                return True
        else:
            logger.debug(f"no udev_file for: {type_name}")
            return False

    @staticmethod
    def peform_pyusb_setup():
        "apply pyusb library settings; must be called before any 'import usb'"

        enable_tracing = CONFIG.getboolean('pyusb/config', 'enable_tracing')
        enable_logging = CONFIG.getboolean('pyusb/config', 'enable_logging')

        logger.debug(f"enable_tracing={enable_tracing} enable_logging={enable_logging}")

        if os.environ.get('PYUSB_DEBUG'):
            del os.environ['PYUSB_DEBUG']

        # trigger usb package logger setup
        import usb

        if enable_tracing:
            usb._debug.enable_tracing(True)

        if enable_logging:
            logger_usb = logging.getLogger('usb')
            logger_usb.setLevel('DEBUG')


# perform by default
DeviceSupport.peform_pyusb_setup()
