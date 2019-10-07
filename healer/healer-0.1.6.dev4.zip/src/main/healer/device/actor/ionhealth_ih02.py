"""
Device actor for
ION IH02 USB WRIST BLOOD PRESSURE MONITOR
https://www.amazon.ca/IH02-WRIST-BLOOD-PRESSURE-MONITOR/dp/B0057WWZMM
"""

from __future__ import annotations

import enum
import itertools
import logging
from typing import Any

from healer.device.actor.arkon import DeviceActor
from healer.device.record import RecordName
from healer.device.record import RecordSupport
from healer.device.usb.ionhealth_ih02 import DeviceIonHealthIH02
from healer.device.usb.ionhealth_ih02 import RecordIH02
from healer.support.actor.proper import proper_receive_type
from healer.support.hronos import DateTime
from healer.support.state_machine import EventEnum
from healer.support.state_machine import StateEnum
from healer.support.typing import override

logger = logging.getLogger(__name__)


@enum.unique
class Command(enum.Enum):
    STATE = enum.auto()


@enum.unique
class Event(EventEnum):

    STOP = enum.auto()
    START = enum.auto()

    TIMEOUT = enum.auto()

    DEVICE_ON = enum.auto()
    DEVICE_OFF = enum.auto()


@enum.unique
class State(StateEnum):

    FAILED = enum.auto()
    STARTED = enum.auto()
    STOPPED = enum.auto()
    PROCESSED = enum.auto()


class ActorIonHealthIH02(DeviceActor):

    device_class = DeviceIonHealthIH02
    device:DeviceIonHealthIH02

    def __init__(self, device:DeviceIonHealthIH02, **kwargs):
        super().__init__(device=device, state=State.STOPPED, **kwargs)

    @override
    def display_title(self) -> str:
        title = super().display_title()
        if self.device.has_run():
            device_id = self.device.device_serial_number().lstrip("0")
        else:
            device_id = None
        if device_id:
            title = f"{title} (id={device_id})"
        return title

    @proper_receive_type
    def on_command(self, message:Command) -> Any:
        if message == Command.STATE:
            return self.machine_state

    @proper_receive_type
    def on_event(self, message:Event) -> Any:
        return self.machine_fire_event(message)

    @override
    def on_start(self) -> None:
        self.tell(Event.START)

    @override
    def on_stop(self) -> None:
        self.invoke_terminate()

    def process_clock(self) -> Any:
        self.display_notify.message = "CLOCK"
        instant = DateTime.now()
        response = self.device.write_device_clock(instant)
        logger.debug(f"clock: {response}")

    def process_fetch(self) -> Any:
        self.display_notify.message = "FETCH"

        storage_status = self.device.read_storage_status()
        record_count = storage_status.record_count

        if record_count == 0:
            logger.debug(f"no records")
            return

        record_index = itertools.count()
        next(record_index)

        session = RecordSupport.produce_session()

        identity = self.device_identity_record()
        summary = RecordIH02.Summary(
            record_count=record_count,
        )

        def react_record(record:RecordIH02.Result) -> None:
            logger.debug(f"record: {record}")
            index = str(next(record_index))
            session.message_put(index, record)

        with session:
            self.device.read_record_stream(react_record)
            session.context_put(RecordName.device_identity, identity)
            session.context_put(RecordName.session_summary, summary)

        self.publish_cluster_session(session)

        self.device.issue_storage_reset()

    def invoke_initiate(self) -> Any:
        self.machine_config_timeout(Event.DEVICE_ON, 5)
        self.display_notify.open()
        self.display_notify.message = "BOOT"
        self.device.start()
        self.display_notify.title = self.display_title()
        self.display_notify.message = "INIT"

    def invoke_terminate(self) -> Any:
        self.machine_config_timeout()
        self.display_notify.message = "DONE"
        self.device.stop()
        self.display_notify.close()

    def invoke_process(self) -> Any:
        self.machine_config_timeout(Event.DEVICE_OFF, 1)
        self.display_notify.message = "WORK"
        self.process_clock()
        self.process_fetch()

    #
    # state machine
    #

    Event.STOP.when_not(State.STOPPED).then(State.STOPPED).invoke(invoke_terminate)
    Event.TIMEOUT.when_not(State.STOPPED).then(State.STOPPED).invoke(invoke_terminate)

    Event.START.when(State.STOPPED).then(State.STARTED).invoke(invoke_initiate)
    Event.DEVICE_ON.when(State.STARTED).then(State.PROCESSED).invoke(invoke_process)
    Event.DEVICE_OFF.when(State.PROCESSED).then(State.STOPPED).invoke(invoke_terminate)
