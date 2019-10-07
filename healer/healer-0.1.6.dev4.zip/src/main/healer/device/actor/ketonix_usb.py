"""
Device actor for
Breath Ketone Analyzer
https://www.ketonix.com/webshop/ketonix-usb-no-battery-2018
"""

from __future__ import annotations

import enum
import logging
import textwrap
import time
from typing import Any

from healer.device.actor.arkon import DeviceActor
from healer.device.record import RecordName
from healer.device.record import RecordSupport
from healer.device.usb.ketonix_usb import DeviceKetonixUSB
from healer.device.usb.ketonix_usb import KetonixPacket
from healer.device.usb.ketonix_usb import RecordKetonixUSB
from healer.support.actor.proper import proper_receive_type
from healer.support.hronos import DateTime
from healer.support.state_machine import EventEnum
from healer.support.state_machine import StateEnum
from healer.support.stream.base import Stream
from healer.support.typing import override

logger = logging.getLogger(__name__)


@enum.unique
class Command(enum.Enum):
    STATE = enum.auto()


@enum.unique
class Event(EventEnum):

    START = enum.auto()  # device start request
    STOP = enum.auto()  # device stop request

    HEATER_ON = enum.auto()  # heater is 100%
    HEATER_OFF = enum.auto()  # heater is not 100%

    SENSOR_INC = enum.auto()  # detected sensor increase
    SENSOR_DEC = enum.auto()  # detected sensor decrease
    SENSOR_FLAT = enum.auto()  # detected sensor flatline

    SESSION_READY = enum.auto()  # session sensor pattern matched
    SESSION_RELEASE = enum.auto()  # session sensor burn off complete
    SESSION_TIMEOUT = enum.auto()  # session failed to complete in time


@enum.unique
class State(StateEnum):

    STARTED = enum.auto()
    STOPPED = enum.auto()

    SESSION_ACTIVE = enum.auto()
    SESSION_COMPLETE = enum.auto()


