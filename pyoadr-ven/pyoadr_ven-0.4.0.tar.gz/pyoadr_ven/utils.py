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
###################################################
#
# Changes for HomeAssistant are marked with **HA**
#
###################################################
"""VOLTTRON platform™ agent helper classes/functions."""
import logging
from datetime import datetime

import pytz

_LOGGER = logging.getLogger(__name__)


def format_timestamp(time_stamp):
    """Create a consistent datetime string representation based on
    ISO 8601 format.

    YYYY-MM-DDTHH:MM:SS.mmmmmm for unaware datetime objects.
    YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM for aware datetime objects

    :param time_stamp: value to convert
    :type time_stamp: datetime
    :returns: datetime in string format
    :rtype: str
    """

    time_str = time_stamp.strftime("%Y-%m-%dT%H:%M:%S.%f")

    if time_stamp.tzinfo is not None:
        sign = "+"
        td = time_stamp.tzinfo.utcoffset(time_stamp)
        if td.days < 0:
            sign = "-"
            td = -td

        seconds = td.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        time_str += "{sign}{HH:02}:{MM:02}".format(sign=sign, HH=hours, MM=minutes)

    return time_str


def get_aware_utc_now():
    """Create a timezone aware UTC datetime object from the system time.

    :returns: an aware UTC datetime object
    :rtype: datetime
    """
    utcnow = datetime.utcnow()
    utcnow = pytz.UTC.localize(utcnow)
    return utcnow
