"""
Device driver for
kernel module: dummy_hcd
"""

from __future__ import annotations

from dataclasses import dataclass

from healer.device.record import DeviceRecord
from healer.device.usb.arkon import DeviceUSB
from healer.support.typing import override


@dataclass(frozen=True)
class RecordDummyHCD(DeviceRecord):
    """
    """

    device_codec_guid = 201


@dataclass
class DeviceDummyHCD(DeviceUSB):
    """
    """

    config_entry = 'device/usb/dummy_hcd'

    @override
    def device_description(self) -> str:
        return "Device driver for kernel module: dummy_hcd"
