# -*- coding: utf-8 -*-
"""Models for WLED."""

from typing import Optional, Tuple

import attr


@attr.s(auto_attribs=True)
class LedInfo:
    count: int = 0
    rgbw: bool = False
    # pin: Optional[bytearray]
    current: int = 0
    max_current: int = 0
    max_segment: int = 0


@attr.s(auto_attribs=True)
class DeviceInfo:

    free_heap: Optional[int]
    mac_address: Optional[str]
    udp_port: Optional[int]

    architecture: str = "Unknown"
    arduino_core_version: str = "Unknown"
    brand: str = "WLED"
    build_type: str = "Unknown"
    effect_count: int = 0
    live: bool = False
    name: str = "WLED Light"
    pallet_count: int = 0
    product: str = "DIY Light"
    uptime: int = 0
    version_id: str = ""
    version: str = "Unknown"

    @staticmethod
    def from_dict(data):
        return DeviceInfo(
            architecture=data.get("arch"),
            arduino_core_version=data.get("core").replace("_", "."),
            brand=data.get("brand"),
            build_type=data.get("btype"),
            effect_count=data.get("fxcount"),
            free_heap=data.get("freeheap"),
            live=data.get("live"),
            mac_address=data.get("mac"),
            name=data.get("name"),
            pallet_count=data.get("palcount"),
            product=data.get("product"),
            udp_port=data.get("udpport"),
            uptime=data.get("uptime"),
            version_id=data.get("vid"),
            version=data.get("ver"),
        )


@attr.s(auto_attribs=True)
class Effect:
    id: int
    name: str
    slug: str


@attr.s(auto_attribs=True)
class NightLight:
    duration: int
    fade: bool = True
    on: bool = False
    target_brightness: int = 1


@attr.s(auto_attribs=True)
class Segment:
    id: int = 0
    start: int = 0
    stop: int = 0
    length: int = 0
    color_primary: Tuple[int, int, int, int] = (0, 0, 0, 0)
    color_secondary: Tuple[int, int, int, int] = (0, 0, 0, 0)
    color_tertiary: Tuple[int, int, int, int] = (0, 0, 0, 0)
    effect: int = 0
    speed: int = 0
    intensity: int = 0
    pallete: int = 0


@attr.s(auto_attribs=True)
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    w: int = 0
