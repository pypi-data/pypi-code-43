"""
Bluetooth response exceptions
"""

from __future__ import annotations

import dbus
import dbus.exceptions


class BluetoothResponseError:
    """
    """


class BluetoothCanceledError(
        BluetoothResponseError,
        dbus.exceptions.DBusException,
        ):
    """
    """
    _dbus_error_name = "org.bluez.Error.Canceled"


class BluetoothRejectedError(
        BluetoothResponseError,
        dbus.exceptions.DBusException,
        ):
    """
    """
    _dbus_error_name = "org.bluez.Error.Rejected"
