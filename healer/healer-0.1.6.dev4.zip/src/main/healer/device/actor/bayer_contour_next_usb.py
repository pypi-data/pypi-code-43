"""
Device actor for
Bayer Contour Next USB
Blood Glucose Monitoring System
"""

from __future__ import annotations

import enum
import itertools
import logging
from typing import Any

from healer.device.actor.arkon import DeviceActor
from healer.device.protocol.ASTM_E1381 import FrameE1381
from healer.device.record import RecordName
from healer.device.record import RecordSupport
from healer.device.usb.bayer_contour_next_usb import DeviceContourNextUSB
from healer.device.usb.bayer_contour_next_usb import RecordCN
from healer.device.usb.bayer_contour_next_usb import RecordSupportCN
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


class ActorBayerContourNextUSB(DeviceActor):

    device_class = DeviceContourNextUSB
    device:DeviceContourNextUSB

    def __init__(self, device:DeviceContourNextUSB, **kwargs):
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
        "update device internal clock"
        self.display_notify.message = "CLOCK"
        instant = DateTime.now()
        clock_past = self.device.read_clock()
        logger.debug(f"clock_past: {clock_past}")
        self.device.write_clock(instant)
        clock_next = self.device.read_clock()
        logger.debug(f"clock_next: {clock_next}")

    def process_fetch(self) -> Any:
        "persist device session records"
        self.display_notify.message = f"FETCH"

        record_index = itertools.count()
        next(record_index)

        session = RecordSupport.produce_session()

        header:RecordCN.Header = None
        patient:RecordCN.Patient = None
        trailer:RecordCN.Trailer = None

        def react_frame(frame:FrameE1381) -> None:
            "collect device records into session"
            nonlocal header, patient, trailer
            record = RecordSupportCN.parse_frame_data(frame.data())
            logger.debug(f"record: {record}")
            if isinstance(record, RecordCN.Result):
                index = str(next(record_index))
                session.message_put(index, record)
            elif isinstance(record, RecordCN.Header):
                header = record
                self.display_notify.message = f"FETCH records={header.record_count}"
            elif isinstance(record, RecordCN.Patient):
                patient = record
            elif isinstance(record, RecordCN.Trailer):
                trailer = record
            else:
                logger.warning(f"wrong record: {record}")

        with session:
            self.device.read_frame_stream(react_frame)
            identity = self.device_identity_record()
            summary = RecordCN.Summary(
                header=header,
                patient=patient,
                trailer=trailer,
            )
            session.context_put(RecordName.device_identity, identity)
            session.context_put(RecordName.session_summary, summary)

        self.publish_cluster_session(session)

    def invoke_initiate(self) -> Any:
        "start device and await device initialization"
        self.machine_config_timeout(Event.DEVICE_ON, 5)
        self.display_notify.open()
        self.display_notify.message = "BOOT"
        self.device.start()
        self.display_notify.title = self.display_title()
        self.display_notify.message = "INIT"

    def invoke_terminate(self) -> Any:
        "cleanup device connection session"
        self.machine_config_timeout()
        self.display_notify.message = "DONE"
        self.device.stop()
        self.display_notify.close()

    def invoke_process(self) -> Any:
        "update clock and fetch stored device messages"
        self.machine_config_timeout(Event.DEVICE_OFF, 1)
        self.display_notify.message = "WORK"
        self.process_clock()
        self.process_fetch()
        self.device.stop()

    #
    # state machine
    #

    Event.STOP.when_not(State.STOPPED).then(State.STOPPED).invoke(invoke_terminate)
    Event.TIMEOUT.when_not(State.STOPPED).then(State.STOPPED).invoke(invoke_terminate)

    Event.START.when(State.STOPPED).then(State.STARTED).invoke(invoke_initiate)
    Event.DEVICE_ON.when(State.STARTED).then(State.PROCESSED).invoke(invoke_process)
    Event.DEVICE_OFF.when(State.PROCESSED).then(State.STOPPED).invoke(invoke_terminate)
