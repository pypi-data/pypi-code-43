"""
Device actor for
Easy@Home CF350BT bluetooth body fat scale
https://www.manualslib.com/manual/1035854/Easy-Home-Cf350bt.html
"""

from __future__ import annotations

import enum
import itertools
import logging
from typing import Any

from healer.device.actor.arkon import DeviceActor
from healer.device.bt.easyhome_cf350bt import DeviceEasyHomeCF350BT
from healer.device.bt.easyhome_cf350bt import PacketSupportCF350
from healer.device.bt.easyhome_cf350bt import RecordCF350BT
from healer.device.bt.easyhome_cf350bt import ResponsePacketCF350
from healer.device.record import RecordName
from healer.device.record import RecordSupport
from healer.support.actor.proper import proper_receive_type
from healer.support.state_machine import EventEnum
from healer.support.state_machine import StateEnum
from healer.support.typing import override
from healer.support.typing import unused
from healer.system.dbus.bt.channel import WithBluetoothSerialChannel
from healer.system.dbus.bt.const import DevicePropertyBT
from healer.system.dbus.bt.event import ProfileConnectEventBT
from healer.system.dbus.bt.event import ProfileDisconnectEventBT
from healer.system.dbus.bt.event import PropertyChangeEventBT

logger = logging.getLogger(__name__)


@enum.unique
class Command(enum.Enum):  # TODO
    hello = enum.auto()


@enum.unique
class Event(EventEnum):

    STOP = enum.auto()
    START = enum.auto()

    TIMEOUT = enum.auto()

    RESPONSE = enum.auto()

    CONNECT = enum.auto()
    DISCONNECT = enum.auto()


@enum.unique
class State(StateEnum):

    FAILED = enum.auto()  # TODO

    STARTED = enum.auto()  # received initiate command
    STOPPED = enum.auto()  # received terminate command

    REQUESTED = enum.auto()  # sent device request
    RESPONDED = enum.auto()  # received device response

    PERSISTED = enum.auto()  # persisted session data


class ActorEasyHomeCF350BT(WithBluetoothSerialChannel, DeviceActor):

    device_class = DeviceEasyHomeCF350BT
    device:DeviceEasyHomeCF350BT

    packet_request:object = None
    packet_response:object = None

    def __init__(self, device:DeviceEasyHomeCF350BT, **kwargs):
        super().__init__(device=device, state=State.STOPPED, **kwargs)
        self.session_reset()

    @override
    def display_title(self) -> str:
        title = super().display_title()
        device_id = self.device.device_address()
        if device_id:
            title = f"{title} (id={device_id})"
        return title

    @override
    def on_start(self) -> None:
        pass

    @override
    def on_stop(self) -> None:
        pass

    @proper_receive_type
    def on_command(self, message:Command) -> Any:
        pass

    @proper_receive_type
    def on_event(self, message:Event) -> Any:
        return self.machine_fire_event(message)

    @proper_receive_type
    def on_profile_connect(self, message:ProfileConnectEventBT) -> Any:
        "initiate serial transfer after device connect"
        self.serial_channel_connect(message.file_desc)
        self.tell(Event.CONNECT)

    @proper_receive_type
    def on_profile_disconnect(self, message:ProfileDisconnectEventBT) -> Any:
        "terminate serial transfer after device disconnect"
        unused(message)
        self.serial_channel_disconnect()
        self.tell(Event.DISCONNECT)

    @proper_receive_type
    def on_property_change(self, message:PropertyChangeEventBT) -> Any:
        "detect when device is present"
        if DevicePropertyBT.RSSI in message.changed_dict:
            self.tell(Event.START)
        elif DevicePropertyBT.TxPower in message.changed_dict:
            self.tell(Event.START)

    @override
    def serial_react_read(self, buffer:bytes) -> None:
        "process incoming device packets"
        logger.debug(f"@ {self}")
#         logger.debug(f"serial_react_read {buffer}")
#         for idx in range(16):
#             val = format(buffer[idx], '02x')
#             print(f"{idx} : {val}")
        if len(buffer) == ResponsePacketCF350.packet_size:
            self.packet_response = PacketSupportCF350.response_packet(buffer)
            self.tell(Event.RESPONSE)  # confirm response received
        else:
            logger.warning(f"wrong buffer: {buffer} @ {self}")
            self.tell(Event.STOP)

    def session_reset(self):
        "remove session packets"
        self.packet_request = None
        self.packet_response = None

    def session_persist(self) -> None:
        "persist collected data"
        logger.info(f"@ {self.packet_request} {self.packet_response}")

        has_valid_session = self.packet_request and self.packet_response
        if not has_valid_session:
            return

        identity = self.device_identity_record()
        summary = RecordCF350BT.produce_summary(self.packet_response)
        buffer_request = RecordCF350BT.produce_buffer(self.packet_request)
        buffer_response = RecordCF350BT.produce_buffer(self.packet_response)

        record_index = itertools.count()
        next(record_index)

        session = RecordSupport.produce_session()

        with session:
            session.message_put(str(next(record_index)), buffer_request)
            session.message_put(str(next(record_index)), buffer_response)
            session.context_put(RecordName.device_identity, identity)
            session.context_put(RecordName.session_summary, summary)

        self.publish_cluster_session(session)

        self.session_reset()

    def invoke_connect(self):
        "react to device detection"
        "activate serial connection"
        logger.debug(f"@ {self}")
        self.machine_config_timeout(Event.TIMEOUT, 20)

        self.display_notify.open()
        self.display_notify.message = "CONNECT"

        self.device.issue_connect()

    def invoke_request(self):
        "react to device connect"
        "issue device query request"
        logger.debug(f"@ {self}")
        self.machine_config_timeout(Event.TIMEOUT, 20)
        self.display_notify.message = "REQUEST"
        self.packet_request = PacketSupportCF350.request_packet()
        self.serial_issue_write(self.packet_request.buffer)

    def invoke_disconnect(self):
        "react to device query response"
        "deactivate serial connection"
        logger.debug(f"@ {self}")
        self.machine_config_timeout(Event.TIMEOUT, 7)
        self.display_notify.message = "DISCONNECT"
        self.device.issue_disconnect()

    def invoke_persist(self):
        "process device response packet"
        "use sleep window to guard against post-session re-start"
        logger.debug(f"@ {self}")
        self.machine_config_timeout(Event.TIMEOUT, 7)
        self.display_notify.message = "PERSIST"
        self.session_persist()

    def invoke_terminate(self):
        "release device resource"
        "release channel resouces"
        logger.debug(f"@ {self}")
        self.machine_config_timeout()
        self.display_notify.message = "TERMINATE"
        self.device.issue_disconnect()
        self.serial_channel_disconnect()
        self.session_reset()
        self.display_notify.close()

    #
    # state machine
    #

    Event.STOP.when_not(State.STOPPED).then(State.STOPPED).invoke(invoke_terminate)
    Event.TIMEOUT.when_not(State.STOPPED).then(State.STOPPED).invoke(invoke_terminate)

    Event.START.when(State.STOPPED).then(State.STARTED).invoke(invoke_connect)
    Event.CONNECT.when(State.STARTED).then(State.REQUESTED).invoke(invoke_request)
    Event.RESPONSE.when(State.REQUESTED).then(State.RESPONDED).invoke(invoke_disconnect)
    Event.DISCONNECT.when(State.RESPONDED).then(State.PERSISTED).invoke(invoke_persist)
