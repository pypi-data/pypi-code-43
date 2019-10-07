"""
Device actor for
kernel module: dummy_hcd
"""

from __future__ import annotations

import enum
import logging
from typing import Any

from healer.device.actor.arkon import DeviceActor
from healer.device.usb.dummy_device import DeviceDummyHCD
from healer.support.state_machine import EventEnum
from healer.support.state_machine import StateEnum

logger = logging.getLogger(__name__)


@enum.unique
class Event(EventEnum):
    START = enum.auto()
    FINISH = enum.auto()


@enum.unique
class State(StateEnum):
    IDLE = enum.auto()
    WORKING = enum.auto()
    TERMINATED = enum.auto()


class ActorDummyHCD(DeviceActor):

    device_class = DeviceDummyHCD
    device:DeviceDummyHCD

    def __init__(self, device:DeviceDummyHCD, **kwargs):
        super().__init__(device=device, state=State.IDLE, **kwargs)

    def on_receive(self, message:Any) -> Any:
        return super().on_receive(message)

    def on_start(self) -> None:
        self.machine_fire_event(Event.START)

    def on_stop(self) -> None:
        self.machine_fire_event(Event.FINISH)

    def process_start(self):
        logger.info("process_start")

    def process_finish(self):
        logger.info("process_finish")

    Event.START.when(State.IDLE).then(State.WORKING).invoke(process_start)
    Event.FINISH.when(State.WORKING).then(State.TERMINATED).invoke(process_finish)
