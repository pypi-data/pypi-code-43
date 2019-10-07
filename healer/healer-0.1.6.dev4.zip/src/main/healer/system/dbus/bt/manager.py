"""
Base types for dbus bluetooth operations
"""

from __future__ import annotations

import logging
from types import FunctionType
from typing import Any
from typing import Mapping

import dbus

from healer.support.typing import cached_method
from healer.support.typing import override
from healer.system.dbus.arkon import ManagerDBUS
from healer.system.dbus.arkon import ObjectManagerDBUS

from .agent import BluetoothAgent
from .agent import WithAgentReactor
from .const import FaceBT
from .const import PathBT
from .event import AgentAnyEventBT
from .event import AgentContextBT
from .event import ProfileAnyEventBT
from .event import ProfileContextBT
from .profile import BluetoothProfile
from .profile import WithProfileReactor

logger = logging.getLogger(__name__)


class WithAgentManager(WithAgentReactor, ManagerDBUS):
    """
    Trait: bluetooth user agent manager

    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt
    """

    bluetooth_agent:BluetoothAgent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bluetooth_agent = None

    def agent_manager(self) -> dbus.Interface:
        root_obj = self.proxy_object(PathBT.ORG_BLUES)
        return dbus.Interface(root_obj, FaceBT.AGENT_MANAGER)

    def agent_register(self, agent_context:AgentContextBT) -> None:
        if not self.has_bus_name():
            logger.warning(f"no bus_name: {self.bus_name}")
            return

        if self.bluetooth_agent is not None:
            logger.warning(f"agent present: {self.bus_name}")
            return
        logger.debug(f"agent context: {agent_context}")
        agent_instance = BluetoothAgent(agent_context, self)
        agent_manager = self.agent_manager()
        agent_manager.RegisterAgent(
            agent_context.service_path,
            agent_context.capability,
        )
        if agent_context.request_default:
            agent_manager.RequestDefaultAgent(
                agent_context.service_path,
            )
        self.bluetooth_agent = agent_instance

    def agent_unregister(self, agent_context:AgentContextBT) -> None:
        if not self.has_bus_name():
            logger.warning(f"no bus_name: {self.bus_name}")
            return
        if self.bluetooth_agent is None:
            logger.warning(f"agent missing: {self.bus_name}")
            return
        logger.debug(f"agent context: {agent_context}")
        agent_manager = self.agent_manager()
        agent_manager.UnregisterAgent(
            agent_context.service_path,
        )
        self.bluetooth_agent.terminate()
        self.bluetooth_agent = None

    def with_agent_scope(self, agent_context:AgentContextBT, scope_function:FunctionType) -> Any:
        try:
            self.agent_register(agent_context)
            return scope_function()
        finally:
            self.agent_unregister(agent_context)

    def react_agent_event(self, event:AgentAnyEventBT) -> None:
        logger.debug(f"event: {event}")


class WithProfileManager(WithProfileReactor, ManagerDBUS):
    """
    Trait: bluetooth channel profile manager

    https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt
    """

    # track profile registration
    bluetooth_profile_map:Mapping[ProfileContextBT, BluetoothProfile]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bluetooth_profile_map = dict()

    def profile_manager(self) -> dbus.Interface:
        root_obj = self.proxy_object(PathBT.ORG_BLUES)
        return dbus.Interface(root_obj, FaceBT.PROFILE_MANAGER)

    def profile_register(self, profile_context:ProfileContextBT) -> None:
        if not self.has_bus_name():
            logger.warning(f"no bus_name: {self.bus_name}")
            return
        if profile_context in self.bluetooth_profile_map:
            logger.warning(f"profile present: {profile_context}")
            return
        logger.debug(f"profile context: {profile_context}")
        profile_instance = BluetoothProfile(profile_context, self)
        profile_manager = self.profile_manager()
        profile_manager.RegisterProfile(
            profile_context.service_path,
            profile_context.service_uuid,
            profile_context.option_dict,
        )
        self.bluetooth_profile_map[profile_context] = profile_instance

    def profile_unregister(self, profile_context:ProfileContextBT) -> None:
        if not self.has_bus_name():
            logger.warning(f"no bus_name: {self.bus_name}")
            return
        profile_instance = self.bluetooth_profile_map.pop(profile_context, None)
        if not profile_instance:
            logger.warning(f"profile missing: {profile_context}")
            return
        logger.debug(f"profile context: {profile_context}")
        profile_manager = self.profile_manager()
        profile_manager.UnregisterProfile(
            profile_context.service_path,
        )
        profile_instance.terminate()

    def react_profile_event(self, event:ProfileAnyEventBT) -> None:
        logger.debug(f"bt profile {event}")


class BluetoothManager(WithAgentManager, WithProfileManager, ObjectManagerDBUS):
    """
    Trait: bluetooth dbus controller and event observer
    """

    bus_name:str = FaceBT.ROOT  # bind to this dbus name
    object_manager_path:str = PathBT.ROOT  # bind to this object manager

    @override
    @cached_method
    def observer_start(self) -> None:
        self.process_cached_objects()  # FIXME offline startup
        super().observer_start()

    @override
    @cached_method
    def observer_stop(self) -> None:
        super().observer_stop()

    def process_cached_objects(self) -> None:
        "produce device events for dbus cached devices"
        if not self.has_bus_name():
            logger.warning(f"no bus_name: {self.bus_name}")
            return
        bucket = self.managed_objects()
        for entry_path, face_dict in bucket.items():
            if FaceBT.ADAPTER in face_dict:
                self.react_adapter_added(entry_path)
            if FaceBT.DEVICE in face_dict:
                self.react_device_added(entry_path)

    def react_faces_added(self, entry_path:str, face_dict:dbus.Dictionary) -> None:
        "deffirentiate adapters vs devices"
        if FaceBT.ADAPTER in face_dict:
            return self.react_adapter_added(entry_path)
        if FaceBT.DEVICE in face_dict:
            return self.react_device_added(entry_path)

    def react_faces_removed(self, entry_path:str, face_list:dbus.Array) -> None:
        "deffirentiate adapters vs devices"
        if FaceBT.ADAPTER in face_list:
            return self.react_adapter_removed(entry_path)
        if FaceBT.DEVICE in face_list:
            return self.react_device_removed(entry_path)

    def react_adapter_added(self, entry_path:str) -> None:
        logger.debug(f"entry_path={entry_path}")

    def react_adapter_removed(self, entry_path:str) -> None:
        logger.debug(f"entry_path={entry_path}")

    def react_device_added(self, entry_path:str) -> None:
        logger.debug(f"entry_path={entry_path}")

    def react_device_removed(self, entry_path:str) -> None:
        logger.debug(f"entry_path={entry_path}")
