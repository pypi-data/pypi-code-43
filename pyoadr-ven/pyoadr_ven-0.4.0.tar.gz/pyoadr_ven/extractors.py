# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2017, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Optional

import isodate
import lxml.etree as etree

from . import enums
from . import exceptions
from . import response_codes

_LOGGER = logging.getLogger(__name__)


"""
The basic design of an extractor or decoder is that it takes some complex value
and returns a relatively simpler, and validated, one.

The return value should be a dataclass:
https://docs.python.org/3/library/dataclasses.html
"""


# ******** oadrCreatedPartyRegistration ********


@dataclass
class CreatedPartyRegistrationData:
    vtn_id: str
    ven_id: Optional[str]
    poll_interval_secs: Optional[int]


def decode_oadr_created_party_registration(
    tree: etree.Element
) -> CreatedPartyRegistrationData:
    return CreatedPartyRegistrationData(
        vtn_id=tree.vtnID,
        ven_id=tree.venID,
        poll_interval_secs=tree.oadrRequestedOadrPollFreq,
    )


# ******** eiEvent ********


@dataclass
class EiEventData:
    event_id: str
    status: enums.EventStatus
    modification_number: int
    priority: int
    official_start: datetime
    duration: timedelta
    start_after: Optional[timedelta]
    signals: str
    test_event: bool


def _check_signals_duration_equals_event_duration(eiEvent):
    """
    Check that the sum of all signal interval durations equals the event duration.

    """
    event_duration = isodate.parse_duration(
        eiEvent.eiActivePeriod.properties.duration.duration
    )
    signals_duration = timedelta(seconds=0)

    all_durations = [
        isodate.parse_duration(interval.duration.duration)
        for signal in eiEvent.eiEventSignals.eiEventSignal
        for interval in signal.intervals.interval
    ]
    signals_duration = sum(all_durations, timedelta(seconds=0))

    if signals_duration != event_duration:
        raise exceptions.OpenADRInterfaceException(
            f"Total signal interval durations {signals_duration} != event duration {event_duration}",
            response_codes.OADR_BAD_SIGNAL,
        )


def _extract_signal(signal):
    """Extract a signal from the received eiEvent."""
    if signal.signalName.lower() != "simple":
        raise exceptions.OpenADRInterfaceException(
            "Received a non-simple event signal; not supported by this VEN.",
            response_codes.OADR_BAD_SIGNAL,
        )
    if signal.signalType.lower() != "level":
        # OADR rule 116: If signalName = simple, signalType = level.
        # Disabling this validation since the EPRI VTN server sometimes sends type "delta" for simple signals.
        # error_msg = 'Simple signalType must be level; = {}'.format(signal.signalType)
        # raise exceptions.OpenADRInterfaceException(error_msg, response_codes.OADR_BAD_SIGNAL)
        pass

    return {
        "signalID": signal.signalID,
        "currentLevel": int(signal.currentValue.payloadFloat.value)
        if signal.currentValue
        else None,
        "intervals": {
            interval.uid
            if interval.uid and interval.uid.strip()
            else str(i): {
                "uid": interval.uid
                if interval.uid and interval.uid.strip()
                else str(i),
                "duration": interval.duration.duration,
                "payloads": {
                    "level": int(payload.payloadBase.value)
                    for payload in interval.streamPayloadBase
                },
            }
            for i, interval in enumerate(signal.intervals.interval)
        },
    }


def _extract_signals(eiEvent) -> str:
    """
    Extract eiEventSignals from the received eiEvent

    :return: A JSON string of signals
    """

    if not eiEvent.eiEventSignals:
        raise exceptions.OpenADRInterfaceException(
            "At least one event signal is required.", response_codes.OADR_BAD_SIGNAL
        )
    if not eiEvent.eiEventSignals.eiEventSignal:
        raise exceptions.OpenADRInterfaceException(
            "At least one event signal is required.", response_codes.OADR_BAD_SIGNAL
        )

    _check_signals_duration_equals_event_duration(eiEvent)

    return json.dumps(
        {s.signalID: _extract_signal(s) for s in eiEvent.eiEventSignals.eiEventSignal}
    )


