"""
Top level dbus interfaces
"""

from __future__ import annotations

import enum

from healer.support.typing import AutoNameEnum


class FaceDBUS:
    """
    Top level dbus interface names
    """
    ROOT = "org.freedesktop.DBus"
    MANAGER = ROOT + ".ObjectManager"
    PROPERTIES = ROOT + ".Properties"
    INTROSPECTABLE = ROOT + ".Introspectable"


@enum.unique
class SignalDBUS(AutoNameEnum):
    """
    Top level dbus signal names
    """

    InterfacesAdded = enum.auto()  # org.freedesktop.DBUS.ObjectManager
    InterfacesRemoved = enum.auto()  # org.freedesktop.DBUS.ObjectManager

    PropertiesChanged = enum.auto()  # org.freedesktop.DBUS.Properties

    NameAcquired = enum.auto()  # org.freedesktop.DBus
    NameLost = enum.auto()  # org.freedesktop.DBus
