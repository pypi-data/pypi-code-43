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
from datetime import datetime as dt
from typing import Optional
from typing import Type

from dateutil import parser

from .utils import format_timestamp
from .utils import get_aware_utc_now


class EiReport:
    """Model object for a report."""

    __tablename__ = "EiReport"

    __slots__ = (
        "iso_start_time",
        "iso_end_time",
        "duration",
        "iso_last_report",
        "name",
        "interval_secs",
        "granularity_secs",
        "telemetry_parameters",
        "created_on",
        "request_id",
        "report_request_id",
        "report_specifier_id",
        "status",
    )

    def __init__(
        self,
        request_id,
        report_request_id,
        report_specifier_id,
        granularity_secs=None,
        interval_secs=None,
        iso_start_time=None,
        iso_end_time=None,
        duration=None,
    ):
        self.iso_start_time: str = iso_start_time or ""  # ISO 8601 timestamp in UTC
        self.iso_end_time: str = iso_end_time or ""  # ISO 8601 timestamp in UTC
        self.duration: str = duration or ""  # ISO 8601 duration
        self.iso_last_report: str = ""  # ISO 8601 timestamp in UTC
        self.name: str = ""
        self.interval_secs: Optional[int] = interval_secs
        self.granularity_secs: Optional[int] = granularity_secs
        self.telemetry_parameters: str = ""
        self.created_on: Type(dt) = get_aware_utc_now()
        self.request_id: str = request_id
        self.report_request_id: str = report_request_id
        self.report_specifier_id: str = report_specifier_id
        self.status: str = "inactive"
        self.last_report: Type(dt) = get_aware_utc_now()

    def __str__(self):
        """Format the instance as a string suitable for trace display."""
        my_str = "{}: ".format(self.__class__.__name__)
        my_str += "report_request_id:{}; ".format(self.report_request_id)
        my_str += "report_specifier_id:{}; ".format(self.report_specifier_id)
        my_str += "start_time:{}; ".format(self.start_time)
        my_str += "end_time:{}; ".format(self.end_time)
        my_str += "status:{}; ".format(self.status)
        return my_str

    @property
    def start_time(self):
        return parser.parse(self.iso_start_time) if self.iso_start_time else None

    @property
    def end_time(self):
        return parser.parse(self.iso_end_time) if self.iso_end_time else None

    @property
    def last_report(self):
        return parser.parse(self.iso_last_report) if self.iso_last_report else None

    @start_time.setter
    def start_time(self, t):
        self.iso_start_time = format_timestamp(t) if t else None

    @end_time.setter
    def end_time(self, t):
        self.iso_end_time = format_timestamp(t) if t else None

    @last_report.setter
    def last_report(self, t):
        self.iso_last_report = format_timestamp(t) if t else None

    def is_active_or_pending(self):
        return self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELED]

    def as_json_compatible_object(self):
        """Format the object as JSON that will be returned in response to an RPC, or sent in a pub/sub."""
        return {attname: getattr(self, attname) for attname in self.__slots__}

    def copy_from_report(self, another_report):
        """(Selectively) Copy the contents of another_report to this one."""
        self.request_id = another_report.request_id
        self.report_request_id = another_report.report_request_id
        self.report_specifier_id = another_report.report_specifier_id
        self.start_time = another_report.start_time
        self.end_time = another_report.end_time
        self.duration = another_report.duration
        self.granularity_secs = another_report.granularity_secs
        # Do not copy created_on from another_report
        # Do not copy status from another_report
        # Do not copy last_report from another_report
        self.name = another_report.name
        self.interval_secs = another_report.interval_secs
        self.telemetry_parameters = another_report.telemetry_parameters


class EiTelemetryValues:
    """Model object for telemetry values."""

    __tablename__ = "EiTelemetryValues"

    __slots__ = (
        "created_on",
        "report_specifier_id",
        "iso_start_time",
        "iso_end_time",
        "values",
    )

    def __init__(
        self, report_specifier_id=None, start_time=None, end_time=None, values=None
    ):
        self.created_on: Type(dt) = get_aware_utc_now()
        self.report_specifier_id: str = report_specifier_id
        self.start_time: str = start_time
        self.end_time: str = end_time
        self.values: dict = values

    def __str__(self):
        """Format the instance as a string suitable for trace display."""
        my_str = "{}: ".format(self.__class__.__name__)
        my_str += "created_on:{}; ".format(self.created_on)
        my_str += "report_request_id:{}; ".format(self.report_request_id)
        my_str += "start_time:{} ".format(self.start_time)
        my_str += "end_time:{} ".format(self.end_time)
        my_str += "values:{} ".format(json.dumps(self.values))
        return my_str

    @property
    def start_time(self):
        return parser.parse(self.iso_start_time) if self.iso_start_time else None

    @property
    def end_time(self):
        return parser.parse(self.iso_end_time) if self.iso_end_time else None

    @start_time.setter
    def start_time(self, t):
        self.iso_start_time = format_timestamp(t) if t else None

    @end_time.setter
    def end_time(self, t):
        self.iso_end_time = format_timestamp(t) if t else None

    @classmethod
    def sample_values(cls):
        """Return a sample set of telemetry values for debugging purposes."""
        telemetry_values = cls()
        telemetry_values.report_specifier_id = "123"
        telemetry_values.values = {"asdasd": 123123}
        return telemetry_values

    def as_json_compatible_object(self):
        """Format the object as JSON that will be returned in response to an RPC, or sent in a pub/sub."""
        return {attname: getattr(self, attname) for attname in self.attribute_names}

    def get_duration(self):
        return self.end_time - self.start_time