def decode_ei_event(eiEvent) -> EiEventData:
    # Ensure various paths exist (error early so we need to check for errors less later)

    if eiEvent.eventDescriptor is None:
        raise exceptions.BadDataError("Missing eiEvent.eventDescriptor")

    if eiEvent.eiActivePeriod is None:
        raise exceptions.BadDataError("Missing eiEvent.eiActivePeriod")

    if eiEvent.eiActivePeriod.properties is None:
        raise exceptions.BadDataError("Missing eiEvent.eiActivePeriod.properties")

    # Extractor mini-functions

    def event_id() -> str:
        event_id = eiEvent.eventDescriptor.eventID
        if event_id is None:
            raise exceptions.BadDataError("Missing eiEvent.eventDescriptor.eventID")
        return eiEvent.eventDescriptor.eventID

    def status() -> enums.EventStatus:
        """
        OADR rule 13: Status value must be a valid type, appropriate for the event's period.
        """
        event_status = eiEvent.eventDescriptor.eventStatus
        if event_status not in enums.EventStatus.list():
            raise exceptions.BadDataError(
                "Missing or invalid eventDescriptor.eventStatus"
            )
        return enums.EventStatus(event_status)

    def modification_number() -> int:
        modification_number = eiEvent.eventDescriptor.modificationNumber
        if modification_number is None:
            raise exceptions.BadDataError("Missing eventDescriptor.modificationNumber")
        return modification_number

    def priority() -> int:
        return eiEvent.eventDescriptor.priority or 0

    def official_start() -> datetime:  # was event_dtstart
        try:
            dtstart = eiEvent.eiActivePeriod.properties.dtstart.date_time
            assert dtstart is not None
            assert dtstart.tzinfo is not None
        except Exception as err:
            raise exceptions.BadDataError(
                f"Missing/Invalid properties.dtstart.date_time: {dtstart} {err}"
            )
        return dtstart.replace(tzinfo=None)

    def duration() -> timedelta:
        try:
            duration = eiEvent.eiActivePeriod.properties.duration.duration
        except AttributeError as err:
            raise exceptions.BadDataError(
                f"Missing/Invalid properties.duration.duration: {err}"
            )
        return isodate.parse_duration(duration)

    def start_after() -> timedelta:
        if not eiEvent.eiActivePeriod.properties.tolerance:
            return timedelta(seconds=0)
        if not eiEvent.eiActivePeriod.properties.tolerance.tolerate:
            return timedelta(seconds=0)
        startafter = eiEvent.eiActivePeriod.properties.tolerance.tolerate.startafter

        try:
            return isodate.parse_duration(startafter)
        except Exception as err:
            raise exceptions.BadDataError(
                f"Invalid activePeriod tolerance.tolerate.startafter: {err}"
            )

    def test_event() -> bool:
        return bool(eiEvent.eventDescriptor.testEvent)

    """
    Currently unused, but keeping here because figuring out the paths to the right
    data is a PITA.

    def created_datetime():
        return eiEvent.eventDescriptor.createdDateTime

    def vtn_comment() -> str:
        return eiEvent.eventDescriptor.vtnComment

    def notification_duration():
        notification = eiEvent.eiActivePeriod.properties.x_eiNotification
        if notification is None:
            # OADR rule 105: eiNotification is required as an element of activePeriod.
            raise exceptions.BadDataError(
                "Missing eiActivePeriod.properties.eiNotification"
            )
        return notification.duration

    def ramp_up_duration():
        return eiEvent.eiActivePeriod.properties.x_eiRampUp.duration

    def recovery_duration():
        return eiEvent.eiActivePeriod.properties.x_eiRecovery.duration
    """

    # Bring it all together now...

    return EiEventData(
        event_id=event_id(),
        status=status(),
        modification_number=modification_number(),
        priority=priority(),
        official_start=official_start(),
        duration=duration(),
        start_after=start_after(),
        signals=_extract_signals(eiEvent),
        test_event=test_event(),
    )


# ******** eiReport ********


def report_extract_specifier_id(request) -> str:
    """Extract a report's properties from oadr model objects received from the VTN as XML."""
    """Extract and return the report's reportSpecifierID."""
    report_specifier = request.reportSpecifier
    if report_specifier is None:
        raise exceptions.BadDataError("Missing oadrReportRequest.reportSpecifier")

    report_specifier_id = report_specifier.reportSpecifierID
    if report_specifier_id is None:
        raise exceptions.BadDataError(
            "Missing oadrReportRequest.reportSpecifier.reportSpecifierID"
        )

    return report_specifier_id


@dataclass
class EiReportData:
    request_id: str
    specifier_id: str
    granularity_secs: int
    interval_secs: int
    start_time: datetime
    end_time: datetime
    duration: timedelta


def decode_ei_report(eiReport, default_interval=None) -> EiReportData:
    if eiReport.reportSpecifier is None:
        raise exceptions.BadDataError("Missing oadrReportRequest.reportSpecifier")
    if eiReport.reportSpecifier.reportSpecifierID is None:
        raise exceptions.BadDataError(
            "Missing oadrReportRequest.reportSpecifier.reportSpecifierID"
        )

    if eiReport.reportRequestID is None:
        raise exceptions.BadDataError("Missing oadrReportRequest.reportRequestID")

    report_specifier = eiReport.reportSpecifier

    def interval() -> Optional[int]:
        if report_specifier.reportBackDuration is not None:
            try:
                duration = report_specifier.reportBackDuration.duration
                return int(isodate.parse_duration(duration).total_seconds())
            except Exception as err:
                raise exceptions.BadDataError(
                    f"reportBackDuration has unparsable duration: {err}"
                )
        elif default_interval:
            return default_interval
        else:
            return None

    def granularity() -> Optional[int]:
        if not report_specifier.granularity:
            return None
        try:
            granularity = isodate.parse_duration(report_specifier.granularity.duration)
        except Exception:
            raise exceptions.BadDataError(
                "Report granularity is missing or is not an ISO8601 duration"
            )

        return int(granularity.total_seconds())

    def start_time() -> datetime:
        try:
            start_time = _report_interval().properties.dtstart.date_time
            assert start_time is not None
            assert start_time.tzinfo is not None
        except Exception as err:
            error_msg = "Missing/Invalid interval properties.dtstart.date_time: {} {}".format(
                start_time, err
            )
            raise exceptions.BadDataError(error_msg)
        return start_time.replace(tzinfo=None)

    def duration() -> timedelta:
        duration = _report_interval().properties.duration
        if not duration:
            _LOGGER.debug(
                f"Missing/null report interval duration: the report will remain active indefinitely"
            )
            return None
        return isodate.parse_duration(duration.duration)

    def end_time() -> datetime:
        if not bool(duration()):
            return None
        return start_time() + duration()

    def _report_interval():
        if eiReport.reportSpecifier.reportInterval is None:
            raise exceptions.BadDataError("Missing reportInterval")
        return eiReport.reportSpecifier.reportInterval

    return EiReportData(
        request_id=eiReport.reportRequestID,
        specifier_id=eiReport.reportSpecifier.reportSpecifierID,
        granularity_secs=granularity(),
        interval_secs=interval(),
        start_time=start_time(),
        end_time=end_time(),
        duration=duration(),
    )