class ActorKetonixUSB(DeviceActor):

    MIN = 0  # device color min
    MAX = 2048  # device color max

    device_class = DeviceKetonixUSB
    device:DeviceKetonixUSB

    display_state:str = ""  # desktop notification
    display_stamp:DateTime = DateTime.now()  # desktop notification

    session_start:float  # session duration
    session_finish:float  # session duration

    def __init__(self, device:DeviceKetonixUSB, **kwargs):
        self.setup_stream()  # FIXME
        super().__init__(device=device, state=State.STOPPED, **kwargs)

    def setup_stream(self) -> None:
        "congigure event streams"

        # produce packets periodically
        self.packet_flow = Stream.ticker(fun=self.device_query, period=1000)
        self.record_flow = self.packet_flow.record(fun=self.packet_record , size=512)

        # expose latest device packet
        self.packet_unit = self.packet_flow.expose()

        # track sensor level
        self.sensor_flow = self.packet_flow.base_map(fun=self.packet_sensor)
        self.sensor_min = self.sensor_flow.calc_min(use_run=True)
        self.sensor_max = self.sensor_flow.calc_max(use_run=True)

        # track heater level
        self.heater_flow = self.packet_flow.calc_avg(fun=self.packet_heater, size=3)
        self.heater_detect = self.heater_flow.trig_delta(value=100, delta=2)
        self.heater_signal = self.heater_detect.base_map(fun=self.heater_eventer)

        # track sensor direction
        self.motion_detect = self.sensor_flow.trig_trend(size=5, delta=1)
        self.motion_signal = self.motion_detect.base_map(fun=self.motion_eventer)

        # track session completion
        self.session_change = self.sensor_max.trig_change()
        self.session_detect = self.session_change.constant(timeout=20 * 1000, use_run=True)
        self.session_signal = self.session_detect.base_map(fun=self.session_eventer)

        # update desktop notification
        self.display_flow = self.packet_flow.target(fun=self.display_update)

    def packet_device_id(self, packet: KetonixPacket) -> int:
        "extract device id"
        return packet.device_id

    def packet_heater(self, packet: KetonixPacket) -> int:
        "extract heater value"
        return packet.heater

    def packet_sensor(self, packet: KetonixPacket) -> int:
        "extract sensor value"
        return packet.sensor

    def packet_record(self, packet: KetonixPacket) -> RecordKetonixUSB.Result:
        "extract persisted record"
        return RecordKetonixUSB.Result(
            stamp=DateTime.now(),
            sensor=packet.sensor,
        )

    @override
    def display_title(self) -> str:
        "extract device title"
        title = super().display_title()
        device_id = self.packet_unit.apply(self.packet_device_id)
        if device_id:
            title = f"{title} (id={device_id})"
        return title

    @override
    def on_start(self) -> None:
        self.machine_fire_event(Event.START)

    @override
    def on_stop(self) -> None:
        self.invoke_device_terminate()

    @proper_receive_type
    def on_command(self, message:Command) -> Any:
        if message == Command.STATE:
            return self.machine_state

    @proper_receive_type
    def on_event(self, message:Event) -> Any:
        return self.machine_fire_event(message)

    def device_setup(self):
        "configure device profile"
        self.device.mode_continous()
        self.device.update_data(
            # ignore sensor adjust
            calibration=0, correction=0,
            # disable color status
            level_grn=self.MAX, level_yel=self.MAX, level_red=self.MAX,
        )

    def device_query(self) -> KetonixPacket:
        "produce periodic device reading"
        logger.trace(f"@ {self}")
        packet = self.device.read_data()
        return packet

    def heater_eventer(self, state:bool) -> None:
        "produce sensor heater on/off events"
        logger.trace(f"@ {self}")
        if state:
            self.machine_fire_event(Event.HEATER_ON)
        else:
            self.machine_fire_event(Event.HEATER_OFF)

    def motion_eventer(self, state:Stream.Trend) -> None:
        "produce sensor increase/decrease events"
        logger.trace(f"@ {self}")
        if state == Stream.Trend.INCREASE:
            self.machine_fire_event(Event.SENSOR_INC)
        elif state == Stream.Trend.DECREASE:
            self.machine_fire_event(Event.SENSOR_DEC)
        elif state == Stream.Trend.FLATLINE:
            self.machine_fire_event(Event.SENSOR_FLAT)

    def session_eventer(self, value:float) -> None:
        "produce session complete events"
        logger.trace(f"@ {self}")
        self.machine_fire_event(Event.SESSION_READY)

    def session_output(self) -> int:
        "calculate measured value"
        minval = self.sensor_min.value
        maxval = self.sensor_max.value
        if minval is None or maxval is None:
            return None
        else:
            return maxval - minval

    def display_update(self, *_) -> None:
        "render desktop notification"

        state = self.display_state
        timer = str(DateTime.now() - self.display_stamp).split('.')[0]

        heater = self.packet_unit.apply(self.packet_heater)
        sensor = self.packet_unit.apply(self.packet_sensor)
        minval = self.sensor_min.value
        maxval = self.sensor_max.value
        output = self.session_output()

        message = textwrap.dedent(f"""
        State={state} Timer={timer} Heater={heater}%
        Sensor={sensor} Min={minval} Max={maxval} Out={output}
        """)

        self.display_notify.title = self.display_title()
        self.display_notify.message = message

    def session_persist(self):
        "persist collected data"
        timer = self.session_finish - self.session_start
        identity = self.device_identity_record()
        summary = RecordKetonixUSB.Summary(
            timer=timer,
            stamp=self.display_stamp,
            value=self.session_output(),
        )
        record_list = list(self.record_flow.buffer)
        session = RecordSupport.produce_session()
        with session:
            for index, record in enumerate(record_list, start=1):
                session.message_put(str(index), record)
            session.context_put(RecordName.device_identity, identity)
            session.context_put(RecordName.session_summary, summary)
        self.publish_cluster_session(session)

    def invoke_device_initiate(self):
        logger.debug(f"@ {self}")

        self.display_notify.open()

        self.display_state = "BOOT"
        self.display_stamp = DateTime.now()
        self.display_update()

        self.display_state = "INIT"

        self.device.start()
        self.device_setup()

        self.sensor_min.reset()
        self.sensor_max.reset()
        self.packet_flow.start()

    def invoke_device_terminate(self):
        logger.debug(f"@ {self}")
        self.machine_config_timeout()

        self.packet_flow.stop()

        self.device.stop()

        self.display_notify.close()

    def invoke_session_active(self):
        logger.debug(f"@ {self}")
        self.machine_config_timeout(Event.SESSION_TIMEOUT, 300)

        self.display_state = "BLOW"
        self.display_stamp = DateTime.now()

        self.sensor_min.start()
        self.sensor_max.start()
        self.record_flow.reset()
        self.motion_detect.reset()
        self.session_detect.start()

        self.session_start = time.time()

    def invoke_session_inactive(self):
        logger.debug(f"@ {self}")
        self.machine_config_timeout(Event.SESSION_RELEASE, 60)

        self.session_finish = time.time()

        self.display_state = "VENT"
        self.display_stamp = DateTime.now()

        self.session_persist()

    def invoke_session_timeout(self):
        logger.debug(f"@ {self}")
        self.machine_config_timeout()
        self.machine_fire_event(Event.STOP)

    def invoke_sensor_increase(self):
        logger.debug(f"@ {self}")
        self.display_state = "INCR"

    def invoke_sensor_decrease(self):
        logger.debug(f"@ {self}")
        self.display_state = "DECR"

    def invoke_sensor_flatline(self):
        logger.debug(f"@ {self}")
        self.display_state = "FLAT"

    #
    # state machine
    #

    Event.STOP.when_not(State.STOPPED).then(State.STOPPED).invoke(invoke_device_terminate)

    Event.START.when(State.STOPPED).then(State.STARTED).invoke(invoke_device_initiate)

    Event.HEATER_ON.when(State.STARTED).then(State.SESSION_ACTIVE).invoke(invoke_session_active)

    Event.SENSOR_INC.when(State.SESSION_ACTIVE).then(State.SESSION_ACTIVE).invoke(invoke_sensor_increase)
    Event.SENSOR_DEC.when(State.SESSION_ACTIVE).then(State.SESSION_ACTIVE).invoke(invoke_sensor_decrease)
    Event.SENSOR_FLAT.when(State.SESSION_ACTIVE).then(State.SESSION_ACTIVE).invoke(invoke_sensor_flatline)

    Event.SESSION_READY.when(State.SESSION_ACTIVE).then(State.SESSION_COMPLETE).invoke(invoke_session_inactive)
    Event.SESSION_TIMEOUT.when(State.SESSION_ACTIVE).then(State.SESSION_COMPLETE).invoke(invoke_session_timeout)

    Event.SESSION_RELEASE.when(State.SESSION_COMPLETE).then(State.STOPPED).invoke(invoke_device_terminate)
