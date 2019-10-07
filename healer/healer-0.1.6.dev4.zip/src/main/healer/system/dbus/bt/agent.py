"""
Base types for dbus bluetooth agents
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt
"""

from __future__ import annotations

import abc
from typing import Any

import dbus

from .base import BluetoothService
from .const import FaceBT
from .event import AgentAnyEventBT
from .event import AgentAuthorizeEntryEventBT
from .event import AgentContextBT
from .event import AgentPasswordRequestEventBT


class WithAgentReactor(abc.ABC):
    """
    Trait: react to bluez agent events
    """

    @abc.abstractmethod
    def react_agent_event(self, event:AgentAnyEventBT) -> str:
        "react to bluez agent events"
        "return failure with known exception type"
        "return requested parameter (pincode, passkey)"


class BluetoothAgent(BluetoothService):
    """
    Bluetooth agent: dbus auto-auth service provider

    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt

    See:
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/simple-agent
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/src/agent.h
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/src/agent.c
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/client/agent.h
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/client/agent.c
    """
    service_context:AgentContextBT
    service_reactor:WithAgentReactor

    def __init__(self,
            service_context:AgentContextBT,
            service_reactor:WithAgentReactor,
        ):
        super().__init__(service_context)
        self.service_reactor = service_reactor

    @dbus.service.method(FaceBT.AGENT, in_signature="", out_signature="")
    def Release(self) -> None:
        "not used"

    @dbus.service.method(FaceBT.AGENT, in_signature="", out_signature="")
    def Cancel(self) -> None:
        "not used"

    @dbus.service.method(FaceBT.AGENT, in_signature="o", out_signature="s")
    def RequestPinCode(self, entry_path:dbus.String) -> dbus.String:
        "https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt#n80"
        event = AgentPasswordRequestEventBT(
            entry_path=str(entry_path),
        )
        pincode:str = self.service_reactor.react_agent_event(event)
        return dbus.String(pincode)

    @dbus.service.method(FaceBT.AGENT, in_signature="os", out_signature="")
    def DisplayPinCode(self, entry_path:dbus.String, pincode:dbus.String) -> None:
        "not used"

    @dbus.service.method(FaceBT.AGENT, in_signature="o", out_signature="u")
    def RequestPasskey(self, entry_path:dbus.String) -> dbus.UInt32:
        "https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt#n115"
        event = AgentPasswordRequestEventBT(
            entry_path=str(entry_path),
        )
        passkey:str = self.service_reactor.react_agent_event(event)
        return dbus.UInt32(passkey)

    @dbus.service.method(FaceBT.AGENT, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, entry_path:dbus.String, passkey:dbus.UInt32, entered:dbus.UInt16) -> None:
        "not used"

    @dbus.service.method(FaceBT.AGENT, in_signature="ou", out_signature="")
    def RequestConfirmation(self, entry_path:dbus.String, passkey:dbus.UInt32) -> None:
        "not used"

    @dbus.service.method(FaceBT.AGENT, in_signature="o", out_signature="")
    def RequestAuthorization(self, entry_path:dbus.String) -> None:
        "allow device access"
        event = AgentAuthorizeEntryEventBT(
            entry_path=str(entry_path),
        )
        self.service_reactor.react_agent_event(event)  # fails via exception

    @dbus.service.method(FaceBT.AGENT, in_signature="os", out_signature="")
    def AuthorizeService(self, entry_path:dbus.String, service_uuid:dbus.String) -> None:
        "allow device/service access"
        event = AgentAuthorizeEntryEventBT(
            entry_path=str(entry_path),
            service_uuid=str(service_uuid),
        )
        self.service_reactor.react_agent_event(event)  # fails via exception
