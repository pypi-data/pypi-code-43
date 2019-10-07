"""
Device actor for
Wrist Pulse Oximeter
https://www.concordhealthsupply.com/Wrist-Oximeter-p/75006.htm
"""

from __future__ import annotations

import enum
import itertools
import logging
from typing import Any

from healer.device.actor.arkon import DeviceActor
from healer.device.record import RecordName
from healer.device.record import RecordSupport
from healer.device.usb.innovo_cms50f import DeviceInnovoCMS50F
from healer.device.usb.innovo_cms50f import RecordCMS
from healer.support.actor.proper import proper_receive_type
from healer.support.hronos import DateTime
from healer.support.state_machine import EventEnum
from healer.support.state_machine import StateEnum
from healer.support.typing import override

logger = logging.getLogger(__name__)


@enum.unique
class Command(enum.Enum):
    hello = enum.auto()


@enum.unique
class Event(EventEnum):

    START = enum.auto()
    STOP = enum.auto()

    DEVICE_ON = enum.auto()
    DEVICE_OFF = enum.auto()

    TIMEOUT = enum.auto()


@enum.unique
class State(StateEnum):
    STARTED = enum.auto()
    STOPPED = enum.auto()
    PROCESSED = enum.auto()


class ActorInnovoCMS50F(DeviceActor):

    device_class = DeviceInnovoCMS50F
    device:DeviceInnovoCMS50F

    def __init__(self, device:DeviceInnovoCMS50F, **kwargs):
        super().__init__(device=device, state=State.STOPPED, **kwargs)

    @override
    def display_title(self) -> str:
        title = super().display_title()
        if self.device.has_run():
            device_id = self.device.query_device_id()
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
        self.machine_fire_event(Event.STOP)

    def process_clock(self) -> Any:
        "update device internal clock"
        self.display_notify.message = "CLOCK"
        instant = DateTime.now()
        self.device.write_device_clock(instant)
        logger.info(f"instant: {instant}")

    def process_fetch(self) -> Any:
        "persist device session records"
        self.display_notify.message = "FETCH"
        user_count = self.device.query_user_count()
        for user in range(user_count):
            segment_count = self.device.query_segment_count(user=user)
            for segment in range(segment_count):
                date_time = self.device.query_segment_stamp(user=user, segment=segment)
                record_count = self.device.query_segment_size(user=user, segment=segment)
                logger.info(
                    f"user={user} segment={segment} record_count={record_count} date_time={date_time}"
                )
                self.display_notify.message = (
                    f"FETCH user={user} segment={segment} records={record_count}"
                )
                record_index = itertools.count()
                next(record_index)
                session = RecordSupport.produce_session()

                def react_record(record:RecordCMS.Result) -> None:
                    logger.debug(f"record: {record}")
                    index = str(next(record_index))
                    session.message_put(index, record)

                identity = self.device_identity_record()
                summary = RecordCMS.Summary(
                    user=user,
                    segment=segment,
                    record_count=record_count,
                    date_time=date_time,
                )
                with session:
                    self.device.visit_stored_record(
                        user=user, segment=segment, react_record=react_record,
                    )
                    session.context_put(RecordName.device_identity, identity)
                    session.context_put(RecordName.session_summary, summary)
                self.publish_cluster_session(session)

    def invoke_initiate(self):
        "start device and await device initialization"
        self.machine_config_timeout()

        self.display_notify.open()
        self.display_notify.message = "BOOT"

        self.device.start()

        if self.device.check_setup():
            self.display_notify.message = "INIT"
            self.display_notify.title = self.display_title()
            self.machine_config_timeout(Event.DEVICE_ON, 3)
        else:
            self.display_notify.message = "DOWN"
            self.machine_config_timeout(Event.TIMEOUT, 3)

    def invoke_terminate(self):
        self.machine_config_timeout()
        self.device.stop()
        self.display_notify.close()

    def invoke_process(self):
        ""
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
