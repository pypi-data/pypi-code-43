"""
Device driver loader
"""

from __future__ import annotations

from healer.device.arkon import DeviceSupport

from .actor import bayer_contour_next_usb
from .actor import dummy_actor
from .actor import easyhome_cf350bt
from .actor import innovo_cms50f
from .actor import ionhealth_ih02
from .actor import ketonix_usb

DeviceSupport.ensure_udev_rules()
