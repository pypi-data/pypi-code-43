"""
Bluetooth constants
"""

from __future__ import annotations

import enum

from healer.support.typing import AutoNameEnum


class PathBT:
    """
    Bluetooth bus known path entries
    """
    ROOT = "/"
    ORG_BLUES = "/org/bluez"


class FaceBT:
    """
    Bluetooth interface names
    """
    ROOT = "org.bluez"
    AGENT = ROOT + ".Agent1"
    ADAPTER = ROOT + ".Adapter1"
    DEVICE = ROOT + ".Device1"
    PROFILE = ROOT + ".Profile1"
    AGENT_MANAGER = ROOT + ".AgentManager1"
    PROFILE_MANAGER = ROOT + ".ProfileManager1"


class GuidBT:
    """
    Bluetooth UUID name space
    https://www.bluetooth.com/specifications/assigned-numbers/service-discovery/
    """
    BASE_UUID = "00000000-0000-1000-8000-00805f9b34fb"
    SerialPort = "00001101-0000-1000-8000-00805f9b34fb"


@enum.unique
class DevicePropertyBT(AutoNameEnum):
    """
    Bluetooth device property names
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt#n123
    """
    Name = enum.auto()
    Alias = enum.auto()
    RSSI = enum.auto()  # use for device detect
    TxPower = enum.auto()  # use for device detect
    UUIDs = enum.auto()
    Blocked = enum.auto()
    Connected = enum.auto()
    Paired = enum.auto()
    Trusted = enum.auto()
    ServicesResolved = enum.auto()
    Adapter = enum.auto()
    Address = enum.auto()
    AddressType = enum.auto()


@enum.unique
class AdapterPropertyBT(AutoNameEnum):
    """
    Bluetooth adapter property names
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/adapter-api.txt#n192
    """
    Name = enum.auto()
    UUIDs = enum.auto()
    Discovering = enum.auto()
    Discoverable = enum.auto()
    DiscoverableTimeout = enum.auto()
    Pairable = enum.auto()
    PairableTimeout = enum.auto()
    Powered = enum.auto()
    Address = enum.auto()
    AddressType = enum.auto()


@enum.unique
class AdapterFilterBT(AutoNameEnum):
    """
    Bluetooth discovery filter parameter names
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/adapter-api.txt#n48
    """
    UUIDs = enum.auto()
    RSSI = enum.auto()
    Pathloss = enum.auto()
    Transport = enum.auto()


@enum.unique
class AgentCapabilityBT(AutoNameEnum):
    """
    Bluetooth agent capability names
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt#n33
    """
    DisplayOnly = enum.auto()
    DisplayYesNo = enum.auto()
    KeyboardOnly = enum.auto()
    NoInputNoOutput = enum.auto()
    KeyboardDisplay = enum.auto()  # default


@enum.unique
class ProfileOptionBT(AutoNameEnum):
    """
    Bluetooth profile option names
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt#n24
    """
    Name = enum.auto()
    Service = enum.auto()
    Role = enum.auto()
    Channel = enum.auto()
    PSM = enum.auto()
    RequireAuthentication = enum.auto()
    RequireAuthorization = enum.auto()
    AutoConnect = enum.auto()
    ServiceRecord = enum.auto()
    Version = enum.auto()
    Features = enum.auto()


@enum.unique
class ProfileRoleBT(AutoNameEnum):
    """
    Bluetooth profile role names
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt#n36
    """
    cluster = enum.auto()
    private = enum.auto()
