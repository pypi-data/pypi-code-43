"""
Base types for device actor
"""

from __future__ import annotations

import enum
import functools
import logging
from typing import Any
from typing import List
from typing import Mapping
from typing import Type

from healer.cluster.bus import BusTopic
from healer.cluster.bus import EventBus
from healer.cluster.talk import DeviceTalk
from healer.device.arkon import DeviceBase
from healer.device.record import DeviceIdentity
from healer.persist.session import PersistSession
from healer.persist.session import SessionSupport
from healer.persist.session import SessionType
from healer.support.actor.proper import ProperActor
from healer.support.actor.proper import ProperRef
from healer.support.actor.proper import ProperRegistry
from healer.support.actor.proper import proper_receive_type
from healer.support.state_machine import MachineBase
from healer.system.notify import NotifyUnit

logger = logging.getLogger(__name__)


@enum.unique
class Command(enum.Enum):
    DEVICE = enum.auto()  # query device from actor


class DeviceActor(
        MachineBase,
        ProperActor,
    ):
    """
    actor managing a device driver
    """

    device_class:Type[DeviceBase] = DeviceBase
    device:DeviceBase

    display_notify:NotifyUnit  # desktop notification

    @classmethod
    def __init_subclass__(cls, **kwargs):
        "register available device actors"
        super().__init_subclass__(**kwargs)
        DeviceActorSupport.register_actor(cls)

    def __init__(self, device:DeviceBase, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(device, self.device_class), f"wrong device: {device}"
        self.device = device
        self.display_notify = NotifyUnit(
            unit_title=self.display_title(),
            unit_message="BOOT",
        )

    def display_title(self) -> str:
        "render desktop device title"
        return self.device_class.__name__

    def device_identity_record(self) -> DeviceIdentity:
        "produce identity record"
        return DeviceIdentity(
            device_identity=self.device.device_identity(),
            device_description=self.device.device_description(),
        )

    @proper_receive_type
    def on_receive_device_command(self, message:Command) -> Any:
        "respond to query commands"
        if message == Command.DEVICE:
            return self.device

    def publish_cluster_session(self, session:PersistSession) -> None:
        "publish device record session to the cluster"
        SessionSupport.move_to_cluster(session)
        topic = BusTopic.device_actor_session
        message = DeviceTalk.SessionCreate(
            session_type=SessionType.cluster, session_identity=session.session_identity,
        )
        EventBus.publish_message(topic, message)


class DeviceActorSupport:
    """
    bind device actors to device drivers
    """

    actor_class_list = list()

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def actor_mapper() -> Mapping[Type[DeviceBase], Type[DeviceActor]]:
        actor_class_list = DeviceActorSupport.actor_class_list
        device_mapping = map(lambda class_type: (class_type.device_class, class_type), actor_class_list)
        return dict(device_mapping)

    @staticmethod
    def register_actor(actor_class:Type[DeviceActor]) -> None:
        "register available derived actors"
        assert actor_class not in DeviceActorSupport.actor_class_list, f"need unique: {actor_class}"
        DeviceActorSupport.actor_class_list.append(actor_class)

    @staticmethod
    def produce_actor(device:DeviceBase) -> ProperRef:
        "create actor managing the device"
        actor_mapper = DeviceActorSupport.actor_mapper()
        device_class = type(device)
        actor_class = actor_mapper[device_class]
        actor_ref = actor_class.start(device=device)
        return actor_ref

    @staticmethod
    def terminate_actor(device:DeviceBase) -> None:
        "delete actor managing the device"
        actor_ref_list = ProperRegistry.find_by_class(DeviceActor)
        for actor_ref in actor_ref_list:
            actor_device = actor_ref.ask(Command.DEVICE)
            if actor_device == device:
                actor_ref.stop()
                return
        logger.error(f"no actor for device: {device}")
