"""
Bluetooth object and service events
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import List
from typing import Mapping

from healer.system.dbus.arkon import EventDBUS

from .const import AgentCapabilityBT


@dataclass(frozen=True)
class AnyServiceContextBT:
    """
    Bluetooth service descriptor base
    """
    # name space for healer bluethooth services
    service_root:str = "/healer/bluez"
    # healer service identity within the name space
    service_uuid:str = "service"

    @property
    def service_path(self):
        "Unique service location on the bus"
        return f"{self.service_root}/{self.service_uuid}".replace('-', '_')


@dataclass(frozen=True)
class PropertyChangeEventBT(EventDBUS):
    """
    Bluetooth property change event
    """
    # object interface
    entry_face:str
    # changed property map
    changed_dict:Mapping[str, Any]
    # invalidated property list
    invalid_list:List[str]


@dataclass(frozen=True)
class AgentContextBT(AnyServiceContextBT):
    """
    Bluetooth agent service descriptor
    """
    # name space for healer bluethooth agent services
    service_root:str = "/healer/bluez/agent"
    request_default:bool = field(compare=False, default=False)
    capability:AgentCapabilityBT = field(compare=False, default=AgentCapabilityBT.KeyboardDisplay)


@dataclass(frozen=True)
class AgentAnyEventBT(EventDBUS):
    """
    Bluetooth agent event base
    """


@dataclass(frozen=True)
class AgentAuthorizeEntryEventBT(AgentAnyEventBT):
    """
    Bluetooth agent device/service grant request event from:

    # allow device access
    void RequestAuthorization(object device)

    # allow device/service access
    void AuthorizeService(object device, string uuid)

    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt
    """
    service_uuid:str = None  # None means whole device


@dataclass(frozen=True)
class AgentPasswordRequestEventBT(AgentAnyEventBT):
    """
    Bluetooth agent pincode/passkey value request event from:

    # text code
    string RequestPinCode(object device)

    # numeric key
    uint32 RequestPasskey(object device)

    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt
    """


@dataclass(frozen=True)
class ProfileContextBT(AnyServiceContextBT):
    """
    Bluetooth profile service descriptor
    """
    # name space for healer bluethooth profile services
    service_root:str = "/healer/bluez/profile"
    option_dict:Mapping[str, Any] = field(compare=False, default_factory=dict)


@dataclass(frozen=True)
class ProfileAnyEventBT(EventDBUS):
    """
    Bluetooth profile event base
    """
    service_context:ProfileContextBT = field(repr=False)


@dataclass(frozen=True)
class ProfileConnectEventBT(ProfileAnyEventBT):
    """
    Bluetooth profile connect event from:
    void NewConnection(object device, fd, dict fd_properties)
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt
    """
    # fd, file descriptor
    file_desc:int
    # connection properties
    property_dict:Mapping[str, Any]


@dataclass(frozen=True)
class ProfileDisconnectEventBT(ProfileAnyEventBT):
    """
    Bluetooth profile discconnect event from:
    void RequestDisconnection(object device)
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt
    """
